"""
应用控制器

作为控制层协调各个组件，管理应用程序的主要业务流程。
负责初始化各个组件并协调它们之间的交互。
"""

import pathlib
from typing import Optional, List, Dict, Any

from config_manager import ConfigManager
from ntrp_evaluator import NTRPEvaluator
from chart_generator import ChartGenerator
from interactive_ui import InteractiveUI
from result_display import ResultDisplay
from data_models import QuestionConfig, EvaluateResult


class AppController:
    """应用程序控制器"""
    
    def __init__(self, config_dir: Optional[pathlib.Path] = None):
        """
        初始化控制器
        
        Args:
            config_dir: 配置文件目录，如果为None则使用默认目录
        """
        # 初始化各个组件
        self.config_manager = ConfigManager(config_dir)
        self.ui = InteractiveUI()
        self.display = ResultDisplay(self.config_manager)
        self.chart_generator = ChartGenerator(self.config_manager)
        
        # 核心组件（需要配置初始化）
        self._evaluator: Optional[NTRPEvaluator] = None
        self._questions: Optional[List[QuestionConfig]] = None
        self._is_initialized = False
    
    def initialize(self) -> bool:
        """
        初始化评估系统
        
        Returns:
            是否初始化成功
        """
        try:
            # 加载配置
            self._questions = self.config_manager.load_questions()
            suggestions = self.config_manager.load_suggestions()
            
            # 初始化评估器
            self._evaluator = NTRPEvaluator(self._questions, suggestions, self.config_manager)
            
            self._is_initialized = True
            return True
            
        except Exception as e:
            self.ui.show_error(f"系统初始化失败: {e}")
            return False
    
    def run(self) -> None:
        """运行主程序"""
        # 显示欢迎信息
        self.ui.show_welcome()
        
        # 初始化系统
        if not self.initialize():
            return
        
        self.ui.show_success(f"成功加载 {len(self._questions)} 个问题和评语规则")
        
        # 主程序循环
        while True:
            try:
                choice = self.ui.show_main_menu()
                
                if choice == 1:
                    self._handle_interactive_evaluation()
                elif choice == 2:
                    self._handle_demo_mode()
                elif choice == 3:
                    self.ui.show_goodbye()
                    break
                    
            except KeyboardInterrupt:
                print("\n")
                self.ui.show_goodbye()
                break
            except Exception as e:
                self.ui.show_error(f"程序运行出错: {e}")
    
    def _handle_interactive_evaluation(self) -> None:
        """处理交互式评估流程（两阶段模式）"""
        try:
            # 显示评估提示
            self.display.display_evaluation_tips()
            self.ui.show_evaluation_tips()
            self.ui.show_questions_summary(self._questions)
            
            self.ui.confirm_continue("准备好了吗？按回车开始评估...")
            
            # 分离基础题和进阶题
            basic_questions = [q for q in self._questions if q.question_tier == "basic"]
            advanced_questions = [q for q in self._questions if q.question_tier == "advanced"]
            
            # 阶段一：基础题评估
            print(f"\n{'='*50}")
            print(f"📊 【基础评估】 共 {len(basic_questions)} 题")
            print(f"{'='*50}")
            
            basic_answers = self.ui.collect_answers(basic_questions)
            
            if not basic_answers:  # 用户取消
                return
            
            # 验证基础题答案（不要求所有问题都有答案）
            if not self.config_manager.validate_answers(basic_answers, require_all=False):
                self.ui.show_error("答案验证失败")
                return
            
            # 执行基础题评估，获得初步等级
            basic_result = self._evaluator.evaluate(basic_answers)
            L_screen = basic_result.total_level
            
            # 判断是否需要进阶题
            all_answers = basic_answers.copy()
            
            if L_screen < 3.0:
                # 低水平选手，跳过进阶题
                print(f"\n正在分析您的答案...")
            else:
                # 需要进阶题
                print(f"\n{'='*50}")
                print(f"📊 【进阶评估】 共 {len(advanced_questions)} 题")
                print(f"{'='*50}")
                
                # 收集进阶题答案（不允许中途退出）
                advanced_answers = self.ui.collect_answers(advanced_questions)
                
                if advanced_answers and self.config_manager.validate_answers(advanced_answers, require_all=False):
                    all_answers.update(advanced_answers)
            
            # 执行最终评估
            print("\n正在生成完整评估报告...")
            result = self._evaluator.evaluate(all_answers)
            
            # 生成图表数据
            result.chart_data = self.chart_generator.generate_chart_data(result)
            
            # 展示结果
            self.display.display_summary_card("🎾 您的NTRP评估结果", result)
            
            # 询问是否查看详细分析
            if self.ui.get_user_confirmation("是否查看详细评估报告？"):
                self.display.display_detailed_result("🎾 您的NTRP详细评估报告", result)
            
            self.ui.confirm_continue()
            
        except Exception as e:
            self.ui.show_error(f"评估过程出错: {e}")
    
    def _handle_demo_mode(self) -> None:
        """处理演示模式"""
        try:
            demo_cases = self.config_manager.get_demo_cases()
            
            while True:
                choice = self.ui.show_demo_menu(demo_cases)
                
                if choice == len(demo_cases) + 2:  # 返回主菜单
                    break
                elif choice == len(demo_cases) + 1:  # 查看所有案例
                    self._show_all_demo_cases(demo_cases)
                elif 1 <= choice <= len(demo_cases):
                    self._show_single_demo_case(demo_cases[choice - 1])
                    
        except Exception as e:
            self.ui.show_error(f"演示模式出错: {e}")
    
    def _show_all_demo_cases(self, demo_cases: List[Dict[str, Any]]) -> None:
        """显示所有演示案例对比"""
        print("\n" + "="*80)
        print("📊 演示案例对比")
        print("="*80)
        
        for case in demo_cases:
            result = self._evaluator.evaluate(case["answers"])
            result.chart_data = self.chart_generator.generate_chart_data(result)
            self.display.display_simple_result(case["name"], result)
        
        print("="*80)
        self.ui.confirm_continue()
    
    def _show_single_demo_case(self, case: Dict[str, Any]) -> None:
        """显示单个演示案例"""
        result = self._evaluator.evaluate(case["answers"])
        result.chart_data = self.chart_generator.generate_chart_data(result)
        
        # 先显示简略版
        self.display.display_summary_card(f"📋 {case['name']}", result)
        
        # 询问是否查看详细分析
        if self.ui.get_user_confirmation("是否查看详细评估报告？"):
            self.display.display_detailed_result(f"📋 {case['name']} - 详细报告", result)
        
        self.ui.confirm_continue()
    
    def get_questions(self) -> List[QuestionConfig]:
        """
        获取问题列表
        
        Returns:
            问题列表
            
        Raises:
            RuntimeError: 如果系统未初始化
        """
        if not self._is_initialized or not self._questions:
            raise RuntimeError("系统未初始化或问题配置加载失败")
        return self._questions
    
    def validate_answers(self, answers: Dict[str, str]) -> bool:
        """
        验证答案有效性
        
        Args:
            answers: 用户答案
            
        Returns:
            是否有效
        """
        return self.config_manager.validate_answers(answers)
    
    def evaluate_answers(self, answers: Dict[str, str]) -> EvaluateResult:
        """
        评估答案并生成结果
        
        Args:
            answers: 用户答案
            
        Returns:
            评估结果
            
        Raises:
            RuntimeError: 如果系统未初始化
            ValueError: 如果答案无效
        """
        if not self._is_initialized or not self._evaluator:
            raise RuntimeError("系统未初始化")
        
        if not self.validate_answers(answers):
            raise ValueError("答案验证失败")
        
        # 执行评估
        result = self._evaluator.evaluate(answers)
        
        # 生成图表数据
        result.chart_data = self.chart_generator.generate_chart_data(result)
        
        return result
    
    def get_demo_cases(self) -> List[Dict[str, Any]]:
        """
        获取演示案例
        
        Returns:
            演示案例列表
        """
        return self.config_manager.get_demo_cases()
    
    @property
    def is_initialized(self) -> bool:
        """
        检查是否已初始化
        
        Returns:
            是否已初始化
        """
        return self._is_initialized