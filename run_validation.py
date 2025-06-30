#!/usr/bin/env python3
"""
LAMBDA 系统验证运行脚本
提供多种验证模式和选项
"""

import argparse
import sys
import os
from datetime import datetime
import json

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="LAMBDA 对话式数据分析系统验证工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python run_validation.py --mode quick                    # 快速验证
  python run_validation.py --mode full                     # 完整验证
  python run_validation.py --mode full --config custom.yaml  # 使用自定义配置
  python run_validation.py --mode report --input results/  # 基于现有结果生成报告
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['quick', 'full', 'report'],
        default='quick',
        help='验证模式: quick(快速验证), full(完整验证), report(仅生成报告)'
    )
    
    parser.add_argument(
        '--config',
        default='validation_config.yaml',
        help='配置文件路径 (默认: validation_config.yaml)'
    )
    
    parser.add_argument(
        '--output',
        default='validation_results',
        help='输出目录 (默认: validation_results)'
    )
    
    parser.add_argument(
        '--input',
        help='输入结果目录 (仅用于report模式)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='详细输出模式'
    )
    
    parser.add_argument(
        '--no-charts',
        action='store_true',
        help='不生成图表'
    )
    
    args = parser.parse_args()
    
    print("🚀 LAMBDA 系统验证工具")
    print("=" * 50)
    print(f"模式: {args.mode}")
    print(f"输出目录: {args.output}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    try:
        if args.mode == 'quick':
            run_quick_validation(args)
        elif args.mode == 'full':
            run_full_validation(args)
        elif args.mode == 'report':
            generate_report_only(args)
        
        print("\n✅ 验证完成!")
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断验证")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 验证过程中出现错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def run_quick_validation(args):
    """运行快速验证"""
    print("🏃 开始快速验证...")
    
    try:
        from quick_validator import QuickValidator
        
        validator = QuickValidator()
        
        # 修改输出路径
        validator.output_path = args.output
        os.makedirs(validator.output_path, exist_ok=True)
        
        # 运行测试
        results = validator.run_quick_tests()
        
        # 生成报告
        report = validator.generate_quick_report()
        
        print(f"\n📊 快速验证结果:")
        print(f"- 总测试数: {len(results)}")
        print(f"- 成功率: {report['summary']['success_rate']:.1%}")
        print(f"- 平均得分: {report['summary']['average_score']:.1f}/100")
        print(f"- 报告保存至: {validator.output_path}")
        
    except ImportError as e:
        print(f"❌ 无法导入快速验证器: {e}")
        print("请确保所有依赖已安装")

def run_full_validation(args):
    """运行完整验证"""
    print("🔍 开始完整验证...")
    
    try:
        from validation_framework import ValidationFramework
        
        # 检查配置文件
        if not os.path.exists(args.config):
            print(f"⚠️  配置文件不存在: {args.config}")
            print("使用默认配置...")
        
        validator = ValidationFramework(args.config)
        
        # 修改输出路径
        validator.config['output_path'] = args.output
        os.makedirs(validator.config['output_path'], exist_ok=True)
        
        # 运行完整测试
        print("📝 运行测试用例...")
        results = validator.run_all_tests()
        
        # 生成评估报告
        print("📊 生成评估报告...")
        report = validator.generate_evaluation_report()
        
        # 生成可视化（如果不禁用）
        if not args.no_charts:
            print("📈 生成可视化图表...")
            validator.visualize_results()
        
        print(f"\n📊 完整验证结果:")
        print(f"- 总测试数: {len(results)}")
        if report:
            print(f"- 成功率: {report['summary']['success_rate']:.1%}")
            print(f"- 平均得分: {report['summary']['average_score']:.1f}/100")
        print(f"- 报告保存至: {validator.config['output_path']}")
        
    except ImportError as e:
        print(f"❌ 无法导入完整验证框架: {e}")
        print("请确保所有依赖已安装")
    except Exception as e:
        print(f"❌ 完整验证失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()

def generate_report_only(args):
    """仅生成报告"""
    print("📊 生成报告模式...")
    
    if not args.input:
        print("❌ 报告模式需要指定输入目录 (--input)")
        return
    
    if not os.path.exists(args.input):
        print(f"❌ 输入目录不存在: {args.input}")
        return
    
    try:
        # 查找结果文件
        results_file = None
        for filename in ['evaluation_report.json', 'quick_validation_report.json', 'intermediate_results.json']:
            filepath = os.path.join(args.input, filename)
            if os.path.exists(filepath):
                results_file = filepath
                break
        
        if not results_file:
            print(f"❌ 在 {args.input} 中未找到结果文件")
            return
        
        print(f"📂 读取结果文件: {results_file}")
        
        with open(results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 创建输出目录
        os.makedirs(args.output, exist_ok=True)
        
        # 生成新的报告
        if 'detailed_results' in data:
            results = data['detailed_results']
        elif 'test_results' in data:
            results = data['test_results']
        else:
            print("❌ 无法从结果文件中提取测试结果")
            return
        
        # 使用评估指标模块生成详细报告
        from evaluation_metrics import EvaluationMetrics
        
        evaluator = EvaluationMetrics()
        summary = evaluator.generate_performance_summary(results)
        
        # 保存新报告
        report_file = os.path.join(args.output, 'regenerated_report.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        # 生成可视化
        if not args.no_charts:
            chart_file = os.path.join(args.output, 'metrics_visualization.png')
            evaluator.visualize_metrics(results, chart_file)
        
        print(f"✅ 报告已生成至: {args.output}")
        
    except Exception as e:
        print(f"❌ 生成报告失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()

def check_dependencies():
    """检查依赖"""
    required_packages = [
        'pandas', 'numpy', 'matplotlib', 'seaborn', 
        'scikit-learn', 'yaml', 'jupyter_client'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n请使用以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

if __name__ == "__main__":
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    main()