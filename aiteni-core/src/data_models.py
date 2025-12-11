"""
数据模型层

包含所有数据结构定义，包括问题配置、评估结果、图表数据等。
所有其他模块都应该从这里导入数据模型。
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


# =========================
#  基础枚举定义
# =========================

class DimensionTag(Enum):
    """维度标签枚举"""
    ADVANTAGE = "优势"
    BALANCED = "均衡"
    WEAKNESS = "短板"


# =========================
#  配置相关数据结构
# =========================

@dataclass
class OptionConfig:
    """单个问题选项配置"""
    id: str                             # 选项ID，如 Q1_A1
    text: str                           # 选项显示文本
    center_level: float                 # 该选项对应的中心等级
    hard_cap: Optional[float] = None    # 硬性等级上限（可选）
    anchor_type: str = "normal"          # 锚点类型: normal/locator/baseline
    baseline_min_level: Optional[float] = None  # 基线最低等级（仅baseline类型使用）


@dataclass
class QuestionConfig:
    """问题配置"""
    id: str                             # 问题ID,如 Q1
    text: str                           # 问题显示文本
    dimension: str                      # 所属维度,如 baseline
    weight: float                       # 权重
    options: List[OptionConfig]         # 选项列表
    question_tier: str = "basic"        # 问题等级: basic(基础问题) / advanced(进阶问题)


# =========================
#  图表相关数据结构
# =========================

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


# =========================
#  评估结果数据结构
# =========================

@dataclass
class EvaluateResult:
    """评估结果完整输出"""
    total_level: float                            # 应用 hard cap 后的原始等级（未四舍五入）
    rounded_level: float                          # 对外展示等级（四舍五入到 0.5）
    level_label: str                              # 等级标签（初学 / 发展中业余 / 城市级...）
    dimension_scores: Dict[str, float]            # 各维度数值
    dimension_comments: Dict[str, str]            # 各维度长评语
    advantages: List[str]                         # 优势维度 key 列表
    weaknesses: List[str]                         # 短板维度 key 列表
    summary_text: str                             # 总结长文案
    support_distribution: Dict[float, float]      # 各等级支持度分布（调试用）
    chart_data: Optional[ChartData] = None        # 图表数据
    # 木桶效应相关统计
    base_level: Optional[float] = None            # Anchor机制计算的基础等级
    dimension_mean: Optional[float] = None        # 维度平均值
    dimension_variance: Optional[float] = None    # 维度方差
    dimension_min: Optional[float] = None         # 最低维度分数
    dimension_max: Optional[float] = None         # 最高维度分数
    balance_factor: Optional[float] = None        # 均衡度因子(0-1)
    barrel_adjusted_level: Optional[float] = None # 木桶修正后等级
    comprehensive_bonus: Optional[float] = None   # 全面型加成


# =========================
#  常量定义
# =========================

class NTRPConstants:
    """NTRP 评估系统常量"""
    
    # 等级刻度
    LEVELS: List[float] = [
        1.0, 1.5, 2.0, 2.5,
        3.0, 3.5, 4.0, 4.5,
        5.0, 5.5, 6.0, 7.0,
    ]
    
    # 等级标签映射
    LEVEL_LABELS: Dict[float, str] = {
        1.0: "初学者",
        1.5: "初学者",
        2.0: "发展中初学者",
        2.5: "发展中初学者",
        3.0: "发展中业余选手",
        3.5: "发展中业余选手",
        4.0: "中等业余选手",
        4.5: "中高级业余选手",
        5.0: "高级业余选手",
        5.5: "优秀业余选手",
        6.0: "城市级选手",
        7.0: "职业级选手",
    }
    
    # 维度元数据
    DIMENSION_META: Dict[str, str] = {
        "baseline": "底线对拉",
        "forehand": "正手技术",
        "backhand": "反手技术", 
        "serve": "发球技术",
        "return": "接发球",
        "net": "网前技术",
        "footwork": "步法移动",
        "tactics": "战术意识",
        "match_result": "比赛表现",
        "training": "训练频率"
    }
    
    # 维度分组配置（用于条形图）
    DIMENSION_GROUPS: Dict[str, List[str]] = {
        "基础技术": ["baseline", "forehand", "backhand", "serve", "return"],
        "网前&移动": ["net", "footwork"],
        "比赛&经验": ["tactics", "match_result", "training"]
    }
    
    # Anchor机制相关常量
    LOCATOR_SIGMA: float = 0.5          # 定位选项的标准差
    BASELINE_SIGMA: float = 1.0         # 基线选项的标准差
    LOCATOR_BOOST: float = 1.2          # 定位选项的权重加成系数
    
    # 木桶效应相关常量
    VARIANCE_LOW: float = 0.1           # 基本均衡的方差阈值
    VARIANCE_HIGH: float = 1.0          # 不平衡严重的方差阈值
    BALANCE_THRESHOLD: float = 0.8      # 高均衡度阈值
    HIGH_LEVEL_THRESHOLD: float = 4.5   # 高水平阈值
    MAX_BARREL_PENALTY: float = 1.0     # 木桶效应最大下调幅度
    COMPREHENSIVE_BONUS: float = 0.25   # 全面型选手加成


# =========================
#  辅助函数
# =========================

def get_level_label(level: float, config_manager=None) -> str:
    """
    根据等级获取标签
    
    Args:
        level: NTRP等级
        config_manager: 配置管理器，可选
        
    Returns:
        等级标签
    """
    # 四舍五入到最近的0.5
    rounded = round(level * 2) / 2
    
    # 确保在有效范围内
    rounded = max(1.0, min(7.0, rounded))
    
    if config_manager:
        return config_manager.get_level_label(rounded)
    else:
        # 默认值兼容
        return f"等级{rounded:.1f}"


def round_to_half(value: float) -> float:
    """
    四舍五入到最近的0.5
    
    Args:
        value: 原始数值
        
    Returns:
        四舍五入后的数值
    """
    return round(value * 2) / 2