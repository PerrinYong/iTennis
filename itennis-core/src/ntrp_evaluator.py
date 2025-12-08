"""
NTRP 网球等级评估系统核心模块

基于多维度模糊评分机制，支持硬性上限限制，自动生成详细评语。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json
import math
import pathlib


# =========================
#  基本数据结构
# =========================

class DimensionTag(Enum):
    """维度标签枚举"""
    ADVANTAGE = "优势"
    BALANCED = "均衡"
    WEAKNESS = "短板"


@dataclass
class RadarChartData:
    """雷达图数据"""
    dimensions: List[str]              # 维度名称列表
    dimension_labels: List[str]        # 维度显示标签列表
    scores: List[float]                # 各维度分数(0-100)
    max_score: float = 100.0          # 最大分数
    

@dataclass
class DimensionBarData:
    """单个维度条形图数据"""
    dimension: str                     # 维度key
    label: str                         # 显示名称
    score: float                       # 原始分数
    normalized_score: float            # 归一化分数(0-100)
    tag: DimensionTag                  # 标签类型
    short_comment: str                 # 简短评语
    full_comment: str                  # 完整评语


@dataclass
class BarChartGroup:
    """条形图分组数据"""
    group_name: str                    # 分组名称
    dimensions: List[DimensionBarData] # 该组的维度数据


@dataclass
class PriorityItem:
    """训练优先级项目"""
    rank: int                          # 排名(1,2,3)
    dimension: str                     # 维度key
    label: str                         # 显示名称
    gap: float                         # 与整体水平差值
    normalized_gap: float              # 归一化差值(0-100)
    suggestion: str                    # 训练建议


@dataclass
class ChartData:
    """完整图表数据"""
    radar_data: RadarChartData         # 雷达图数据
    bar_groups: List[BarChartGroup]    # 分组条形图数据
    priority_list: List[PriorityItem]  # 优先级列表


@dataclass
class OptionConfig:
    """单个问题选项配置"""
    id: str
    text: str
    center_level: float
    hard_cap: Optional[float] = None


@dataclass
class QuestionConfig:
    """问题配置"""
    id: str
    text: str
    dimension: str       # baseline / forehand / ...
    weight: float
    options: List[OptionConfig]


@dataclass
class EvaluateResult:
    """评估结果完整输出"""
    total_level: float                     # 应用 hard cap 后的原始等级（未四舍五入）
    rounded_level: float                   # 对外展示等级（四舍五入到 0.5）
    level_label: str                       # 等级标签（初学 / 发展中业余 / 城市级...）
    dimension_scores: Dict[str, float]     # 各维度数值
    dimension_comments: Dict[str, str]     # 各维度长评语
    advantages: List[str]                  # 优势维度 key 列表
    weaknesses: List[str]                  # 短板维度 key 列表
    summary_text: str                      # 总结长文案
    support_distribution: Dict[float, float]  # 各等级支持度分布（调试用）
    chart_data: Optional['ChartData'] = None  # 图表数据


# =========================
#  NTRP 评估器
# =========================

class NTRPEvaluator:
    """
    NTRP 网球等级评估系统核心类（Python Demo 版）

    使用方法：
        questions = NTRPEvaluator.load_questions("questions.json")
        suggestion_rules = NTRPEvaluator.load_suggestions("dimension_suggestions.json")
        evaluator = NTRPEvaluator(questions, suggestion_rules)

        # 用户作答：question_id -> option_id
        answers = {
            "Q1": "Q1_A3",
            "Q2": "Q2_A4",
            ...
        }

        result = evaluator.evaluate(answers)
        print(result.rounded_level, result.summary_text)
    """

    # 等级刻度
    LEVELS: List[float] = [
        1.0, 1.5, 2.0, 2.5,
        3.0, 3.5, 4.0, 4.5,
        5.0, 5.5, 6.0, 7.0,
    ]

    # 维度名称映射（中文展示用）
    DIMENSION_META: Dict[str, str] = {
        "baseline": "底线综合（稳定性+深度）",
        "forehand": "正手",
        "backhand": "反手",
        "serve": "发球",
        "return": "接发球",
        "net": "网前与高压",
        "footwork": "步伐与场地覆盖",
        "tactics": "战术与心理",
        "match_result": "实战成绩",
        "training": "训练背景 / 频率",
    }

    # 雷达图核心维度（最多8个）
    RADAR_DIMENSIONS = [
        "baseline", "forehand", "backhand", "serve", 
        "return", "net", "footwork", "tactics"
    ]

    # 维度分组配置（用于条形图）
    DIMENSION_GROUPS = {
        "基础技术": ["baseline", "forehand", "backhand", "serve", "return"],
        "网前&移动": ["net", "footwork"],
        "比赛&经验": ["tactics", "match_result", "training"]
    }

    def __init__(
        self,
        questions: List[QuestionConfig],
        suggestion_rules: Dict[str, List[Dict[str, Any]]],
        spread: float = 1.0,
    ) -> None:
        self.questions = questions
        # suggestion_rules: {"baseline": [ {"min":..,"max":..,"text":..}, ... ], ...}
        self.suggestion_rules = suggestion_rules
        self.spread = spread

    # ---------- 静态加载工具 ----------

    @staticmethod
    def load_questions(path: str | pathlib.Path) -> List[QuestionConfig]:
        """从 questions.json 加载题目配置。"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        questions: List[QuestionConfig] = []
        for q in data["questions"]:
            options = [
                OptionConfig(
                    id=o["id"],
                    text=o["text"],
                    center_level=float(o["center_level"]),
                    hard_cap=float(o["hard_cap"]) if "hard_cap" in o else None,
                )
                for o in q["options"]
            ]
            questions.append(
                QuestionConfig(
                    id=q["id"],
                    text=q["text"],
                    dimension=q["dimension"],
                    weight=float(q.get("weight", 1.0)),
                    options=options,
                )
            )
        return questions

    @staticmethod
    def load_suggestions(path: str | pathlib.Path) -> Dict[str, List[Dict[str, Any]]]:
        """从 dimension_suggestions.json 加载维度评语规则。"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # data = {"suggestions": {dim: [ {min,max,text}, ... ] } }
        return data.get("suggestions", {})

    # ---------- 公共入口 ----------

    def evaluate(self, answers: Dict[str, str]) -> EvaluateResult:
        """
        核心入口：输入用户作答（question_id -> option_id），返回评估结果。
        """

        # 1) 计算 support(L) + hardCap + 维度分数
        support = {L: 0.0 for L in self.LEVELS}
        hard_cap = max(self.LEVELS)

        dim_sum: Dict[str, float] = {}
        dim_wsum: Dict[str, float] = {}

        for q in self.questions:
            if q.id not in answers:
                continue
            opt_id = answers[q.id]
            opt = self._find_option(q, opt_id)
            if not opt:
                continue

            # 模糊 membership 加到 support
            for L in self.LEVELS:
                m = self._membership(L, opt.center_level, self.spread)
                support[L] += m * q.weight

            # hard cap
            if opt.hard_cap is not None:
                hard_cap = min(hard_cap, opt.hard_cap)

            # 维度加权平均
            dim_sum[q.dimension] = dim_sum.get(q.dimension, 0.0) + opt.center_level * q.weight
            dim_wsum[q.dimension] = dim_wsum.get(q.dimension, 0.0) + q.weight

        # 2) 得到期望值 + 应用 hard cap
        raw_level = self._compute_raw_level(support, hard_cap)

        rounded_level = self._round_to_half(raw_level)
        level_label = self._map_level_to_label(rounded_level)

        # 3) 各维度分数（简单加权平均）
        dimension_scores: Dict[str, float] = {}
        for dim, s in dim_sum.items():
            w = dim_wsum.get(dim, 0.0) or 1.0
            dimension_scores[dim] = s / w

        # 4) 维度评语：基础评语 + 优/劣/中补充语
        dimension_comments = self._build_dimension_comments(
            dimension_scores, rounded_level
        )

        # 5) 优势 / 短板维度
        advantages, weaknesses = self._pick_advantages_and_weaknesses(dimension_scores)

        # 6) 总体 summary 文案
        summary = self._build_summary_text(
            rounded_level,
            level_label,
            dimension_scores,
            dimension_comments,
            advantages,
            weaknesses,
        )

        # 7) 生成图表数据
        chart_data = self._build_chart_data(
            dimension_scores,
            dimension_comments,
            rounded_level
        )

        return EvaluateResult(
            total_level=raw_level,
            rounded_level=rounded_level,
            level_label=level_label,
            dimension_scores=dimension_scores,
            dimension_comments=dimension_comments,
            advantages=advantages,
            weaknesses=weaknesses,
            summary_text=summary,
            support_distribution=support.copy(),
            chart_data=chart_data,
        )

    # =========================
    #  内部工具函数
    # =========================

    def _find_option(self, q: QuestionConfig, opt_id: str) -> Optional[OptionConfig]:
        """查找问题中的指定选项"""
        for o in q.options:
            if o.id == opt_id:
                return o
        return None

    @staticmethod
    def _membership(level: float, center: float, spread: float) -> float:
        """
        三角形隶属度函数：
            diff >= spread  -> 0
            diff == 0       -> 1
            中间线性衰减
        """
        diff = abs(level - center)
        if diff >= spread:
            return 0.0
        return 1.0 - diff / spread

    def _compute_raw_level(
        self,
        support: Dict[float, float],
        hard_cap: float,
    ) -> float:
        """基于支持度分布计算期望值等级"""
        total_support = sum(support.values())
        if total_support <= 0:
            # fallback：没有答题时，用 LEVELS 中位数
            fallback = self.LEVELS[len(self.LEVELS) // 2]
            return min(fallback, hard_cap)

        expectation = sum(L * support[L] for L in self.LEVELS) / total_support
        return min(expectation, hard_cap)

    @staticmethod
    def _round_to_half(x: float) -> float:
        """四舍五入到 0.5 的倍数。"""
        return round(x * 2) / 2.0

    @staticmethod
    def _map_level_to_label(L: float) -> str:
        """等级数值映射到中文标签"""
        if L <= 1.5:
            return "初学者"
        if L <= 2.5:
            return "入门级爱好者"
        if L <= 3.5:
            return "发展中业余选手"
        if L <= 4.5:
            return "城市级业余高手"
        if L <= 5.5:
            return "准专业 / 专业水平"
        return "职业 / 国际级水平"

    # ---------- 维度评语 ----------

    def _build_dimension_comments(
        self,
        dim_scores: Dict[str, float],
        total_level: float,
    ) -> Dict[str, str]:
        """为每个维度生成详细评语"""
        comments: Dict[str, str] = {}
        for dim, score in dim_scores.items():
            base = self._pick_base_comment(dim, score)
            extra = self._extra_comment_for_dim(score, total_level)
            comments[dim] = base + extra
        return comments

    def _pick_base_comment(self, dim: str, score: float) -> str:
        """根据维度和分数选择基础评语模板"""
        rules = self.suggestion_rules.get(dim, [])
        chosen = ""
        for rule in rules:
            r_min = float(rule.get("min", -math.inf))
            r_max = float(rule.get("max", math.inf))
            if score >= r_min and score < r_max:
                chosen = rule.get("text", "")
                break
        # 如果没匹配到，用一个通用 fallback
        if not chosen:
            chosen = f"在该维度上你的水平约为 NTRP {score:.1f}，可以结合自身情况继续针对性训练。"
        return chosen

    @staticmethod
    def _extra_comment_for_dim(score: float, total_level: float) -> str:
        """
        根据维度分数相对于整体等级的偏差，补充优势/短板/中性评语。
        """
        diff = score - total_level
        if diff >= 0.5:
            return "你在这一项上明显高于整体水平，可以把它当成比赛中的主要得分手段之一。"
        elif diff <= -0.5:
            return "这一项相对是短板，会在比赛中拖慢整体上限，建议作为近期重点练习方向。"
        else:
            return "这一项与整体水平大体一致，可以在保持稳定的基础上，循序渐进地提高质量。"

    # ---------- 优势 / 短板选择 ----------

    def _pick_advantages_and_weaknesses(
        self,
        dim_scores: Dict[str, float],
        top_k: int = 3,
    ) -> Tuple[List[str], List[str]]:
        """选择得分最高和最低的几个维度作为优势和短板"""
        items = sorted(dim_scores.items(), key=lambda kv: kv[1], reverse=True)
        if not items:
            return [], []

        advantages = [dim for dim, _ in items[:top_k]]
        weaknesses = [dim for dim, _ in reversed(items[-top_k:])]
        return advantages, weaknesses

    # ---------- Summary 文案 ----------

    def _build_summary_text(
        self,
        rounded_level: float,
        level_label: str,
        dim_scores: Dict[str, float],
        dim_comments: Dict[str, str],
        advantages: List[str],
        weaknesses: List[str],
    ) -> str:
        """组合生成完整的评估总结文案"""
        parts: List[str] = []

        # 1) 总体概述
        parts.append(
            f"整体来看，你当前的综合水平约为 NTRP {rounded_level:.1f}（{level_label}）。\n"
        )

        # 2) 优势总结
        if advantages:
            parts.append("你的主要优势在：")
            for dim in advantages:
                name = self.DIMENSION_META.get(dim, dim)
                score = dim_scores.get(dim, 0.0)
                short = self._first_sentence(dim_comments.get(dim, ""))
                parts.append(f"- {name}（约 {score:.1f} 级）：{short}")
            parts.append("")  # 空行

        # 3) 提升重点
        if weaknesses:
            parts.append("当前最值得优先提升的环节是：")
            for dim in weaknesses:
                name = self.DIMENSION_META.get(dim, dim)
                score = dim_scores.get(dim, 0.0)
                short = self._first_sentence(dim_comments.get(dim, ""))
                parts.append(f"- {name}（约 {score:.1f} 级）：{short}")
            parts.append("如果你只想抓重点，建议优先在上述 2～3 个方向投入练习时间。\n")

        # 4) 详细拆解
        parts.append("下面是各个维度的具体评估与建议：\n")

        # 按 dim_meta 定义的顺序输出，体验更统一
        for dim_key, dim_name in self.DIMENSION_META.items():
            if dim_key not in dim_scores:
                continue
            score = dim_scores[dim_key]
            comment = dim_comments.get(dim_key, "")
            parts.append(f"【{dim_name}（约 {score:.1f} 级）】")
            parts.append(comment)
            parts.append("")  # 空行

        return "\n".join(parts).strip()

    @staticmethod
    def _first_sentence(text: str) -> str:
        """
        截取评语的第一句，作为“短标签”。
        用简单的句号/感叹号分割。
        """
        if not text:
            return ""
        for sep in ["。", "！", "!"]:
            if sep in text:
                idx = text.find(sep)
                return text[: idx + 1]
        return text

    # =========================
    #  图表数据生成
    # =========================

    def _build_chart_data(
        self,
        dim_scores: Dict[str, float],
        dim_comments: Dict[str, str],
        total_level: float
    ) -> ChartData:
        """生成完整的图表数据"""
        # 1) 雷达图数据
        radar_data = self._build_radar_data(dim_scores)
        
        # 2) 分组条形图数据
        bar_groups = self._build_bar_groups_data(dim_scores, dim_comments, total_level)
        
        # 3) 优先级列表
        priority_list = self._build_priority_list(dim_scores, total_level)
        
        return ChartData(
            radar_data=radar_data,
            bar_groups=bar_groups,
            priority_list=priority_list
        )

    def _build_radar_data(self, dim_scores: Dict[str, float]) -> RadarChartData:
        """生成雷达图数据"""
        dimensions = []
        labels = []
        scores = []
        
        for dim in self.RADAR_DIMENSIONS:
            if dim in dim_scores:
                dimensions.append(dim)
                labels.append(self.DIMENSION_META.get(dim, dim))
                # 将NTRP 1.0-5.0转换为0-100
                normalized = self._normalize_score_to_percent(dim_scores[dim])
                scores.append(normalized)
        
        return RadarChartData(
            dimensions=dimensions,
            dimension_labels=labels,
            scores=scores
        )

    def _build_bar_groups_data(
        self,
        dim_scores: Dict[str, float],
        dim_comments: Dict[str, str],
        total_level: float
    ) -> List[BarChartGroup]:
        """生成分组条形图数据"""
        groups = []
        
        for group_name, group_dims in self.DIMENSION_GROUPS.items():
            group_data = []
            
            for dim in group_dims:
                if dim not in dim_scores:
                    continue
                    
                score = dim_scores[dim]
                tag = self._get_dimension_tag(score, total_level)
                short_comment = self._first_sentence(dim_comments.get(dim, ""))
                full_comment = dim_comments.get(dim, "")
                
                bar_data = DimensionBarData(
                    dimension=dim,
                    label=self.DIMENSION_META.get(dim, dim),
                    score=score,
                    normalized_score=self._normalize_score_to_percent(score),
                    tag=tag,
                    short_comment=short_comment,
                    full_comment=full_comment
                )
                group_data.append(bar_data)
            
            if group_data:  # 只添加有数据的分组
                groups.append(BarChartGroup(
                    group_name=group_name,
                    dimensions=group_data
                ))
        
        return groups

    def _build_priority_list(
        self,
        dim_scores: Dict[str, float],
        total_level: float
    ) -> List[PriorityItem]:
        """生成训练优先级列表（取前3个最大差值）"""
        # 计算各维度与整体水平的差值
        gaps = []
        for dim, score in dim_scores.items():
            gap = total_level - score  # 差值越大越该补
            if gap > 0:  # 只考虑低于整体水平的维度
                gaps.append((dim, gap))
        
        # 按差值降序排列，取前3个
        gaps.sort(key=lambda x: x[1], reverse=True)
        top_gaps = gaps[:3]
        
        priority_items = []
        for rank, (dim, gap) in enumerate(top_gaps, 1):
            suggestion = self._get_training_suggestion(dim)
            
            priority_items.append(PriorityItem(
                rank=rank,
                dimension=dim,
                label=self.DIMENSION_META.get(dim, dim),
                gap=gap,
                normalized_gap=min(gap * 25, 100),  # 粗略归一化到0-100
                suggestion=suggestion
            ))
        
        return priority_items

    @staticmethod
    def _normalize_score_to_percent(score: float) -> float:
        """将NTRP分数(1.0-5.0)归一化为百分比(0-100)"""
        # 线性映射: 1.0->0, 5.0->100
        normalized = (score - 1.0) / (5.0 - 1.0) * 100
        return max(0, min(100, normalized))

    @staticmethod 
    def _get_dimension_tag(score: float, total_level: float) -> DimensionTag:
        """根据维度分数相对于整体等级的偏差，返回标签"""
        diff = score - total_level
        if diff >= 0.5:
            return DimensionTag.ADVANTAGE
        elif diff <= -0.5:
            return DimensionTag.WEAKNESS
        else:
            return DimensionTag.BALANCED

    def _get_training_suggestion(self, dimension: str) -> str:
        """根据维度获取训练建议"""
        suggestions = {
            "baseline": "增加底线对拉练习，重点提高稳定性和深度控制",
            "forehand": "加强正手击球练习，注意动作一致性和力量转换",
            "backhand": "强化反手技术，可以练习单反或双反的基本动作",
            "serve": "重点练习发球动作和准确性，建立稳定的发球节奏",
            "return": "加强接发球练习，提高反应速度和球路预判",
            "net": "增加网前截击和高压球练习，提高上网频率",
            "footwork": "加强步伐和移动练习，提高场地覆盖能力",
            "tactics": "多参与比赛和对抗，积累战术经验和心理素质",
            "match_result": "参加更多比赛，积累实战经验",
            "training": "增加训练频率和强度，有条件可找教练指导"
        }
        return suggestions.get(dimension, f"加强{self.DIMENSION_META.get(dimension, dimension)}的针对性练习")


# =========================
#  简单示例（本地测试用）
# =========================

if __name__ == "__main__":
    # 假设当前目录下有 questions.json 和 dimension_suggestions.json
    base_dir = pathlib.Path(__file__).parent.parent / "config"

    try:
        questions = NTRPEvaluator.load_questions(base_dir / "questions.json")
        suggestions = NTRPEvaluator.load_suggestions(base_dir / "dimension_suggestions.json")

        evaluator = NTRPEvaluator(questions, suggestions, spread=1.0)

        # Demo：模拟一份回答（实际中由小程序前端收集）
        demo_answers = {
            "Q1": "Q1_A3",
            "Q2": "Q2_A4",
            "Q3": "Q3_A4",
            "Q4": "Q4_A3",
            "Q5": "Q5_A3",
            "Q6": "Q6_A3",
            "Q7": "Q7_A3",
            "Q8": "Q8_A3",
            "Q9": "Q9_A3",
            "Q10": "Q10_A3",
            "Q11": "Q11_A3",
            "Q12": "Q12_A3",
        }

        result = evaluator.evaluate(demo_answers)

        print("== NTRP 评估结果 ==")
        print("总等级(raw):", f"{result.total_level:.2f}")
        print("展示等级:", f"NTRP {result.rounded_level:.1f}", f"（{result.level_label}）\n")

        print("各维度得分：")
        for dim, score in result.dimension_scores.items():
            print(f"- {NTRPEvaluator.DIMENSION_META.get(dim, dim)}: {score:.2f}")
        print()

        print("优势维度:", result.advantages)
        print("短板维度:", result.weaknesses)
        print("\n===== 详细评语 =====\n")
        print(result.summary_text)

    except FileNotFoundError as e:
        print(f"配置文件未找到: {e}")
        print("请先创建 questions.json 和 dimension_suggestions.json 文件")