"""
测试新评分机制:Anchor机制和木桶效应
"""

import sys
from pathlib import Path

# 添加src到路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from config_manager import ConfigManager
from ntrp_evaluator import NTRPEvaluator
from data_models import NTRPConstants

def test_anchor_mechanism():
    """测试Anchor机制"""
    print("=" * 60)
    print("测试 Anchor 机制")
    print("=" * 60)
    
    # 初始化
    config_manager = ConfigManager()
    questions = config_manager.load_questions()
    suggestions = config_manager.load_suggestions()
    
    evaluator = NTRPEvaluator(
        questions=questions,
        suggestion_rules=suggestions,
        config_manager=config_manager,
        spread=1.0
    )
    
    # 测试用例: 高水平选手
    high_level_answers = {
        "Q1": "Q1_A6",   # baseline选项,4.5
        "Q2": "Q2_A6",   # 深度控制很好
        "Q3": "Q3_A6",   # 正手是主要武器
        "Q4": "Q4_A6",   # 反手不是短板
        "Q5": "Q5_A6",   # baseline选项,4.5
        "Q6": "Q6_A5",   # 发球有威胁性
        "Q7": "Q7_A5",   # 接发能处理并反击
        "Q8": "Q8_A5",   # 网前技术全面
        "Q9": "Q9_A5",   # 移动迅速
        "Q10": "Q10_A5", # 能执行战术
        "Q11": "Q11_A5", # baseline选项,4.5
        "Q12": "Q12_A4", # 经常训练
        "Q13": "Q13_A3",
        "Q14": "Q14_A3",
        "Q15": "Q15_A4",
        "Q16": "Q16_A3",
        "Q17": "Q17_A3",
        "Q18": "Q18_A4",
        "Q19": "Q19_A4",
    }
    
    result = evaluator.evaluate(high_level_answers)
    
    print(f"\n基础等级 (Anchor机制后): {result.base_level:.2f}")
    print(f"维度平均值: {result.dimension_mean:.2f}")
    print(f"维度方差: {result.dimension_variance:.3f}")
    print(f"均衡度因子: {result.balance_factor:.3f}")
    print(f"木桶修正后等级: {result.barrel_adjusted_level:.2f}")
    print(f"全面型加成: {result.comprehensive_bonus:.2f}")
    print(f"最终等级: {result.total_level:.2f}")
    print(f"四舍五入等级: {result.rounded_level:.1f} ({result.level_label})")
    
    print(f"\n维度分数:")
    for dim, score in result.dimension_scores.items():
        dim_name = NTRPConstants.DIMENSION_META.get(dim, dim)
        print(f"  {dim_name}: {score:.2f}")
    
    print(f"\n优势维度: {[NTRPConstants.DIMENSION_META.get(d, d) for d in result.advantages]}")
    print(f"短板维度: {[NTRPConstants.DIMENSION_META.get(d, d) for d in result.weaknesses]}")


def test_barrel_effect():
    """测试木桶效应"""
    print("\n" + "=" * 60)
    print("测试木桶效应")
    print("=" * 60)
    
    # 初始化
    config_manager = ConfigManager()
    questions = config_manager.load_questions()
    suggestions = config_manager.load_suggestions()
    
    evaluator = NTRPEvaluator(
        questions=questions,
        suggestion_rules=suggestions,
        config_manager=config_manager,
        spread=1.0
    )
    
    # 测试用例: 不均衡的选手(正手很强但反手很弱)
    unbalanced_answers = {
        "Q1": "Q1_A4",   # 底线对拉10拍以上
        "Q2": "Q2_A4",   # 深度中深场
        "Q3": "Q3_A5",   # 正手能主动压制(高分)
        "Q4": "Q4_A2",   # 反手只能挡回去(低分)
        "Q5": "Q5_A4",   # 发球一般
        "Q6": "Q6_A3",   # 发球威胁性一般
        "Q7": "Q7_A3",   # 接发一般
        "Q8": "Q8_A3",   # 网前一般
        "Q9": "Q9_A3",   # 步法一般
        "Q10": "Q10_A3", # 战术意识一般
        "Q11": "Q11_A3", # 比赛结果一般
        "Q12": "Q12_A3", # 训练频率
        "Q13": "Q13_A2",
        "Q14": "Q14_A1", # 反手短板
        "Q15": "Q15_A3",
        "Q16": "Q16_A2",
        "Q17": "Q17_A2",
        "Q18": "Q18_A3",
        "Q19": "Q19_A3",
    }
    
    result = evaluator.evaluate(unbalanced_answers)
    
    print(f"\n基础等级: {result.base_level:.2f}")
    print(f"维度平均值: {result.dimension_mean:.2f}")
    print(f"维度方差: {result.dimension_variance:.3f}")
    print(f"维度最小值: {result.dimension_min:.2f}")
    print(f"维度最大值: {result.dimension_max:.2f}")
    print(f"均衡度因子: {result.balance_factor:.3f}")
    print(f"木桶修正后等级: {result.barrel_adjusted_level:.2f}")
    print(f"最终等级: {result.total_level:.2f}")
    print(f"四舍五入等级: {result.rounded_level:.1f} ({result.level_label})")
    
    print(f"\n维度分数:")
    for dim, score in result.dimension_scores.items():
        dim_name = NTRPConstants.DIMENSION_META.get(dim, dim)
        print(f"  {dim_name}: {score:.2f}")
    
    print(f"\n优势维度: {[NTRPConstants.DIMENSION_META.get(d, d) for d in result.advantages]}")
    print(f"短板维度: {[NTRPConstants.DIMENSION_META.get(d, d) for d in result.weaknesses]}")
    
    print("\n说明: 由于存在明显短板(反手),木桶效应会降低总体等级")


def test_comparison():
    """对比测试:均衡 vs 不均衡"""
    print("\n" + "=" * 60)
    print("对比测试:均衡选手 vs 不均衡选手")
    print("=" * 60)
    
    config_manager = ConfigManager()
    questions = config_manager.load_questions()
    suggestions = config_manager.load_suggestions()
    
    evaluator = NTRPEvaluator(
        questions=questions,
        suggestion_rules=suggestions,
        config_manager=config_manager,
        spread=1.0
    )
    
    # 均衡选手: 所有维度都是3.5水平
    balanced_answers = {
        "Q1": "Q1_A4",
        "Q2": "Q2_A4",
        "Q3": "Q3_A4",
        "Q4": "Q4_A4",
        "Q5": "Q5_A4",
        "Q6": "Q6_A4",
        "Q7": "Q7_A4",
        "Q8": "Q8_A4",
        "Q9": "Q9_A4",
        "Q10": "Q10_A4",
        "Q11": "Q11_A3",
        "Q12": "Q12_A3",
        "Q13": "Q13_A2",
        "Q14": "Q14_A2",
        "Q15": "Q15_A3",
        "Q16": "Q16_A2",
        "Q17": "Q17_A2",
        "Q18": "Q18_A3",
        "Q19": "Q19_A3",
    }
    
    balanced_result = evaluator.evaluate(balanced_answers)
    
    print("\n【均衡选手】")
    print(f"基础等级: {balanced_result.base_level:.2f}")
    print(f"维度方差: {balanced_result.dimension_variance:.3f}")
    print(f"均衡度: {balanced_result.balance_factor:.3f}")
    print(f"木桶修正: {balanced_result.barrel_adjusted_level:.2f}")
    print(f"最终等级: {balanced_result.total_level:.2f} → {balanced_result.rounded_level:.1f}")
    
    # 不均衡选手: 同样的基础等级,但方差大
    unbalanced_answers = balanced_answers.copy()
    unbalanced_answers["Q3"] = "Q3_A6"  # 正手很强
    unbalanced_answers["Q4"] = "Q4_A2"  # 反手很弱
    unbalanced_answers["Q5"] = "Q5_A6"  # 发球很强
    unbalanced_answers["Q8"] = "Q8_A2"  # 网前很弱
    
    unbalanced_result = evaluator.evaluate(unbalanced_answers)
    
    print("\n【不均衡选手】")
    print(f"基础等级: {unbalanced_result.base_level:.2f}")
    print(f"维度方差: {unbalanced_result.dimension_variance:.3f}")
    print(f"均衡度: {unbalanced_result.balance_factor:.3f}")
    print(f"木桶修正: {unbalanced_result.barrel_adjusted_level:.2f}")
    print(f"最终等级: {unbalanced_result.total_level:.2f} → {unbalanced_result.rounded_level:.1f}")
    
    print("\n【对比结果】")
    print(f"均衡选手最终等级: {balanced_result.rounded_level:.1f}")
    print(f"不均衡选手最终等级: {unbalanced_result.rounded_level:.1f}")
    print(f"差异: {balanced_result.rounded_level - unbalanced_result.rounded_level:.1f}")


if __name__ == "__main__":
    test_anchor_mechanism()
    test_barrel_effect()
    test_comparison()
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
