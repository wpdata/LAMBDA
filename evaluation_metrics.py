#!/usr/bin/env python3
"""
LAMBDA 系统评估指标模块
定义各种评估指标和计算方法
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import matplotlib.pyplot as plt
import seaborn as sns

class EvaluationMetrics:
    """评估指标计算器"""
    
    def __init__(self):
        """初始化评估指标"""
        self.metrics = {}
    
    def calculate_code_quality_score(self, code: str) -> Dict[str, float]:
        """计算代码质量得分"""
        if not code:
            return {'syntax_score': 0, 'complexity_score': 0, 'best_practices_score': 0}
        
        scores = {}
        
        # 1. 语法正确性（简单检查）
        syntax_score = self._check_syntax_quality(code)
        scores['syntax_score'] = syntax_score
        
        # 2. 代码复杂度
        complexity_score = self._calculate_complexity_score(code)
        scores['complexity_score'] = complexity_score
        
        # 3. 最佳实践
        best_practices_score = self._check_best_practices(code)
        scores['best_practices_score'] = best_practices_score
        
        # 总体代码质量得分
        scores['overall_code_quality'] = np.mean(list(scores.values()))
        
        return scores
    
    def _check_syntax_quality(self, code: str) -> float:
        """检查语法质量"""
        score = 100.0
        
        # 检查常见语法问题
        issues = [
            (r'^\s*import\s', 10),  # 缺少导入语句
            (r'print\s*\(', 5),     # 有print语句（好的调试习惯）
            (r'#.*', 5),            # 有注释
            (r'def\s+\w+\s*\(', 10), # 有函数定义
            (r'pd\.|np\.|plt\.', 15) # 使用了常见数据科学库
        ]
        
        for pattern, bonus in issues:
            if re.search(pattern, code, re.MULTILINE):
                score += bonus
        
        # 检查不好的实践
        bad_practices = [
            (r'exec\s*\(', -20),    # 使用exec
            (r'eval\s*\(', -20),    # 使用eval
            (r'import\s+\*', -10),  # 使用import *
        ]
        
        for pattern, penalty in bad_practices:
            if re.search(pattern, code):
                score += penalty
        
        return max(0, min(100, score))
    
    def _calculate_complexity_score(self, code: str) -> float:
        """计算复杂度得分"""
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # 基于代码行数的复杂度
        line_count = len(non_empty_lines)
        
        if line_count <= 10:
            complexity_score = 100
        elif line_count <= 30:
            complexity_score = 80
        elif line_count <= 50:
            complexity_score = 60
        else:
            complexity_score = 40
        
        # 检查嵌套层次
        max_indent = 0
        for line in non_empty_lines:
            indent = len(line) - len(line.lstrip())
            max_indent = max(max_indent, indent)
        
        # 嵌套层次过深会降低得分
        if max_indent > 16:  # 超过4层嵌套
            complexity_score -= 20
        elif max_indent > 12:  # 超过3层嵌套
            complexity_score -= 10
        
        return max(0, complexity_score)
    
    def _check_best_practices(self, code: str) -> float:
        """检查最佳实践"""
        score = 50.0  # 基础分数
        
        best_practices = [
            (r'^\s*#.*', 10),       # 有注释
            (r'pd\.read_csv\(', 15), # 正确读取数据
            (r'plt\.show\(\)', 10),  # 显示图表
            (r'\.describe\(\)', 10), # 使用describe方法
            (r'\.head\(\)', 5),      # 查看数据头部
            (r'\.info\(\)', 5),      # 查看数据信息
            (r'try:', 15),          # 使用异常处理
            (r'\.fillna\(', 10),    # 处理缺失值
        ]
        
        for pattern, bonus in best_practices:
            if re.search(pattern, code, re.MULTILINE):
                score += bonus
        
        return min(100, score)
    
    def calculate_accuracy_metrics(self, expected_results: List[Any], 
                                 actual_results: List[Any]) -> Dict[str, float]:
        """计算准确性指标"""
        if not expected_results or not actual_results:
            return {'accuracy': 0.0}
        
        # 简单的匹配计算
        matches = sum(1 for exp, act in zip(expected_results, actual_results) 
                     if self._results_match(exp, act))
        
        accuracy = matches / len(expected_results) if expected_results else 0
        
        return {
            'accuracy': accuracy,
            'total_expected': len(expected_results),
            'total_actual': len(actual_results),
            'matches': matches
        }
    
    def _results_match(self, expected: Any, actual: Any) -> bool:
        """判断结果是否匹配"""
        # 这里可以实现更复杂的匹配逻辑
        if isinstance(expected, str) and isinstance(actual, str):
            return expected.lower().strip() == actual.lower().strip()
        elif isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            return abs(expected - actual) < 1e-6
        else:
            return str(expected) == str(actual)
    
    def calculate_response_quality(self, response: str, query: str) -> Dict[str, float]:
        """计算响应质量"""
        scores = {}
        
        # 1. 响应长度合理性
        length_score = self._evaluate_response_length(response)
        scores['length_score'] = length_score
        
        # 2. 相关性得分
        relevance_score = self._calculate_relevance_score(response, query)
        scores['relevance_score'] = relevance_score
        
        # 3. 完整性得分
        completeness_score = self._evaluate_completeness(response, query)
        scores['completeness_score'] = completeness_score
        
        # 4. 清晰度得分
        clarity_score = self._evaluate_clarity(response)
        scores['clarity_score'] = clarity_score
        
        # 总体响应质量
        scores['overall_response_quality'] = np.mean(list(scores.values()))
        
        return scores
    
    def _evaluate_response_length(self, response: str) -> float:
        """评估响应长度合理性"""
        if not response:
            return 0
        
        length = len(response)
        
        if 50 <= length <= 2000:  # 合理长度
            return 100
        elif length < 50:  # 太短
            return max(0, length * 2)  # 按长度线性评分
        else:  # 太长
            return max(20, 100 - (length - 2000) / 50)
    
    def _calculate_relevance_score(self, response: str, query: str) -> float:
        """计算相关性得分"""
        if not response or not query:
            return 0
        
        # 提取查询中的关键词
        query_words = set(re.findall(r'\w+', query.lower()))
        response_words = set(re.findall(r'\w+', response.lower()))
        
        # 计算关键词重叠度
        overlap = len(query_words.intersection(response_words))
        relevance = overlap / len(query_words) if query_words else 0
        
        return min(100, relevance * 150)  # 放大相关性得分
    
    def _evaluate_completeness(self, response: str, query: str) -> float:
        """评估完整性"""
        # 检查是否包含代码块
        has_code = '```' in response or 'import ' in response
        
        # 检查是否有解释
        has_explanation = len(response.split()) > 20
        
        # 检查是否有结果
        has_results = any(keyword in response.lower() 
                         for keyword in ['结果', '输出', '图', 'result', 'output'])
        
        completeness_factors = [has_code, has_explanation, has_results]
        return (sum(completeness_factors) / len(completeness_factors)) * 100
    
    def _evaluate_clarity(self, response: str) -> float:
        """评估清晰度"""
        if not response:
            return 0
        
        # 基础清晰度指标
        sentences = response.split('.')
        avg_sentence_length = np.mean([len(s.split()) for s in sentences if s.strip()])
        
        # 合理的句子长度得分
        if 5 <= avg_sentence_length <= 25:
            length_score = 100
        else:
            length_score = max(0, 100 - abs(avg_sentence_length - 15) * 3)
        
        # 检查是否有结构化内容
        has_structure = any(marker in response for marker in ['##', '1.', '2.', '- ', '* '])
        structure_score = 100 if has_structure else 70
        
        return (length_score + structure_score) / 2
    
    def calculate_execution_metrics(self, execution_times: List[float]) -> Dict[str, float]:
        """计算执行指标"""
        if not execution_times:
            return {}
        
        return {
            'avg_execution_time': np.mean(execution_times),
            'median_execution_time': np.median(execution_times),
            'min_execution_time': np.min(execution_times),
            'max_execution_time': np.max(execution_times),
            'std_execution_time': np.std(execution_times),
            'total_execution_time': np.sum(execution_times)
        }
    
    def calculate_reliability_metrics(self, results: List[Dict]) -> Dict[str, float]:
        """计算可靠性指标"""
        if not results:
            return {}
        
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.get('success', False))
        failed_tests = total_tests - successful_tests
        
        # 按类别分析成功率
        category_success = {}
        for result in results:
            category = result.get('category', 'unknown')
            if category not in category_success:
                category_success[category] = {'total': 0, 'success': 0}
            
            category_success[category]['total'] += 1
            if result.get('success', False):
                category_success[category]['success'] += 1
        
        # 计算各类别成功率
        category_rates = {}
        for category, stats in category_success.items():
            category_rates[category] = stats['success'] / stats['total'] if stats['total'] > 0 else 0
        
        return {
            'overall_success_rate': successful_tests / total_tests,
            'failure_rate': failed_tests / total_tests,
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'failed_tests': failed_tests,
            'category_success_rates': category_rates,
            'reliability_score': (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        }
    
    def generate_performance_summary(self, results: List[Dict]) -> Dict[str, Any]:
        """生成性能摘要"""
        if not results:
            return {}
        
        # 收集各种指标
        execution_times = [r.get('execution_time', 0) for r in results]
        scores = [r.get('score', 0) for r in results]
        
        execution_metrics = self.calculate_execution_metrics(execution_times)
        reliability_metrics = self.calculate_reliability_metrics(results)
        
        # 代码质量分析
        code_quality_scores = []
        for result in results:
            if result.get('code_generated'):
                # 这里应该传入实际的代码，但为演示目的使用模拟数据
                code_quality = self.calculate_code_quality_score(result.get('code_generated', ''))
                code_quality_scores.append(code_quality.get('overall_code_quality', 0))
        
        summary = {
            'execution_metrics': execution_metrics,
            'reliability_metrics': reliability_metrics,
            'score_statistics': {
                'mean_score': np.mean(scores),
                'median_score': np.median(scores),
                'std_score': np.std(scores),
                'min_score': np.min(scores),
                'max_score': np.max(scores)
            },
            'code_quality_statistics': {
                'mean_quality': np.mean(code_quality_scores) if code_quality_scores else 0,
                'median_quality': np.median(code_quality_scores) if code_quality_scores else 0,
                'total_code_generated': len(code_quality_scores)
            },
            'performance_grade': self._calculate_performance_grade(reliability_metrics, np.mean(scores))
        }
        
        return summary
    
    def _calculate_performance_grade(self, reliability_metrics: Dict, avg_score: float) -> str:
        """计算性能等级"""
        success_rate = reliability_metrics.get('overall_success_rate', 0)
        
        if success_rate >= 0.95 and avg_score >= 90:
            return 'A+'
        elif success_rate >= 0.9 and avg_score >= 85:
            return 'A'
        elif success_rate >= 0.85 and avg_score >= 80:
            return 'A-'
        elif success_rate >= 0.8 and avg_score >= 75:
            return 'B+'
        elif success_rate >= 0.75 and avg_score >= 70:
            return 'B'
        elif success_rate >= 0.7 and avg_score >= 65:
            return 'B-'
        elif success_rate >= 0.6 and avg_score >= 60:
            return 'C'
        else:
            return 'D'
    
    def visualize_metrics(self, results: List[Dict], output_path: str = None):
        """可视化指标"""
        if not results:
            return
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # 1. 成功率分布
        success_counts = [sum(1 for r in results if r.get('success', False)),
                         sum(1 for r in results if not r.get('success', False))]
        axes[0, 0].pie(success_counts, labels=['成功', '失败'], autopct='%1.1f%%', colors=['lightgreen', 'lightcoral'])
        axes[0, 0].set_title('测试成功率分布')
        
        # 2. 得分分布
        scores = [r.get('score', 0) for r in results]
        axes[0, 1].hist(scores, bins=15, alpha=0.7, color='skyblue', edgecolor='black')
        axes[0, 1].set_xlabel('得分')
        axes[0, 1].set_ylabel('频数')
        axes[0, 1].set_title('得分分布')
        axes[0, 1].axvline(np.mean(scores), color='red', linestyle='--', label=f'平均分: {np.mean(scores):.1f}')
        axes[0, 1].legend()
        
        # 3. 执行时间分布
        exec_times = [r.get('execution_time', 0) for r in results]
        axes[0, 2].boxplot(exec_times)
        axes[0, 2].set_ylabel('执行时间(秒)')
        axes[0, 2].set_title('执行时间分布')
        
        # 4. 按类别的成功率
        categories = {}
        for result in results:
            category = result.get('category', 'unknown')
            if category not in categories:
                categories[category] = {'total': 0, 'success': 0}
            categories[category]['total'] += 1
            if result.get('success', False):
                categories[category]['success'] += 1
        
        cat_names = list(categories.keys())
        success_rates = [categories[cat]['success'] / categories[cat]['total'] for cat in cat_names]
        
        bars = axes[1, 0].bar(cat_names, success_rates, color='lightblue', alpha=0.7)
        axes[1, 0].set_ylabel('成功率')
        axes[1, 0].set_title('各类别成功率')
        axes[1, 0].set_ylim(0, 1)
        plt.setp(axes[1, 0].get_xticklabels(), rotation=45)
        
        # 为每个柱子添加数值标签
        for bar, rate in zip(bars, success_rates):
            height = bar.get_height()
            axes[1, 0].text(bar.get_x() + bar.get_width()/2., height + 0.01,
                           f'{rate:.2f}', ha='center', va='bottom')
        
        # 5. 得分 vs 执行时间散点图
        axes[1, 1].scatter(exec_times, scores, alpha=0.6, color='orange')
        axes[1, 1].set_xlabel('执行时间(秒)')
        axes[1, 1].set_ylabel('得分')
        axes[1, 1].set_title('得分 vs 执行时间')
        
        # 6. 时间序列趋势（如果有时间戳）
        if all('timestamp' in r for r in results):
            timestamps = [datetime.fromisoformat(r['timestamp']) for r in results]
            axes[1, 2].plot(timestamps, scores, marker='o', linestyle='-', alpha=0.7)
            axes[1, 2].set_xlabel('时间')
            axes[1, 2].set_ylabel('得分')
            axes[1, 2].set_title('得分时间趋势')
            plt.setp(axes[1, 2].get_xticklabels(), rotation=45)
        else:
            # 如果没有时间戳，显示测试顺序趋势
            test_indices = list(range(len(results)))
            axes[1, 2].plot(test_indices, scores, marker='o', linestyle='-', alpha=0.7, color='green')
            axes[1, 2].set_xlabel('测试序号')
            axes[1, 2].set_ylabel('得分')
            axes[1, 2].set_title('测试序列得分趋势')
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"指标可视化图表已保存至: {output_path}")
        
        plt.show()

# 使用示例
if __name__ == "__main__":
    # 创建示例数据
    sample_results = [
        {
            'test_name': '基础统计分析',
            'category': 'statistics',
            'success': True,
            'execution_time': 2.5,
            'score': 85,
            'code_generated': True,
            'timestamp': datetime.now().isoformat()
        },
        {
            'test_name': '数据可视化',
            'category': 'visualization',
            'success': True,
            'execution_time': 3.2,
            'score': 92,
            'code_generated': True,
            'timestamp': datetime.now().isoformat()
        },
        {
            'test_name': '机器学习',
            'category': 'machine_learning',
            'success': False,
            'execution_time': 5.1,
            'score': 45,
            'code_generated': False,
            'timestamp': datetime.now().isoformat()
        }
    ]
    
    # 创建评估指标对象
    evaluator = EvaluationMetrics()
    
    # 生成性能摘要
    summary = evaluator.generate_performance_summary(sample_results)
    print("性能摘要:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    # 生成可视化
    evaluator.visualize_metrics(sample_results)