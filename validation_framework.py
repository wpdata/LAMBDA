#!/usr/bin/env python3
"""
LAMBDA 对话式数据分析系统验证框架
用于评估系统准确性和性能的综合测试程序
"""

import os
import sys
import json
import time
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_iris, load_boston, make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# 导入 LAMBDA 系统组件
from conversation import Conversation
from app import app
import yaml

class ValidationFramework:
    """LAMBDA 系统验证框架"""
    
    def __init__(self, config_path='validation_config.yaml'):
        """初始化验证框架"""
        self.config = self.load_config(config_path)
        self.results = []
        self.test_cases = []
        self.setup_test_environment()
        
    def load_config(self, config_path):
        """加载验证配置"""
        default_config = {
            'test_data_path': 'validation_data/',
            'output_path': 'validation_results/',
            'timeout': 300,  # 5分钟超时
            'lambda_config': 'config.yaml'
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
                default_config.update(config)
        
        return default_config
    
    def setup_test_environment(self):
        """设置测试环境"""
        # 创建测试数据目录
        os.makedirs(self.config['test_data_path'], exist_ok=True)
        os.makedirs(self.config['output_path'], exist_ok=True)
        
        # 生成测试数据
        self.generate_test_datasets()
        
        # 初始化 LAMBDA 应用
        try:
            self.lambda_app = app(self.config['lambda_config'])
        except Exception as e:
            print(f"警告：无法初始化 LAMBDA 应用: {e}")
            self.lambda_app = None
    
    def generate_test_datasets(self):
        """生成测试数据集"""
        datasets = {}
        
        # 1. 基础数值数据集
        np.random.seed(42)
        basic_data = pd.DataFrame({
            'A': np.random.normal(50, 10, 100),
            'B': np.random.normal(30, 5, 100),
            'C': np.random.choice(['Type1', 'Type2', 'Type3'], 100),
            'D': pd.date_range('2023-01-01', periods=100, freq='D')
        })
        datasets['basic_data.csv'] = basic_data
        
        # 2. 鸢尾花数据集
        iris = load_iris()
        iris_df = pd.DataFrame(iris.data, columns=iris.feature_names)
        iris_df['target'] = iris.target
        iris_df['species'] = iris_df['target'].map({0: 'setosa', 1: 'versicolor', 2: 'virginica'})
        datasets['iris.csv'] = iris_df
        
        # 3. 带缺失值的数据集
        missing_data = pd.DataFrame({
            'feature1': [1, 2, np.nan, 4, 5, np.nan, 7, 8, 9, 10],
            'feature2': [10, np.nan, 30, 40, np.nan, 60, 70, 80, 90, 100],
            'category': ['A', 'B', 'A', np.nan, 'C', 'B', 'A', 'C', 'B', 'A']
        })
        datasets['missing_data.csv'] = missing_data
        
        # 4. 时间序列数据
        dates = pd.date_range('2023-01-01', periods=365, freq='D')
        ts_data = pd.DataFrame({
            'date': dates,
            'value': np.sin(np.arange(365) * 2 * np.pi / 365) + np.random.normal(0, 0.1, 365),
            'trend': np.arange(365) * 0.01 + np.random.normal(0, 0.05, 365)
        })
        datasets['timeseries.csv'] = ts_data
        
        # 保存数据集
        for filename, data in datasets.items():
            data.to_csv(os.path.join(self.config['test_data_path'], filename), index=False)
        
        print(f"生成了 {len(datasets)} 个测试数据集")
    
    def define_test_cases(self):
        """定义测试用例"""
        test_cases = [
            # 基础统计分析测试
            {
                'name': '基础统计描述',
                'dataset': 'basic_data.csv',
                'query': '请分析这个数据集的基本统计信息，包括数值变量的均值、标准差、分布情况',
                'expected_operations': ['describe', 'mean', 'std'],
                'category': 'statistics'
            },
            {
                'name': '相关性分析',
                'dataset': 'basic_data.csv',
                'query': '分析数值变量之间的相关性，并生成相关性热力图',
                'expected_operations': ['corr', 'heatmap'],
                'category': 'statistics'
            },
            
            # 数据可视化测试
            {
                'name': '分布图生成',
                'dataset': 'iris.csv',
                'query': '为每个数值特征生成分布图，并按物种分组显示',
                'expected_operations': ['hist', 'boxplot', 'groupby'],
                'category': 'visualization'
            },
            {
                'name': '散点图矩阵',
                'dataset': 'iris.csv',
                'query': '创建所有数值特征的散点图矩阵，按物种着色',
                'expected_operations': ['scatter_matrix', 'pairplot'],
                'category': 'visualization'
            },
            
            # 数据预处理测试
            {
                'name': '缺失值处理',
                'dataset': 'missing_data.csv',
                'query': '检测并处理数据中的缺失值，展示处理前后的数据质量',
                'expected_operations': ['isnull', 'fillna', 'dropna'],
                'category': 'preprocessing'
            },
            
            # 机器学习测试
            {
                'name': '分类模型训练',
                'dataset': 'iris.csv',
                'query': '使用随机森林算法训练一个分类模型预测鸢尾花物种，并评估模型性能',
                'expected_operations': ['RandomForestClassifier', 'train_test_split', 'accuracy_score'],
                'category': 'machine_learning'
            },
            
            # 时间序列分析测试
            {
                'name': '时间序列分析',
                'dataset': 'timeseries.csv',
                'query': '分析时间序列数据的趋势和季节性模式，生成时间序列图',
                'expected_operations': ['plot', 'rolling', 'trend'],
                'category': 'timeseries'
            },
            
            # 高级分析测试
            {
                'name': '聚类分析',
                'dataset': 'iris.csv',
                'query': '对鸢尾花数据进行K-means聚类分析，确定最优聚类数量',
                'expected_operations': ['KMeans', 'elbow_method', 'silhouette_score'],
                'category': 'advanced'
            }
        ]
        
        self.test_cases = test_cases
        return test_cases
    
    def execute_test_case(self, test_case: Dict) -> Dict:
        """执行单个测试用例"""
        print(f"\n执行测试: {test_case['name']}")
        print(f"数据集: {test_case['dataset']}")
        print(f"查询: {test_case['query']}")
        
        result = {
            'test_name': test_case['name'],
            'dataset': test_case['dataset'],
            'query': test_case['query'],
            'category': test_case['category'],
            'start_time': datetime.now(),
            'success': False,
            'execution_time': 0,
            'error_message': None,
            'code_generated': None,
            'code_executed': False,
            'output_generated': False,
            'expected_operations_found': [],
            'score': 0
        }
        
        try:
            start_time = time.time()
            
            if self.lambda_app is None:
                result['error_message'] = "LAMBDA 应用未初始化"
                return result
            
            # 上传测试数据
            dataset_path = os.path.join(self.config['test_data_path'], test_case['dataset'])
            if not os.path.exists(dataset_path):
                result['error_message'] = f"测试数据集不存在: {dataset_path}"
                return result
            
            # 模拟文件上传
            class MockFile:
                def __init__(self, path):
                    self.name = path
            
            mock_file = MockFile(dataset_path)
            self.lambda_app.add_file(mock_file)
            
            # 执行查询
            chat_history = []
            final_response = None
            
            # 模拟对话流程
            for response in self.lambda_app.conv.stream_workflow(
                chat_history=[[test_case['query'], None]], 
                code=None
            ):
                chat_history = response
                if response and len(response) > 0 and response[-1][1]:
                    final_response = response[-1][1]
            
            result['execution_time'] = time.time() - start_time
            
            if final_response:
                result['success'] = True
                result['code_generated'] = self.extract_code_from_response(final_response)
                result['output_generated'] = len(final_response) > 100  # 简单的输出质量指标
                
                # 检查是否包含期望的操作
                expected_ops = test_case.get('expected_operations', [])
                found_ops = []
                for op in expected_ops:
                    if op.lower() in final_response.lower():
                        found_ops.append(op)
                result['expected_operations_found'] = found_ops
                
                # 计算得分
                result['score'] = self.calculate_test_score(result, test_case)
            
            result['end_time'] = datetime.now()
            
        except Exception as e:
            result['error_message'] = str(e)
            result['execution_time'] = time.time() - start_time
            result['end_time'] = datetime.now()
        
        return result
    
    def extract_code_from_response(self, response: str) -> Optional[str]:
        """从响应中提取代码"""
        import re
        code_pattern = r'```python\n(.*?)\n```'
        matches = re.findall(code_pattern, response, re.DOTALL)
        if matches:
            return matches[-1]  # 返回最后一个代码块
        return None
    
    def calculate_test_score(self, result: Dict, test_case: Dict) -> float:
        """计算测试得分"""
        score = 0.0
        
        # 基础分数：成功执行
        if result['success']:
            score += 30
        
        # 代码生成分数
        if result['code_generated']:
            score += 20
        
        # 输出质量分数
        if result['output_generated']:
            score += 20
        
        # 期望操作命中率
        expected_ops = test_case.get('expected_operations', [])
        if expected_ops:
            hit_rate = len(result['expected_operations_found']) / len(expected_ops)
            score += hit_rate * 30
        
        return min(score, 100)  # 限制在100分以内
    
    def run_all_tests(self) -> List[Dict]:
        """运行所有测试用例"""
        print("开始运行验证测试...")
        test_cases = self.define_test_cases()
        
        for i, test_case in enumerate(test_cases):
            print(f"\n进度: {i+1}/{len(test_cases)}")
            result = self.execute_test_case(test_case)
            self.results.append(result)
            
            # 保存中间结果
            self.save_intermediate_results()
        
        print("\n所有测试完成")
        return self.results
    
    def save_intermediate_results(self):
        """保存中间结果"""
        results_file = os.path.join(self.config['output_path'], 'intermediate_results.json')
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2, default=str)
    
    def generate_evaluation_report(self) -> Dict:
        """生成评估报告"""
        if not self.results:
            print("没有测试结果可用于生成报告")
            return {}
        
        report = {
            'summary': self.generate_summary_statistics(),
            'category_analysis': self.analyze_by_category(),
            'detailed_results': self.results,
            'recommendations': self.generate_recommendations()
        }
        
        # 保存报告
        report_file = os.path.join(self.config['output_path'], 'evaluation_report.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        # 生成可读性报告
        self.generate_readable_report(report)
        
        return report
    
    def generate_summary_statistics(self) -> Dict:
        """生成摘要统计"""
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r['success'])
        
        scores = [r['score'] for r in self.results if r['score'] > 0]
        avg_score = np.mean(scores) if scores else 0
        
        execution_times = [r['execution_time'] for r in self.results]
        avg_execution_time = np.mean(execution_times) if execution_times else 0
        
        return {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': successful_tests / total_tests if total_tests > 0 else 0,
            'average_score': avg_score,
            'average_execution_time': avg_execution_time,
            'code_generation_rate': sum(1 for r in self.results if r['code_generated']) / total_tests if total_tests > 0 else 0
        }
    
    def analyze_by_category(self) -> Dict:
        """按类别分析结果"""
        categories = {}
        
        for result in self.results:
            category = result['category']
            if category not in categories:
                categories[category] = {
                    'total': 0,
                    'successful': 0,
                    'scores': [],
                    'execution_times': []
                }
            
            categories[category]['total'] += 1
            if result['success']:
                categories[category]['successful'] += 1
            categories[category]['scores'].append(result['score'])
            categories[category]['execution_times'].append(result['execution_time'])
        
        # 计算各类别统计
        for category, stats in categories.items():
            stats['success_rate'] = stats['successful'] / stats['total'] if stats['total'] > 0 else 0
            stats['average_score'] = np.mean(stats['scores']) if stats['scores'] else 0
            stats['average_execution_time'] = np.mean(stats['execution_times']) if stats['execution_times'] else 0
        
        return categories
    
    def generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        summary = self.generate_summary_statistics()
        
        if summary['success_rate'] < 0.8:
            recommendations.append("系统整体成功率较低，需要提升系统稳定性和错误处理能力")
        
        if summary['average_score'] < 70:
            recommendations.append("平均得分较低，需要改进代码生成质量和输出准确性")
        
        if summary['code_generation_rate'] < 0.9:
            recommendations.append("代码生成率需要提升，建议优化代码提取和执行逻辑")
        
        if summary['average_execution_time'] > 60:
            recommendations.append("平均执行时间较长，建议优化响应速度")
        
        # 按类别分析问题
        categories = self.analyze_by_category()
        for category, stats in categories.items():
            if stats['success_rate'] < 0.7:
                recommendations.append(f"{category} 类别任务成功率较低，需要专门优化")
        
        if not recommendations:
            recommendations.append("系统表现良好，继续保持当前水平")
        
        return recommendations
    
    def generate_readable_report(self, report: Dict):
        """生成可读性报告"""
        report_content = f"""
# LAMBDA 系统验证报告

## 生成时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 执行摘要

### 总体统计
- 总测试数量: {report['summary']['total_tests']}
- 成功测试数量: {report['summary']['successful_tests']}
- 成功率: {report['summary']['success_rate']:.2%}
- 平均得分: {report['summary']['average_score']:.2f}/100
- 平均执行时间: {report['summary']['average_execution_time']:.2f}秒
- 代码生成率: {report['summary']['code_generation_rate']:.2%}

### 按类别分析
"""
        
        for category, stats in report['category_analysis'].items():
            report_content += f"""
#### {category.upper()} 类别
- 成功率: {stats['success_rate']:.2%}
- 平均得分: {stats['average_score']:.2f}
- 平均执行时间: {stats['average_execution_time']:.2f}秒
"""
        
        report_content += f"""
## 详细测试结果

"""
        
        for result in report['detailed_results']:
            status = "✅ 成功" if result['success'] else "❌ 失败"
            report_content += f"""
### {result['test_name']} {status}
- 数据集: {result['dataset']}
- 类别: {result['category']}
- 得分: {result['score']:.2f}/100
- 执行时间: {result['execution_time']:.2f}秒
- 代码生成: {'是' if result['code_generated'] else '否'}
"""
            if result['error_message']:
                report_content += f"- 错误信息: {result['error_message']}\n"
            
            if result['expected_operations_found']:
                report_content += f"- 匹配的操作: {', '.join(result['expected_operations_found'])}\n"
        
        report_content += f"""
## 改进建议

"""
        for i, rec in enumerate(report['recommendations'], 1):
            report_content += f"{i}. {rec}\n"
        
        # 保存可读性报告
        report_file = os.path.join(self.config['output_path'], 'validation_report.md')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"验证报告已保存至: {report_file}")
    
    def visualize_results(self):
        """可视化测试结果"""
        if not self.results:
            print("没有结果可供可视化")
            return
        
        # 创建可视化图表
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. 成功率饼图
        success_counts = [sum(1 for r in self.results if r['success']),
                         sum(1 for r in self.results if not r['success'])]
        axes[0, 0].pie(success_counts, labels=['成功', '失败'], autopct='%1.1f%%')
        axes[0, 0].set_title('测试成功率')
        
        # 2. 得分分布直方图
        scores = [r['score'] for r in self.results]
        axes[0, 1].hist(scores, bins=10, alpha=0.7)
        axes[0, 1].set_xlabel('得分')
        axes[0, 1].set_ylabel('频数')
        axes[0, 1].set_title('得分分布')
        
        # 3. 按类别的成功率
        categories = self.analyze_by_category()
        cat_names = list(categories.keys())
        success_rates = [categories[cat]['success_rate'] for cat in cat_names]
        axes[1, 0].bar(cat_names, success_rates)
        axes[1, 0].set_ylabel('成功率')
        axes[1, 0].set_title('各类别成功率')
        plt.setp(axes[1, 0].get_xticklabels(), rotation=45)
        
        # 4. 执行时间分布
        exec_times = [r['execution_time'] for r in self.results]
        axes[1, 1].boxplot(exec_times)
        axes[1, 1].set_ylabel('执行时间(秒)')
        axes[1, 1].set_title('执行时间分布')
        
        plt.tight_layout()
        
        # 保存图表
        chart_file = os.path.join(self.config['output_path'], 'validation_charts.png')
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"可视化图表已保存至: {chart_file}")

def main():
    """主函数"""
    print("LAMBDA 系统验证程序")
    print("=" * 50)
    
    # 创建验证框架
    validator = ValidationFramework()
    
    # 运行测试
    results = validator.run_all_tests()
    
    # 生成报告
    report = validator.generate_evaluation_report()
    
    # 生成可视化
    validator.visualize_results()
    
    print("\n验证完成！")
    print(f"总测试数量: {len(results)}")
    print(f"成功测试数量: {sum(1 for r in results if r['success'])}")
    print(f"平均得分: {np.mean([r['score'] for r in results]):.2f}")

if __name__ == "__main__":
    main()