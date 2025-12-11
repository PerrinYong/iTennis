"""
配置管理器

负责加载和管理问题配置、评语规则等配置文件。
提供统一的配置访问接口。
"""

import json
import pathlib
from typing import Dict, List, Any, Optional

from data_models import QuestionConfig, OptionConfig


class ConfigManager:
    """配置文件管理器"""
    
    def __init__(self, config_dir: Optional[pathlib.Path] = None):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件目录路径，如果为None则使用默认路径
        """
        if config_dir is None:
            # 默认配置目录为当前文件上级目录的config文件夹
            self.config_dir = pathlib.Path(__file__).parent.parent / "config"
        else:
            self.config_dir = config_dir
            
        self._questions: Optional[List[QuestionConfig]] = None
        self._suggestions: Optional[Dict[str, List[Dict[str, Any]]]] = None
        self._tennis_knowledge: Optional[Dict[str, Any]] = None
    
    def load_questions(self) -> List[QuestionConfig]:
        """
        加载问题配置
        
        Returns:
            问题配置列表
            
        Raises:
            FileNotFoundError: 配置文件不存在
            ValueError: 配置文件格式错误
        """
        if self._questions is not None:
            return self._questions
            
        questions_file = self.config_dir / "questions.json"
        
        try:
            with open(questions_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"问题配置文件不存在: {questions_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"问题配置文件格式错误: {e}")

        try:
            questions: List[QuestionConfig] = []
            for q in data["questions"]:
                options = [
                    OptionConfig(
                        id=o["id"],
                        text=o["text"],
                        center_level=float(o["center_level"]),
                        hard_cap=float(o["hard_cap"]) if "hard_cap" in o else None,
                        anchor_type=o.get("anchor_type", "normal"),
                        baseline_min_level=float(o["baseline_min_level"]) if "baseline_min_level" in o else None,
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
                        question_tier=q.get("question_tier", "basic"),
                    )
                )
            
            self._questions = questions
            return questions
            
        except (KeyError, TypeError, ValueError) as e:
            raise ValueError(f"问题配置文件数据结构错误: {e}")
    
    def load_suggestions(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        加载评语建议配置
        
        Returns:
            评语规则字典，key为维度名称，value为评语规则列表
            
        Raises:
            FileNotFoundError: 配置文件不存在
            ValueError: 配置文件格式错误
        """
        if self._suggestions is not None:
            return self._suggestions
            
        suggestions_file = self.config_dir / "dimension_suggestions.json"
        
        try:
            with open(suggestions_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            self._suggestions = data
            return data
            
        except FileNotFoundError:
            raise FileNotFoundError(f"评语配置文件不存在: {suggestions_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"评语配置文件格式错误: {e}")
    
    def load_tennis_knowledge(self) -> Dict[str, Any]:
        """
        加载网球知识配置
        
        Returns:
            网球知识配置字典
            
        Raises:
            FileNotFoundError: 配置文件不存在
            ValueError: 配置文件格式错误
        """
        if self._tennis_knowledge is not None:
            return self._tennis_knowledge
            
        knowledge_file = self.config_dir / "tennis_knowledge.json"
        
        try:
            with open(knowledge_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            self._tennis_knowledge = data
            return data
            
        except FileNotFoundError:
            raise FileNotFoundError(f"网球知识配置文件不存在: {knowledge_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"网球知识配置文件格式错误: {e}")
    
    def load_dimension_suggestions(self) -> Dict[str, Any]:
        """
        加载维度建议配置
        
        Returns:
            维度建议配置字典
            
        Raises:
            FileNotFoundError: 配置文件不存在
            ValueError: 配置文件格式错误
        """
        suggestion_file = self.config_dir / "dimension_suggestions.json"
        
        try:
            with open(suggestion_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
            
        except FileNotFoundError:
            raise FileNotFoundError(f"维度建议配置文件不存在: {suggestion_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"维度建议配置文件格式错误: {e}")
    
    def get_level_description(self, level: float) -> str:
        """
        获取等级描述
        
        Args:
            level: NTRP等级
            
        Returns:
            等级描述
        """
        knowledge = self.load_tennis_knowledge()
        level_str = f"{level:.1f}"
        return knowledge.get("level_descriptions", {}).get(level_str, "")
    
    def get_level_label(self, level: float) -> str:
        """
        获取等级标签
        
        Args:
            level: NTRP等级
            
        Returns:
            等级标签
        """
        knowledge = self.load_tennis_knowledge()
        level_str = f"{level:.1f}"
        return knowledge.get("level_labels", {}).get(level_str, f"等级{level:.1f}")
    
    def get_dimension_name(self, dimension: str) -> str:
        """
        获取维度中文名称
        
        Args:
            dimension: 维度英文名
            
        Returns:
            维度中文名称
        """
        knowledge = self.load_tennis_knowledge()
        return knowledge.get("dimension_meta", {}).get(dimension, dimension)
    
    def get_advantage_suggestion(self, dimension: str) -> str:
        """
        获取优势维度建议
        
        Args:
            dimension: 维度名称
            
        Returns:
            建议文本
        """
        knowledge = self.load_tennis_knowledge()
        suggestions = knowledge.get("advantage_suggestions", {})
        return suggestions.get(dimension, suggestions.get("default", "这是你的优势项目。"))
    
    def get_improvement_suggestion(self, dimension: str) -> str:
        """
        获取改进建议
        
        Args:
            dimension: 维度名称
            
        Returns:
            建议文本
        """
        knowledge = self.load_tennis_knowledge()
        suggestions = knowledge.get("improvement_suggestions", {})
        return suggestions.get(dimension, suggestions.get("default", "建议加强这方面的练习。"))
    
    def get_relative_evaluation_text(self, evaluation_type: str) -> str:
        """
        获取相对评价文本
        
        Args:
            evaluation_type: 评价类型 (strong_advantage, moderate_advantage, weakness, balanced)
            
        Returns:
            评价文本
        """
        knowledge = self.load_tennis_knowledge()
        texts = knowledge.get("relative_evaluation_texts", {})
        return texts.get(evaluation_type, "")
    
    def get_dimension_suggestion(self, dimension: str, score: float) -> str:
        """
        根据维度和分数获取详细建议
        
        Args:
            dimension: 维度名称
            score: 分数
            
        Returns:
            建议文本
        """
        suggestions_config = self.load_dimension_suggestions()
        dimension_suggestions = suggestions_config.get("suggestions", {}).get(dimension, [])
        
        # 根据分数找到匹配的建议
        for suggestion in dimension_suggestions:
            min_score = suggestion.get("min")
            max_score = suggestion.get("max")
            
            # 检查分数是否在范围内
            if min_score is None and max_score is None:
                continue
            elif min_score is None:
                if score <= max_score:
                    return suggestion.get("text", "")
            elif max_score is None:
                if score >= min_score:
                    return suggestion.get("text", "")
            else:
                if min_score <= score <= max_score:
                    return suggestion.get("text", "")
        
        return f"暂无针对{self.get_dimension_name(dimension)} {score:.1f}分的具体建议。"
    
    def get_training_intensity_text(self, intensity: str) -> str:
        """
        获取训练强度文本
        
        Args:
            intensity: 强度级别 (high, medium, low)
            
        Returns:
            强度描述文本
        """
        knowledge = self.load_tennis_knowledge()
        texts = knowledge.get("training_intensity_texts", {})
        return texts.get(intensity, "")
    
    def get_general_training_advice(self, advice_type: str) -> str:
        """
        获取通用训练建议
        
        Args:
            advice_type: 建议类型 (weekly_practice, periodic_evaluation, focus_on_weakness)
            
        Returns:
            建议文本
        """
        knowledge = self.load_tennis_knowledge()
        advice = knowledge.get("general_training_advice", {})
        return advice.get(advice_type, "")
    
    def get_question_by_id(self, question_id: str) -> Optional[QuestionConfig]:
        """
        根据ID获取问题配置
        
        Args:
            question_id: 问题ID
            
        Returns:
            问题配置，如果不存在返回None
        """
        questions = self.load_questions()
        for question in questions:
            if question.id == question_id:
                return question
        return None
    
    def get_option_by_id(self, question_id: str, option_id: str) -> Optional[OptionConfig]:
        """
        根据ID获取选项配置
        
        Args:
            question_id: 问题ID
            option_id: 选项ID
            
        Returns:
            选项配置，如果不存在返回None
        """
        question = self.get_question_by_id(question_id)
        if question is None:
            return None
            
        for option in question.options:
            if option.id == option_id:
                return option
        return None
    
    def validate_answer(self, question_id: str, option_id: str) -> bool:
        """
        验证答案是否有效
        
        Args:
            question_id: 问题ID
            option_id: 选项ID
            
        Returns:
            是否有效
        """
        return self.get_option_by_id(question_id, option_id) is not None
    
    def validate_answers(self, answers: Dict[str, str], require_all: bool = True) -> bool:
        """
        验证答案集合是否有效
        
        Args:
            answers: 答案字典，key为问题ID，value为选项ID
            require_all: 是否要求所有问题都有答案（默认True）
            
        Returns:
            是否全部有效
        """
        questions = self.load_questions()
        question_ids = {q.id for q in questions}
        
        # 如果要求所有问题都有答案
        if require_all and not question_ids.issubset(answers.keys()):
            return False
        
        # 检查每个答案是否有效
        for question_id, option_id in answers.items():
            if not self.validate_answer(question_id, option_id):
                return False
        
        return True
    
    def get_demo_cases(self) -> List[Dict[str, Any]]:
        """
        获取演示用例
        
        Returns:
            演示用例列表
        """
        return [
            {
                "name": "初级选手示例",
                "description": "刚开始学习网球，基础技术尚不稳定",
                "answers": {
                    "Q1": "Q1_A1",    # 很难连续超过3拍
                    "Q2": "Q2_A1",    # 多数球都落在发球线附近
                    "Q3": "Q3_A1",    # 正手动作不完整
                    "Q4": "Q4_A1",    # 基本不敢用反手
                    "Q5": "Q5_A1",    # 经常双误
                    "Q6": "Q6_A1",    # 基本只求发进去
                    "Q7": "Q7_A1",    # 对快球容易慌
                    "Q8": "Q8_A1",    # 很少上网
                    "Q9": "Q9_A1",    # 移动覆盖范围很小
                    "Q10": "Q10_A1",  # 基本没有战术意识
                    "Q11": "Q11_A1",  # 基本都是0:6失败
                    "Q12": "Q12_A1",  # 很少练球
                }
            },
            {
                "name": "中级选手示例",
                "description": "有一定基础，正在提高技术水平",
                "answers": {
                    "Q1": "Q1_A3",    # 能打到6-10拍
                    "Q2": "Q2_A3",    # 有时能打到底线
                    "Q3": "Q3_A3",    # 正手方向控制不错
                    "Q4": "Q4_A3",    # 反手能稳定回场
                    "Q5": "Q5_A3",    # 一发有力量但经常出界
                    "Q6": "Q6_A3",    # 有一定威胁性
                    "Q7": "Q7_A3",    # 中速发球可以稳定接进
                    "Q8": "Q8_A3",    # 正手截击还算稳定
                    "Q9": "Q9_A3",    # 能覆盖大部分底线区域
                    "Q10": "Q10_A3",  # 会观察对手弱点
                    "Q11": "Q11_A3",  # 比赛经常是3:6、4:6
                    "Q12": "Q12_A3",  # 大概每周2次
                }
            },
            {
                "name": "高级选手示例",
                "description": "技术比较全面，有一定比赛经验",
                "answers": {
                    "Q1": "Q1_A5",    # 中速对拉失误很少
                    "Q2": "Q2_A5",    # 能有意识压在对手底线
                    "Q3": "Q3_A5",    # 正手能主动压制对手
                    "Q4": "Q4_A5",    # 反手能主动变线攻击
                    "Q5": "Q5_A5",    # 一发威力大且进球率高
                    "Q6": "Q6_A5",    # 二发也有一定攻击性
                    "Q7": "Q7_A5",    # 能处理大部分发球并反击
                    "Q8": "Q8_A5",    # 网前技术比较全面
                    "Q9": "Q9_A5",    # 移动迅速，覆盖能力强
                    "Q10": "Q10_A5",  # 能制定和执行战术
                    "Q11": "Q11_A5",  # 经常能赢下6:4、6:3
                    "Q12": "Q12_A5",  # 几乎每天都练
                }
            }
        ]