"""
NTRP 网球等级评估系统 Demo

这是一个网球等级评估系统的演示程序，基于多维度模糊评分机制。
"""

import sys
import pathlib
import json
from typing import Dict, List

# 添加当前目录到路径，确保可以导入 ntrp_evaluator
current_dir = pathlib.Path(__file__).parent
sys.path.insert(0, str(current_dir))

from ntrp_evaluator import NTRPEvaluator, EvaluateResult


def load_demo_answers() -> List[Dict[str, str]]:
    """加载几个不同水平的演示答案"""
    return [
        {
            "name": "初级选手示例",
            "answers": {
                "Q1": "Q1_A1",    # 很难连续超过3拍
                "Q2": "Q2_A1",    # 多数球都落在发球线附近
                "Q3": "Q3_A1",    # 正手动作不完整
                "Q4": "Q4_A1",    # 基本不敢用反手
                "Q5": "Q5_A1",    # 经常双误
                "Q6": "Q6_A1",    # 基本只求发进去
                "Q7": "Q7_A1",    # 对快球容易慌
                "Q8": "Q8_A1",    # 基本不主动上网
                "Q9": "Q9_A1",    # 跑不到位
                "Q10": "Q10_A1",  # 只把球打回去
                "Q11": "Q11_A1",  # 很难拿到2局以上
                "Q12": "Q12_A1",  # 打得不多
            }
        },
        {
            "name": "中级选手示例",
            "answers": {
                "Q1": "Q1_A3",    # 经常能打到6-10拍
                "Q2": "Q2_A3",    # 能打到中后场
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
            "answers": {
                "Q1": "Q1_A5",    # 中速对拉失误很少
                "Q2": "Q2_A5",    # 能有意识压在对手底线
                "Q3": "Q3_A5",    # 正手能主动压制对手
                "Q4": "Q4_A5",    # 反手能打出上旋或切削
                "Q5": "Q5_A5",    # 发球能针对对手弱点
                "Q6": "Q6_A5",    # 能通过组合变化发球
                "Q7": "Q7_A5",    # 接发经常给压力
                "Q8": "Q8_A5",    # 能在合适时机上网
                "Q9": "Q9_A5",    # 能保持良好击球点
                "Q10": "Q10_A5",  # 能根据比分调整打法
                "Q11": "Q11_A4",  # 经常能打到5:7、6:4
                "Q12": "Q12_A4",  # 每周3次或以上
            }
        }
    ]


def interactive_evaluation(evaluator: NTRPEvaluator) -> None:
    """交互式评估模式"""
    print("\n=== 交互式 NTRP 评估 ===")
    print("请根据你的实际情况回答以下问题（输入选项编号）：\n")
    
    user_answers = {}
    
    for i, question in enumerate(evaluator.questions, 1):
        print(f"问题 {i}: {question.text}")
        print()
        
        for j, option in enumerate(question.options, 1):
            print(f"  {j}. {option.text}")
        print()
        
        while True:
            try:
                choice = input(f"请选择 1-{len(question.options)}: ").strip()
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(question.options):
                    selected_option = question.options[choice_idx]
                    user_answers[question.id] = selected_option.id
                    print(f"你选择了: {selected_option.text}\n")
                    break
                else:
                    print(f"请输入 1-{len(question.options)} 之间的数字")
            except ValueError:
                print("请输入有效的数字")
            except KeyboardInterrupt:
                print("\n\n用户取消了评估。")
                return
    
    # 执行评估
    print("正在分析你的答案...")
    result = evaluator.evaluate(user_answers)
    display_result("你的评估结果", result)


def display_result(name: str, result: EvaluateResult) -> None:
    """显示评估结果"""
    print(f"\n{'='*50}")
    print(f"  {name}")
    print(f"{'='*50}")
    
    print(f"\n🎾 总体等级: NTRP {result.rounded_level:.1f} ({result.level_label})")
    print(f"原始得分: {result.total_level:.2f}")
    
    print(f"\n📊 各维度得分:")
    for dim, score in result.dimension_scores.items():
        dim_name = NTRPEvaluator.DIMENSION_META.get(dim, dim)
        print(f"  • {dim_name}: {score:.1f}")
    
    print(f"\n💪 主要优势: {', '.join([NTRPEvaluator.DIMENSION_META.get(d, d) for d in result.advantages[:3]])}")
    print(f"🎯 提升重点: {', '.join([NTRPEvaluator.DIMENSION_META.get(d, d) for d in result.weaknesses[:3]])}")
    
    # 展示图表数据
    if result.chart_data:
        print(f"\n{'='*50}")
        print("  📈 图表数据详情")
        print(f"{'='*50}")
        
        # 雷达图数据
        radar = result.chart_data.radar_data
        print(f"\n🎯 雷达图数据（核心技术维度）:")
        for i, (dim, label, score) in enumerate(zip(radar.dimensions, radar.dimension_labels, radar.scores)):
            print(f"  {label}: {score:.1f}% (原始: {result.dimension_scores[dim]:.1f}级)")
        
        # 分组条形图数据
        print(f"\n📊 分组条形图数据:")
        for group in result.chart_data.bar_groups:
            print(f"\n  【{group.group_name}】")
            for dim_data in group.dimensions:
                tag_emoji = {"优势": "🟢", "均衡": "🟡", "短板": "🔴"}[dim_data.tag.value]
                print(f"    {dim_data.label}: {dim_data.score:.1f}级 ({dim_data.normalized_score:.0f}%) {tag_emoji}")
                if dim_data.short_comment:
                    print(f"      💬 {dim_data.short_comment}")
        
        # 训练优先级
        if result.chart_data.priority_list:
            print(f"\n🏃‍♂️ 训练优先级建议:")
            priority_emojis = ["🥇", "🥈", "🥉"]
            for item in result.chart_data.priority_list:
                emoji = priority_emojis[item.rank - 1] if item.rank <= 3 else "🏅"
                print(f"  {emoji} 第{item.rank}位: {item.label}")
                print(f"      📉 差距: {item.gap:.1f}级 ({item.normalized_gap:.0f}%)")
                print(f"      📚 建议: {item.suggestion}")
        else:
            print(f"\n🎉 各维度发展均衡，可以全面提升！")
    
    print(f"\n📝 详细评语:")
    print("-" * 40)
    print(result.summary_text)
    print("-" * 40)


def demo_evaluation(evaluator: NTRPEvaluator) -> None:
    """演示模式 - 展示不同水平的评估结果"""
    print("\n=== 演示模式：不同水平选手的评估结果 ===\n")
    
    demo_cases = load_demo_answers()
    
    for case in demo_cases:
        result = evaluator.evaluate(case["answers"])
        display_result(case["name"], result)
        print()


def main():
    """主程序入口"""
    print("🎾 NTRP 网球等级评估系统")
    print("基于多维度模糊评分机制，为你提供科学的网球水平评估")
    
    # 加载配置文件
    try:
        config_dir = pathlib.Path(__file__).parent.parent / "config"
        questions = NTRPEvaluator.load_questions(config_dir / "questions.json")
        suggestions = NTRPEvaluator.load_suggestions(config_dir / "dimension_suggestions.json")
        evaluator = NTRPEvaluator(questions, suggestions, spread=1.0)
        print(f"✅ 成功加载 {len(questions)} 个问题和评语规则")
        
    except FileNotFoundError as e:
        print(f"❌ 配置文件加载失败: {e}")
        print("请确保 config/questions.json 和 config/dimension_suggestions.json 文件存在")
        return
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    while True:
        print("\n请选择运行模式:")
        print("1. 交互式评估 (根据你的情况回答问题)")
        print("2. 演示模式 (查看不同水平的评估示例)")
        print("3. 退出")
        
        try:
            choice = input("\n请选择 (1-3): ").strip()
            
            if choice == "1":
                interactive_evaluation(evaluator)
            elif choice == "2":
                demo_evaluation(evaluator)
            elif choice == "3":
                print("感谢使用 NTRP 评估系统！")
                break
            else:
                print("请输入 1、2 或 3")
                
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"运行出错: {e}")


if __name__ == "__main__":
    main()
    
    