"""
结果显示器

负责格式化和显示评估结果。
提供多种格式的结果展示方式。
"""

from typing import Dict, List

from data_models import EvaluateResult, ChartData, NTRPConstants, DimensionTag


class ResultDisplay:
    """结果显示器"""
    
    def __init__(self, config_manager):
        """初始化结果显示器"""
        self.config_manager = config_manager
    
    def display_summary_card(self, title: str, result: EvaluateResult) -> None:
        """
        显示简略版卡片（概览卡）
        
        Args:
            title: 显示标题
            result: 评估结果
        """
        print("\n" + "="*50)
        print(f"🎾 {title}")
        print("="*50)
        
        # 卡片顶部 - 总体等级
        print(f"🎾 NTRP {result.rounded_level:.1f}")
        print(f"{result.level_label}")
        
        # 中部 - 能力雷达图概要
        print("\n📊 技术能力概览:")
        self._display_radar_summary(result)
        
        # 底部 - 优势和提升重点
        print("\n💪 主要优势:", end=" ")
        if result.advantages:
            advantage_names = [self.config_manager.get_dimension_name(dim) for dim in result.advantages[:3]]
            print(" / ".join(advantage_names))
        else:
            print("各方面发展较为均衡")
        
        print("🎯 提升重点:", end=" ")
        if result.weaknesses:
            weakness_names = [self.config_manager.get_dimension_name(dim) for dim in result.weaknesses[:3]]
            print(" / ".join(weakness_names))
        else:
            print("继续保持全面发展")
        
        print("\n" + "="*50)
    
    def display_detailed_result(self, title: str, result: EvaluateResult) -> None:
        """
        显示详细版卡片（完整评语版）
        
        Args:
            title: 显示标题
            result: 评估结果
        """
        print("\n" + "="*60)
        print(f"  {title}")
        print("="*60)
        
        # 1. 结果头部
        self._display_result_header(result)
        
        # 2. 总体摘要段落
        self._display_overall_summary(result)
        
        # 3. 优势维度 - 展开描述
        self._display_detailed_advantages(result)
        
        # 4. 提升重点 - 展开描述
        self._display_detailed_improvements(result)
        
        # 5. 各维度得分与评语
        self._display_dimension_details_expanded(result)
        
        # 6. 结尾建议
        self._display_final_suggestions(result)
        
        print("="*60)
    
    def display_full_result(self, title: str, result: EvaluateResult) -> None:
        """
        显示完整的评估结果（兼容旧接口）
        
        Args:
            title: 显示标题
            result: 评估结果
        """
        self.display_detailed_result(title, result)
    
    def display_simple_result(self, title: str, result: EvaluateResult) -> None:
        """
        显示简化的评估结果
        
        Args:
            title: 显示标题
            result: 评估结果
        """
        print(f"\n📋 {title}")
        print("-" * 40)
        
        # 显示基本信息
        print(f"🎾 NTRP等级: {result.rounded_level:.1f} ({result.level_label})")
        
        # 显示优势和短板
        if result.advantages:
            advantage_names = [self.config_manager.get_dimension_name(dim) for dim in result.advantages]
            print(f"💪 优势项目: {', '.join(advantage_names)}")
        
        if result.weaknesses:
            weakness_names = [self.config_manager.get_dimension_name(dim) for dim in result.weaknesses]
            print(f"📈 改进方向: {', '.join(weakness_names)}")
        
        print()
    
    def _display_result_header(self, result: EvaluateResult) -> None:
        """显示结果头部"""
        print(f"\n🎾 总体等级: NTRP {result.rounded_level:.1f} ({result.level_label})")
        print(f"原始得分: {result.total_level:.2f}")
    
    def _display_overall_summary(self, result: EvaluateResult) -> None:
        """显示总体摘要段落"""
        print(f"\n整体来看，你当前的综合水平约为 NTRP {result.rounded_level:.1f}（{result.level_label}）。")
        
        summary_parts = []
        if result.advantages:
            advantage_names = [self.config_manager.get_dimension_name(dim) for dim in result.advantages]
            summary_parts.append(f"在同水平玩家中，你已经具备一定的实战竞争力，尤其在{'、'.join(advantage_names)}上表现较好。")
        
        if result.weaknesses:
            weakness_names = [self.config_manager.get_dimension_name(dim) for dim in result.weaknesses]
            summary_parts.append(f"如果能够补上{'、'.join(weakness_names)}等环节，你的整体实力还有明显上升空间。")
        
        for part in summary_parts:
            print(part)
    
    def _display_radar_summary(self, result: EvaluateResult) -> None:
        """显示雷达图概要"""
        # 从配置获取维度分组
        knowledge = self.config_manager.load_tennis_knowledge()
        dimension_groups = knowledge.get("dimension_groups", {})
        
        # 按分组显示核心维度得分
        for group_name, dimensions in dimension_groups.items():
            group_dims = [(dim, result.dimension_scores.get(dim)) for dim in dimensions 
                         if dim in result.dimension_scores]
            
            if group_dims:
                dim_scores = [f"{self.config_manager.get_dimension_name(dim)}({score:.1f})" 
                             for dim, score in group_dims if score is not None]
                print(f"   {group_name}: {' / '.join(dim_scores)}")
    
    def _display_detailed_advantages(self, result: EvaluateResult) -> None:
        """显示优势维度展开描述"""
        if not result.advantages:
            return
            
        print(f"\n💪 你的主要优势：")
        print()
        
        for dim in result.advantages:
            dim_name = self.config_manager.get_dimension_name(dim)
            score = result.dimension_scores.get(dim, 0)
            
            # 获取现状表现（从dimension_suggestions.json）
            current_state = self.config_manager.get_dimension_suggestion(dim, score)
            
            # 获取优势利用建议（从tennis_knowledge.json）
            advantage_suggestion = self.config_manager.get_advantage_suggestion(dim)
            
            print(f"- {dim_name}（约 {score:.1f} 级）：")
            if current_state:
                # 分割现状描述和建议，提取现状部分
                current_lines = [line.strip() for line in current_state.split('。') if line.strip()]
                if current_lines:
                    # 显示现状表现（第一句作为现状描述）
                    print(f"  {current_lines[0]}。")
            
            # 显示如何继续放大优势/作为得分手段
            if advantage_suggestion:
                print(f"  {advantage_suggestion}")
            print()
    
    def _display_detailed_improvements(self, result: EvaluateResult) -> None:
        """显示提升重点展开描述"""
        if not result.weaknesses:
            return
            
        print(f"🎯 当前最值得优先提升的环节是：")
        print()
        
        for dim in result.weaknesses:
            dim_name = self.config_manager.get_dimension_name(dim)
            score = result.dimension_scores.get(dim, 0)
            
            # 获取现状问题描述（从dimension_suggestions.json）
            current_state = self.config_manager.get_dimension_suggestion(dim, score)
            
            # 根据差距生成个性化训练建议
            gap = result.rounded_level - score  # 计算与总体水平的差距
            training_suggestion = self._generate_personalized_training_suggestion(dim, gap)
            
            print(f"- {dim_name}（约 {score:.1f} 级）：")
            if current_state:
                # 分割描述，提取现状问题部分
                current_lines = [line.strip() for line in current_state.split('。') if line.strip()]
                if current_lines:
                    # 显示现状问题（第一句作为问题描述）
                    print(f"  {current_lines[0]}。")
            
            # 显示个性化训练建议
            if training_suggestion:
                print(f"  {training_suggestion}")
            print()
        
        # 添加总结句
        print("如果你只想抓重点，建议优先在上述 2～3 个方向投入练习时间。")
        print()
    
    def _display_dimension_details_expanded(self, result: EvaluateResult) -> None:
        """显示各维度得分与评语（逐维度展开）"""
        print("📝 各维度详细评估与建议：")
        print()
        
        # 从配置获取维度分组
        knowledge = self.config_manager.load_tennis_knowledge()
        dimension_groups = knowledge.get("dimension_groups", {})
        
        for group_name, dimensions in dimension_groups.items():
            group_has_content = any(dim in result.dimension_scores for dim in dimensions)
            if group_has_content:
                for dim in dimensions:
                    if dim in result.dimension_scores:
                        dim_name = self.config_manager.get_dimension_name(dim)
                        score = result.dimension_scores[dim]
                        
                        # 获取基础评语（从dimension_suggestions.json）
                        base_comment = self.config_manager.get_dimension_suggestion(dim, score)
                        
                        # 获取相对评语（基于分数相对整体的差异）
                        diff = score - result.rounded_level
                        if diff >= 0.5:
                            relative_comment = "你在这一项上明显高于整体水平，可以把它当成比赛中的主要得分手段之一。"
                        elif diff <= -0.5:
                            relative_comment = "这一项相对是短板，会在比赛中拖慢整体上限，建议作为近期重点练习方向。"
                        else:
                            relative_comment = "这一项与整体水平大体一致，可以在保持稳定的基础上，循序渐进地提高质量。"
                        
                        print(f"【{dim_name}（约 {score:.1f} 级）】")
                        if base_comment:
                            print(f"{base_comment}")
                        print(f"{relative_comment}")
                        print()
    
    def _display_final_suggestions(self, result: EvaluateResult) -> None:
        """显示结尾建议"""
        print(self.config_manager.get_general_training_advice("weekly_practice"))
        print(self.config_manager.get_general_training_advice("periodic_evaluation"))
        print()
    
    def _display_level_description(self, level: float) -> None:
        """显示等级详细说明"""
        description = self.config_manager.get_level_description(level)
        if description:
            print(f"💡 等级说明: {description}")
    
    def _display_dimension_analysis(self, result: EvaluateResult) -> None:
        """显示维度分析"""
        print(f"\n📊 技术维度分析:")
        print("-" * 40)
        
        # 按分组显示
        for group_name, dimensions in NTRPConstants.DIMENSION_GROUPS.items():
            group_dims = [(dim, result.dimension_scores.get(dim)) for dim in dimensions 
                         if dim in result.dimension_scores]
            
            if group_dims:
                print(f"\n🔍 {group_name}:")
                for dim, score in group_dims:
                    if score is not None:
                        dim_name = NTRPConstants.DIMENSION_META.get(dim, dim)
                        bar = self._create_score_bar(score, result.rounded_level)
                        tag = self._get_dimension_tag_text(score, result.rounded_level)
                        print(f"   {dim_name:8} {score:.1f} {bar} {tag}")
    
    def _create_score_bar(self, score: float, total_level: float) -> str:
        """创建分数条形图"""
        # 将分数转换为条形长度 (1-7 -> 0-20)
        bar_length = int((score - 1.0) / 6.0 * 20)
        bar_length = max(0, min(20, bar_length))
        
        # 确定颜色（相对于总体水平）
        diff = score - total_level
        if diff >= 0.5:
            # 优势项目用绿色
            filled = "█" * bar_length
            empty = "░" * (20 - bar_length)
            return f"[{filled}{empty}]"
        elif diff <= -0.5:
            # 短板项目用红色标记
            filled = "▓" * bar_length
            empty = "░" * (20 - bar_length)
            return f"[{filled}{empty}]"
        else:
            # 平衡项目用蓝色
            filled = "■" * bar_length
            empty = "░" * (20 - bar_length)
            return f"[{filled}{empty}]"
    
    def _get_dimension_tag_text(self, score: float, total_level: float) -> str:
        """获取维度标签文本"""
        diff = score - total_level
        if diff >= 0.5:
            return "💪 优势"
        elif diff <= -0.5:
            return "📈 短板"
        else:
            return "⚖️ 均衡"
    
    def _display_strengths_weaknesses(self, result: EvaluateResult) -> None:
        """显示优势和短板分析"""
        print(f"\n🎯 技术特点分析:")
        print("-" * 40)
        
        if result.advantages:
            print("💪 优势项目:")
            for i, dim in enumerate(result.advantages, 1):
                dim_name = NTRPConstants.DIMENSION_META.get(dim, dim)
                score = result.dimension_scores.get(dim, 0)
                print(f"   {i}. {dim_name} (NTRP {score:.1f})")
                # 显示详细评语的第一句
                comment = result.dimension_comments.get(dim, "")
                short_comment = comment.split("。")[0] + "。" if "。" in comment else comment[:50] + "..."
                print(f"      {short_comment}")
        
        if result.weaknesses:
            print("\n📈 改进方向:")
            for i, dim in enumerate(result.weaknesses, 1):
                dim_name = NTRPConstants.DIMENSION_META.get(dim, dim)
                score = result.dimension_scores.get(dim, 0)
                print(f"   {i}. {dim_name} (NTRP {score:.1f})")
                # 显示详细评语的第一句
                comment = result.dimension_comments.get(dim, "")
                short_comment = comment.split("。")[0] + "。" if "。" in comment else comment[:50] + "..."
                print(f"      {short_comment}")
    
    def _display_chart_summary(self, chart_data: ChartData) -> None:
        """显示图表数据概要"""
        print(f"\n📈 训练优先级建议:")
        print("-" * 40)
        
        if chart_data.priority_list:
            for item in chart_data.priority_list:
                print(f"{item.rank}. {item.label} (差距: {item.gap:.1f})")
                print(f"   💡 {item.suggestion}")
                print()
        else:
            print("   各维度发展较为均衡，继续保持全面训练即可。")
    
    def _display_summary(self, result: EvaluateResult) -> None:
        """显示总体评语"""
        print(f"\n📝 综合评语:")
        print("-" * 40)
        
        # 将长文本分段显示
        summary_lines = result.summary_text.split("。")
        for line in summary_lines:
            line = line.strip()
            if line:
                print(f"   {line}。")
    
    def display_evaluation_tips(self) -> None:
        """显示评估提示信息"""
        print("\n📋 NTRP评估说明:")
        print("-" * 40)
        print("• NTRP (National Tennis Rating Program) 是国际通用的网球水平分级标准")
        print("• 分级范围从1.0到7.0，每0.5为一个档次")
        print("• 评估涵盖底线、发球、网前等多个技术维度")
        print("• 建议根据实际情况如实回答，以获得准确的评估结果")
        print("• 评估结果可作为选择比赛对手和训练方向的参考")
        
    def display_dimension_details(self, result: EvaluateResult) -> None:
        """显示详细的维度评语（兼容旧接口）"""
        self._display_dimension_details_expanded(result)

    def _generate_advantage_suggestion(self, dimension: str, current_state: str) -> str:
        """生成优势维度的建议"""
        return self.config_manager.get_advantage_suggestion(dimension)
    
    def _generate_improvement_suggestion(self, dimension: str, problem: str) -> str:
        """生成改进建议"""
        return self.config_manager.get_improvement_suggestion(dimension)
    
    def _split_dimension_comment(self, comment: str, score: float, total_level: float) -> tuple:
        """分离维度评语为基础评语和相对评语"""
        # 按句子分割
        sentences = comment.split("。")
        
        # 基础评语（通常是第一句或前几句）
        base_sentences = []
        relative_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # 如果包含相对比较的关键词，归为相对评语
            if any(keyword in sentence for keyword in ["优势", "短板", "高于", "低于", "明显", "相对", "整体水平"]):
                relative_sentences.append(sentence)
            else:
                base_sentences.append(sentence)
        
        base_comment = "。".join(base_sentences) + "。" if base_sentences else ""
        
        # 如果没有现成的相对评语，生成一个
        if not relative_sentences:
            diff = score - total_level
            if diff >= 0.5:
                relative_comment = self.config_manager.get_relative_evaluation_text("strong_advantage")
            elif diff <= -0.5:
                relative_comment = self.config_manager.get_relative_evaluation_text("weakness")
            else:
                relative_comment = self.config_manager.get_relative_evaluation_text("balanced")
        else:
            relative_comment = "。".join(relative_sentences) + "。"
        
        return base_comment, relative_comment
    
    def _generate_personalized_training_suggestion(self, dimension: str, gap: float) -> str:
        """
        根据维度和差距生成个性化训练建议
        
        Args:
            dimension: 维度名称
            gap: 与总体水平的差距
            
        Returns:
            个性化训练建议
        """
        # 获取详细的训练方法（从improvement_suggestions）
        detailed_suggestion = self.config_manager.get_improvement_suggestion(dimension)
        
        # 根据差距大小添加训练强度提示
        if gap >= 1.0:
            intensity = self.config_manager.get_training_intensity_text("high")
        elif gap >= 0.5:
            intensity = self.config_manager.get_training_intensity_text("medium")
        else:
            intensity = self.config_manager.get_training_intensity_text("low")
        
        # 组合详细方法和强度建议
        return f"{detailed_suggestion} {intensity}"