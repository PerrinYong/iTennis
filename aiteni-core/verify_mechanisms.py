"""
快速验证新机制是否正常工作
"""

import sys
from pathlib import Path

# 添加src到路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from config_manager import ConfigManager
    from ntrp_evaluator import NTRPEvaluator
    
    print("✓ 模块导入成功")
    
    # 测试配置加载
    config_manager = ConfigManager()
    questions = config_manager.load_questions()
    suggestions = config_manager.load_suggestions()
    
    print(f"✓ 配置加载成功: {len(questions)}个问题")
    
    # 检查anchor_type字段
    anchor_count = {"normal": 0, "locator": 0, "baseline": 0}
    for q in questions:
        for opt in q.options:
            anchor_count[opt.anchor_type] += 1
    
    print(f"✓ Anchor类型统计:")
    print(f"  - normal: {anchor_count['normal']}")
    print(f"  - locator: {anchor_count['locator']}")
    print(f"  - baseline: {anchor_count['baseline']}")
    
    # 测试评估器初始化
    evaluator = NTRPEvaluator(
        questions=questions,
        suggestion_rules=suggestions,
        config_manager=config_manager,
        spread=1.0
    )
    
    print("✓ 评估器初始化成功")
    
    # 测试一个简单的评估
    test_answers = {
        "Q1": "Q1_A3",
        "Q2": "Q2_A3",
        "Q3": "Q3_A3",
        "Q4": "Q4_A3",
        "Q5": "Q5_A3",
        "Q6": "Q6_A3",
        "Q7": "Q7_A3",
        "Q8": "Q8_A3",
        "Q9": "Q9_A3",
        "Q10": "Q10_A3",
        "Q11": "Q11_A2",
        "Q12": "Q12_A2",
        "Q13": "Q13_A2",
        "Q14": "Q14_A2",
        "Q15": "Q15_A2",
        "Q16": "Q16_A2",
        "Q17": "Q17_A2",
        "Q18": "Q18_A2",
        "Q19": "Q19_A2",
    }
    
    result = evaluator.evaluate(test_answers)
    
    print("✓ 评估计算成功")
    print(f"\n评估结果:")
    print(f"  基础等级: {result.base_level:.2f}")
    print(f"  维度平均: {result.dimension_mean:.2f}")
    print(f"  维度方差: {result.dimension_variance:.3f}")
    print(f"  均衡度: {result.balance_factor:.3f}")
    print(f"  木桶修正: {result.barrel_adjusted_level:.2f}")
    print(f"  最终等级: {result.total_level:.2f}")
    print(f"  展示等级: {result.rounded_level:.1f} ({result.level_label})")
    
    print("\n" + "=" * 50)
    print("✓✓✓ 所有验证测试通过! ✓✓✓")
    print("=" * 50)
    
except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
