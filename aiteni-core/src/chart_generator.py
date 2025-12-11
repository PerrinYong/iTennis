"""
图表数据生成器

负责生成雷达图、条形图等可视化数据。
将评估结果转换为适合前端展示的图表数据结构。
"""

from typing import Dict, List
import math

from data_models import (
    ChartData, RadarChartData, BarChartGroup, DimensionBarData, 
    DimensionTag, EvaluateResult, NTRPConstants
)


class ChartGenerator:
    """图表数据生成器"""
    
    def __init__(self, config_manager):
        """初始化图表生成器"""
        self.config_manager = config_manager
    
    def generate_chart_data(self, result: EvaluateResult) -> ChartData:
        """
        根据评估结果生成完整的图表数据
        
        Args:
            result: 评估结果
            
        Returns:
            图表数据对象
        """
        # 生成雷达图数据
        radar_data = self._generate_radar_data(result.dimension_scores)
        
        # 生成分组条形图数据
        bar_groups = self._generate_bar_groups(
            result.dimension_scores, 
            result.dimension_comments,
            result.rounded_level
        )
        
        return ChartData(
            radar_data=radar_data,
            bar_groups=bar_groups,
            priority_list=[]  # 简化为空列表，不再生成训练优先级列表
        )
    
    def _generate_radar_data(self, dimension_scores: Dict[str, float]) -> RadarChartData:
        """
        生成雷达图数据
        
        Args:
            dimension_scores: 各维度分数
            
        Returns:
            雷达图数据
        """
        # 按预定义顺序排列维度
        ordered_dimensions = []
        ordered_labels = []
        ordered_scores = []
        
        # 使用维度分组中的顺序
        for group_name, dimensions in NTRPConstants.DIMENSION_GROUPS.items():
            for dim in dimensions:
                if dim in dimension_scores:
                    ordered_dimensions.append(dim)
                    ordered_labels.append(NTRPConstants.DIMENSION_META.get(dim, dim))
                    # 将NTRP分数(1-7)转换为百分比(0-100)
                    score_percentage = self._ntrp_to_percentage(dimension_scores[dim])
                    ordered_scores.append(score_percentage)
        
        return RadarChartData(
            dimensions=ordered_dimensions,
            dimension_labels=ordered_labels,
            scores=ordered_scores,
            max_score=100.0
        )
    
    def _generate_bar_groups(
        self,
        dimension_scores: Dict[str, float],
        dimension_comments: Dict[str, str],
        total_level: float
    ) -> List[BarChartGroup]:
        """
        生成分组条形图数据
        
        Args:
            dimension_scores: 各维度分数
            dimension_comments: 各维度评语
            total_level: 总体水平
            
        Returns:
            分组条形图数据列表
        """
        bar_groups = []
        
        for group_name, dimensions in NTRPConstants.DIMENSION_GROUPS.items():
            group_data = []
            
            for dim in dimensions:
                if dim in dimension_scores:
                    score = dimension_scores[dim]
                    
                    # 生成单个维度的条形图数据
                    bar_data = DimensionBarData(
                        dimension=dim,
                        label=NTRPConstants.DIMENSION_META.get(dim, dim),
                        score=score,
                        normalized_score=self._ntrp_to_percentage(score),
                        tag=self._get_dimension_tag(score, total_level),
                        short_comment=self._extract_short_comment(dimension_comments.get(dim, "")),
                        full_comment=dimension_comments.get(dim, "")
                    )
                    group_data.append(bar_data)
            
            if group_data:
                bar_groups.append(BarChartGroup(
                    group_name=group_name,
                    dimensions=group_data
                ))
        
        return bar_groups
    
    def _ntrp_to_percentage(self, ntrp_score: float) -> float:
        """
        将NTRP分数转换为百分比
        
        Args:
            ntrp_score: NTRP分数 (1.0-7.0)
            
        Returns:
            百分比分数 (0-100)
        """
        # 将1.0-7.0映射到0-100
        # 使用非线性映射，让中等水平的差异更明显
        if ntrp_score <= 1.0:
            return 0.0
        elif ntrp_score >= 7.0:
            return 100.0
        else:
            # 使用平方根函数进行映射，使低分段差异更明显
            normalized = (ntrp_score - 1.0) / 6.0  # 归一化到0-1
            return math.sqrt(normalized) * 100.0
    
    def _get_dimension_tag(self, dimension_score: float, total_level: float) -> DimensionTag:
        """
        根据维度分数相对总体水平确定标签
        
        Args:
            dimension_score: 维度分数
            total_level: 总体水平
            
        Returns:
            维度标签
        """
        diff = dimension_score - total_level
        
        if diff >= 0.5:
            return DimensionTag.ADVANTAGE
        elif diff <= -0.5:
            return DimensionTag.WEAKNESS
        else:
            return DimensionTag.BALANCED
    
    def _extract_short_comment(self, full_comment: str) -> str:
        """
        从完整评语中提取短评语
        
        Args:
            full_comment: 完整评语
            
        Returns:
            短评语
        """
        if not full_comment:
            return ""
        
        # 用句号分割，取第一句
        sentences = full_comment.split("。")
        if sentences and sentences[0]:
            return sentences[0] + "。"
        
        # 如果没有句号，截取前50个字符
        if len(full_comment) > 50:
            return full_comment[:47] + "..."
        
        return full_comment