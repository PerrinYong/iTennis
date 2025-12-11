"""
NTRP 网球等级评估核心计算器

专注于核心评估算法和计算逻辑。
基于多维度模糊评分机制，支持硬性上限限制。
"""

import math
from typing import Dict, List, Optional, Tuple

from data_models import (
    QuestionConfig, OptionConfig, EvaluateResult,
    NTRPConstants, get_level_label, round_to_half
)


class NTRPEvaluator:
    """NTRP 网球等级评估核心计算器"""
    
    def __init__(
        self,
        questions: List[QuestionConfig],
        suggestion_rules: Dict[str, List[Dict[str, any]]],
        config_manager,
        spread: float = 1.0,
    ) -> None:
        """
        初始化评估器
        
        Args:
            questions: 问题配置列表
            suggestion_rules: 评语规则字典
            config_manager: 配置管理器
            spread: 模糊评分的扩散参数，控制三角形隶属度函数的宽度
        """
        self.questions = questions
        self.suggestion_rules = suggestion_rules
        self.config_manager = config_manager
        self.spread = spread
        
        # 创建问题和选项的快速查找字典
        self._question_dict = {q.id: q for q in questions}
        self._option_dict: Dict[str, OptionConfig] = {}
        for q in questions:
            for opt in q.options:
                self._option_dict[opt.id] = opt
    
    def evaluate(self, answers: Dict[str, str]) -> EvaluateResult:
        """
        核心评估方法
        
        Args:
            answers: 用户答案字典，key为问题ID，value为选项ID
            
        Returns:
            评估结果
            
        Raises:
            ValueError: 答案格式错误或包含无效选项
        """
        # 1) 验证输入
        if not self._validate_answers(answers):
            raise ValueError("答案格式错误或包含无效选项")
        
        # 2) 计算支持度分布
        support, dim_scores, hard_cap = self._compute_support_distribution(answers)
        
        # 3) 计算基础等级（Anchor机制后的结果）
        base_level = self._compute_raw_level(support, hard_cap)
        
        # 4) 计算维度分数
        dimension_scores = self._compute_dimension_scores(dim_scores)
        
        # 5) 计算木桶效应统计数据
        barrel_stats = self._compute_barrel_effect(dimension_scores, base_level)
        
        # 6) 应用木桶效应调整
        final_level = barrel_stats['final_level']
        rounded_level = round_to_half(final_level)
        level_label = get_level_label(rounded_level, self.config_manager)
        
        # 5) 生成评语
        dimension_comments = self._build_dimension_comments(dimension_scores, rounded_level)
        
        # 6) 分析优势和短板
        advantages, weaknesses = self._analyze_strengths_weaknesses(dimension_scores)
        
        # 7) 生成总体评语
        summary_text = self._build_summary_text(
            rounded_level, level_label, dimension_scores, 
            dimension_comments, advantages, weaknesses
        )
        
        return EvaluateResult(
            total_level=final_level,
            rounded_level=rounded_level,
            level_label=level_label,
            dimension_scores=dimension_scores,
            dimension_comments=dimension_comments,
            advantages=advantages,
            weaknesses=weaknesses,
            summary_text=summary_text,
            support_distribution=support.copy(),
            chart_data=None,  # 将由 chart_generator 生成
            # 木桶效应统计数据
            base_level=base_level,
            dimension_mean=barrel_stats['mean'],
            dimension_variance=barrel_stats['variance'],
            dimension_min=barrel_stats['min'],
            dimension_max=barrel_stats['max'],
            balance_factor=barrel_stats['balance_factor'],
            barrel_adjusted_level=barrel_stats['barrel_adjusted'],
            comprehensive_bonus=barrel_stats['bonus']
        )
    
    def _validate_answers(self, answers: Dict[str, str]) -> bool:
        """验证答案有效性"""
        # 检查至少有一些答案
        if not answers:
            return False
        
        # 检查每个答案是否有效
        for question_id, option_id in answers.items():
            # 验证问题ID是否存在
            if question_id not in self._question_dict:
                return False
            # 验证选项ID是否有效
            if option_id not in self._option_dict:
                return False
        
        return True
    
    def _compute_support_distribution(
        self, 
        answers: Dict[str, str]
    ) -> Tuple[Dict[float, float], Dict[str, List[Tuple[float, float]]], float]:
        """
        计算支持度分布和维度分数
        
        Returns:
            (支持度分布, 维度分数累积, 硬性上限)
        """
        # 初始化支持度分布
        support: Dict[float, float] = {L: 0.0 for L in NTRPConstants.LEVELS}
        
        # 维度分数累积：{dimension: [(score, weight), ...]}
        dim_scores: Dict[str, List[Tuple[float, float]]] = {}
        
        # 硬性上限
        hard_cap = float('inf')
        
        for question_id, option_id in answers.items():
            question = self._question_dict[question_id]
            option = self._option_dict[option_id]
            
            # 更新硬性上限
            if option.hard_cap is not None:
                hard_cap = min(hard_cap, option.hard_cap)
            
            # 计算该选项对各等级的隔属度
            for level in NTRPConstants.LEVELS:
                membership = self._compute_membership_by_anchor(level, option)
                
                # 如果是locator类型，应用加成系数
                weight_factor = question.weight
                if option.anchor_type == "locator":
                    weight_factor *= NTRPConstants.LOCATOR_BOOST
                
                support[level] += membership * weight_factor
            
            # 记录维度分数
            if question.dimension not in dim_scores:
                dim_scores[question.dimension] = []
            dim_scores[question.dimension].append((option.center_level, question.weight))
        
        return support, dim_scores, hard_cap
    
    def _compute_membership(self, level: float, center: float, spread: float) -> float:
        """
        计算三角形隔属度函数
        
        Args:
            level: 目标等级
            center: 中心等级
            spread: 扩散参数
            
        Returns:
            隔属度 [0, 1]
        """
        diff = abs(level - center)
        if diff >= spread:
            return 0.0
        return 1.0 - diff / spread
    
    def _compute_membership_by_anchor(self, level: float, option: OptionConfig) -> float:
        """
        根据anchor_type计算不同类型的membership
        
        Args:
            level: 目标等级
            option: 选项配置
            
        Returns:
            隔属度 [0, 1]
        """
        anchor_type = option.anchor_type
        center = option.center_level
        
        if anchor_type == "locator":
            # 定位选项: 使用更窄的高斯分布
            sigma = NTRPConstants.LOCATOR_SIGMA
            return math.exp(-((level - center) ** 2) / (2 * sigma ** 2))
            
        elif anchor_type == "baseline":
            # 基线选项: 只给高段位贡献
            min_level = option.baseline_min_level
            if min_level is None:
                min_level = NTRPConstants.HIGH_LEVEL_THRESHOLD
            
            if level < min_level:
                return 0.0
            
            sigma = NTRPConstants.BASELINE_SIGMA
            return math.exp(-((level - min_level) ** 2) / (2 * sigma ** 2))
            
        else:  # normal
            # 普通选项: 沿用现有逻辑
            return math.exp(-((level - center) ** 2) / (2 * self.spread ** 2))
    
    def _compute_raw_level(self, support: Dict[float, float], hard_cap: float) -> float:
        """基于支持度分布计算期望等级"""
        total_support = sum(support.values())
        if total_support <= 0:
            # 没有有效答案时的fallback
            fallback = NTRPConstants.LEVELS[len(NTRPConstants.LEVELS) // 2]
            return min(fallback, hard_cap)
        
        # 计算加权平均
        expectation = sum(level * support[level] for level in NTRPConstants.LEVELS) / total_support
        return min(expectation, hard_cap)
    
    def _compute_dimension_scores(
        self, 
        dim_scores: Dict[str, List[Tuple[float, float]]]
    ) -> Dict[str, float]:
        """计算各维度的加权平均分数"""
        dimension_scores: Dict[str, float] = {}
        
        for dimension, score_weight_pairs in dim_scores.items():
            if not score_weight_pairs:
                continue
            
            total_weight = sum(weight for _, weight in score_weight_pairs)
            if total_weight > 0:
                weighted_sum = sum(score * weight for score, weight in score_weight_pairs)
                dimension_scores[dimension] = weighted_sum / total_weight
            else:
                # fallback
                dimension_scores[dimension] = sum(score for score, _ in score_weight_pairs) / len(score_weight_pairs)
        
        return dimension_scores
    
    def _build_dimension_comments(
        self,
        dimension_scores: Dict[str, float],
        total_level: float,
    ) -> Dict[str, str]:
        """为每个维度生成详细评语"""
        comments: Dict[str, str] = {}
        
        for dimension, score in dimension_scores.items():
            # 基础评语
            base_comment = self._get_base_comment(dimension, score)
            
            # 相对评语
            relative_comment = self._get_relative_comment(score, total_level)
            
            # 组合评语
            comments[dimension] = base_comment + relative_comment
        
        return comments
    
    def _get_base_comment(self, dimension: str, score: float) -> str:
        """根据维度和分数获取基础评语"""
        # 使用dimension_suggestions.json中的内容
        return self.config_manager.get_dimension_suggestion(dimension, score)
    
    def _get_relative_comment(self, dimension_score: float, total_level: float) -> str:
        """根据维度分数相对整体的差异生成评语"""
        diff = dimension_score - total_level
        
        if diff >= 0.5:
            return self.config_manager.get_relative_evaluation_text("strong_advantage")
        elif diff <= -0.5:
            return self.config_manager.get_relative_evaluation_text("weakness")
        else:
            return self.config_manager.get_relative_evaluation_text("balanced")
    
    def _analyze_strengths_weaknesses(
        self, 
        dimension_scores: Dict[str, float]
    ) -> Tuple[List[str], List[str]]:
        """分析优势和短板维度"""
        if not dimension_scores:
            return [], []
        
        # 计算平均分
        avg_score = sum(dimension_scores.values()) / len(dimension_scores)
        
        # 计算偏差
        dimension_diffs = [(dim, score - avg_score) for dim, score in dimension_scores.items()]
        dimension_diffs.sort(key=lambda x: x[1], reverse=True)
        
        # 选取优势项目（前2-3个，且偏差>=0.3）
        advantages = []
        for dim, diff in dimension_diffs:
            if diff >= 0.3 and len(advantages) < 3:
                advantages.append(dim)
        
        # 选取短板项目（后2-3个，且偏差<=-0.3）
        weaknesses = []
        for dim, diff in reversed(dimension_diffs):
            if diff <= -0.3 and len(weaknesses) < 3:
                weaknesses.append(dim)
        
        return advantages, weaknesses
    
    def _compute_barrel_effect(
        self,
        dimension_scores: Dict[str, float],
        base_level: float
    ) -> Dict[str, float]:
        """
        计算木桶效应相关统计数据和等级调整
        
        Args:
            dimension_scores: 各维度分数
            base_level: Anchor机制计算的基础等级
            
        Returns:
            包含木桶效应统计数据的字典
        """
        if not dimension_scores:
            return {
                'mean': base_level,
                'variance': 0.0,
                'min': base_level,
                'max': base_level,
                'balance_factor': 1.0,
                'barrel_adjusted': base_level,
                'bonus': 0.0,
                'final_level': base_level
            }
        
        # 1. 计算基本统计量
        scores = list(dimension_scores.values())
        n = len(scores)
        
        mean = sum(scores) / n
        variance = sum((s - mean) ** 2 for s in scores) / n
        min_score = min(scores)
        max_score = max(scores)
        
        # 2. 计算均衡度因子 B ∈ [0, 1]
        variance_low = NTRPConstants.VARIANCE_LOW
        variance_high = NTRPConstants.VARIANCE_HIGH
        
        if variance <= variance_low:
            balance_factor = 1.0
        elif variance >= variance_high:
            balance_factor = 0.0
        else:
            balance_factor = 1.0 - (variance - variance_low) / (variance_high - variance_low)
        
        balance_factor = max(0.0, min(1.0, balance_factor))
        
        # 3. 木桶效应调整
        # L_barrel = B * L_base + (1 - B) * D_min
        barrel_adjusted = balance_factor * base_level + (1 - balance_factor) * min_score
        
        # 应用最大下调限制
        max_penalty = NTRPConstants.MAX_BARREL_PENALTY
        barrel_adjusted = max(base_level - max_penalty, barrel_adjusted)
        
        # 4. 高水平全面型加成
        bonus = 0.0
        if mean >= NTRPConstants.HIGH_LEVEL_THRESHOLD and balance_factor >= NTRPConstants.BALANCE_THRESHOLD:
            bonus = NTRPConstants.COMPREHENSIVE_BONUS
        
        final_level = barrel_adjusted + bonus
        
        return {
            'mean': mean,
            'variance': variance,
            'min': min_score,
            'max': max_score,
            'balance_factor': balance_factor,
            'barrel_adjusted': barrel_adjusted,
            'bonus': bonus,
            'final_level': final_level
        }
    
    def _build_summary_text(
        self,
        rounded_level: float,
        level_label: str,
        dimension_scores: Dict[str, float],
        dimension_comments: Dict[str, str],
        advantages: List[str],
        weaknesses: List[str],
    ) -> str:
        """构建总体评估文本"""
        lines = []
        
        # 总体等级
        lines.append(f"根据你的回答，你的NTRP等级为 {rounded_level:.1f}（{level_label}）。")
        
        # 优势分析
        if advantages:
            advantage_names = [self.config_manager.get_dimension_name(dim) for dim in advantages]
            lines.append(f"你的优势项目包括：{', '.join(advantage_names)}。")
        
        # 短板分析
        if weaknesses:
            weakness_names = [self.config_manager.get_dimension_name(dim) for dim in weaknesses]
            lines.append(f"需要重点改进的方面有：{', '.join(weakness_names)}。")
        
        # 训练建议
        if weaknesses:
            # 这里可以考虑使用更个性化的建议，但目前保持简洁
            lines.append("建议在日常训练中重点针对短板项目进行专项练习，这样能更快提升整体水平。")
        
        # 鼓励语
        if rounded_level >= 4.0:
            lines.append("你已经具备了相当不错的网球技术水平，继续保持训练就能向更高层次迈进！")
        elif rounded_level >= 3.0:
            lines.append("你正处在快速进步的阶段，坚持规律训练能让你的技术有显著提升！")
        else:
            lines.append("继续保持学习的热情，随着练习的积累你会感受到明显的技术进步！")
        
        return " ".join(lines)