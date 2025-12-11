"""
交互式用户界面

负责用户交互、输入收集和基础界面展示。
提供命令行界面的交互逻辑。
"""

from typing import Dict, List, Optional
import sys
import random

from data_models import QuestionConfig, NTRPConstants


class InteractiveUI:
    """交互式用户界面"""
    
    def __init__(self):
        """初始化交互界面"""
        pass
    
    def show_welcome(self) -> None:
        """显示欢迎信息"""
        print("\n" + "="*50)
        print("🎾 NTRP 网球等级评估系统")
        print("="*50)
        print("基于多维度模糊评分机制，为您提供科学的网球水平评估")
        print("通过回答12个问题，我们将分析您在各个技术维度的表现")
        print("并为您提供详细的评估报告和训练建议")
        print()
    
    def show_main_menu(self) -> int:
        """
        显示主菜单并获取用户选择
        
        Returns:
            用户选择的选项编号
        """
        print("\n请选择运行模式:")
        print("1. 🏃‍♂️ 交互式评估 (根据你的情况回答问题)")
        print("2. 🎬 演示模式 (查看不同水平的评估示例)")
        print("3. 🚪 退出")
        
        while True:
            try:
                choice = input("\n请选择 (1-3): ").strip()
                
                if choice in ["1", "2", "3"]:
                    return int(choice)
                else:
                    print("❌ 请输入 1、2 或 3")
                    
            except (ValueError, EOFError, KeyboardInterrupt):
                print("\n❌ 输入无效，请重试")
    
    def show_demo_menu(self, demo_cases: List[Dict]) -> int:
        """
        显示演示模式菜单
        
        Args:
            demo_cases: 演示用例列表
            
        Returns:
            用户选择的选项编号
        """
        print("\n演示模式 - 请选择要查看的示例:")
        
        for i, case in enumerate(demo_cases, 1):
            print(f"{i}. {case['name']} - {case['description']}")
        
        print(f"{len(demo_cases) + 1}. 查看所有示例对比")
        print(f"{len(demo_cases) + 2}. 返回主菜单")
        
        while True:
            try:
                choice = input(f"\n请选择 (1-{len(demo_cases) + 2}): ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(demo_cases) + 2:
                    return choice_num
                else:
                    print(f"❌ 请输入 1 到 {len(demo_cases) + 2} 之间的数字")
                    
            except (ValueError, EOFError, KeyboardInterrupt):
                print("\n❌ 输入无效，请重试")
    
    def collect_answers(self, questions: List[QuestionConfig]) -> Optional[Dict[str, str]]:
        """
        收集用户对所有问题的答案
        
        Args:
            questions: 问题配置列表
            
        Returns:
            答案字典，如果用户取消则返回None
        """
        print("\n开始评估，请根据您的实际情况选择最合适的答案")
        print("(输入 'q' 可以随时退出)")
        print("-" * 50)
        
        answers: Dict[str, str] = {}
        
        # 创建问题列表的副本并打乱顺序，以避免用户感知到维度分组
        display_questions = questions.copy()
        random.shuffle(display_questions)
        
        for i, question in enumerate(display_questions, 1):
            print(f"\n【问题 {i}/{len(questions)}】")
            print(f"📋 {question.text}")
            print()
            
            # 显示选项
            for j, option in enumerate(question.options, 1):
                print(f"   {j}. {option.text}")
            
            # 获取用户选择
            while True:
                try:
                    user_input = input(f"\n请选择 (1-{len(question.options)}): ").strip()
                    
                    # 检查是否要退出
                    if user_input.lower() == 'q':
                        print("\n用户取消了评估")
                        return None
                    
                    # 验证输入
                    choice_num = int(user_input)
                    if 1 <= choice_num <= len(question.options):
                        selected_option = question.options[choice_num - 1]
                        answers[question.id] = selected_option.id
                        print(f"✅ 已选择: {selected_option.text}")
                        break
                    else:
                        print(f"❌ 请输入 1 到 {len(question.options)} 之间的数字")
                        
                except ValueError:
                    print("❌ 请输入有效的数字")
                except (EOFError, KeyboardInterrupt):
                    print("\n\n用户取消了评估")
                    return None
        
        print(f"\n✅ 已完成所有 {len(questions)} 个问题的回答")
        print("正在分析您的答案...")
        
        return answers
    
    def confirm_continue(self, message: str = "按回车键继续...") -> None:
        """
        等待用户确认继续
        
        Args:
            message: 提示信息
        """
        try:
            input(f"\n{message}")
        except (EOFError, KeyboardInterrupt):
            pass
    
    def show_evaluation_tips(self) -> None:
        """显示评估提示"""
        print("\n📝 评估说明:")
        print("• 请根据您的真实水平选择答案，这样评估结果才会准确")
        print("• 如果某个技术您还不太熟悉，请选择相应的初级选项")
        print("• 评估大约需要3-5分钟，请耐心完成所有问题")
        print("• 完成后您将获得详细的技术分析和训练建议")
    
    def show_questions_summary(self, questions: List[QuestionConfig]) -> None:
        """
        显示问题概要
        
        Args:
            questions: 问题列表
        """
        print(f"\n📊 本次评估包含 {len(questions)} 个问题，涵盖以下技术维度:")
        
        # 按维度分组显示
        dimensions = set(q.dimension for q in questions)
        dimension_counts = {}
        for dim in dimensions:
            count = sum(1 for q in questions if q.dimension == dim)
            dimension_counts[dim] = count
        
        for group_name, dims in NTRPConstants.DIMENSION_GROUPS.items():
            group_questions = [dim for dim in dims if dim in dimensions]
            if group_questions:
                print(f"\n{group_name}:")
                for dim in group_questions:
                    dim_name = NTRPConstants.DIMENSION_META.get(dim, dim)
                    count = dimension_counts.get(dim, 0)
                    print(f"  • {dim_name} ({count}题)")
    
    def show_success(self, message: str) -> None:
        """
        显示成功信息
        
        Args:
            message: 成功信息
        """
        print(f"✅ {message}")
    
    def show_error(self, message: str) -> None:
        """
        显示错误信息
        
        Args:
            message: 错误信息
        """
        print(f"❌ {message}")
    
    def show_warning(self, message: str) -> None:
        """
        显示警告信息
        
        Args:
            message: 警告信息
        """
        print(f"⚠️ {message}")
    
    def show_info(self, message: str) -> None:
        """
        显示一般信息
        
        Args:
            message: 信息内容
        """
        print(f"ℹ️ {message}")
    
    def show_goodbye(self) -> None:
        """显示告别信息"""
        print("\n" + "="*50)
        print("感谢使用 NTRP 网球等级评估系统！")
        print("希望评估结果对您的网球训练有所帮助")
        print("继续加油，不断提升您的网球技术水平！🎾")
        print("="*50)
    
    def get_user_confirmation(self, message: str) -> bool:
        """
        获取用户确认
        
        Args:
            message: 确认信息
            
        Returns:
            用户是否确认
        """
        while True:
            try:
                response = input(f"{message} (y/N): ").strip().lower()
                if response in ['y', 'yes', 'Y', '是']:
                    return True
                elif response in ['n', 'no', 'N', '否', '']:
                    return False
                else:
                    print("请输入 y(是) 或 n(否)")
            except (EOFError, KeyboardInterrupt):
                return False