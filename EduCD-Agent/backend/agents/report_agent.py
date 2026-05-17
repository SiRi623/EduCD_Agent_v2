from __future__ import annotations

import json
from typing import Any, Dict, List

from agents.qwen_client import QwenClient


def generate_report(
    qwen_client: QwenClient,
    student_id: str,
    mastery: Dict[str, float],
    error_analyses: List[Dict[str, Any]],
    overall_performance: Dict[str, Any],
) -> str:
    prompt = f"""
请为学生 {student_id} 生成结构化中文学情报告。

知识点掌握度：{json.dumps(mastery, ensure_ascii=False)}
错因分析列表：{json.dumps(error_analyses, ensure_ascii=False)}
答题总体表现：{json.dumps(overall_performance, ensure_ascii=False)}

报告必须包含以下六个标题：
一、总体表现
二、知识点掌握情况
三、主要薄弱点
四、典型错因分析
五、个性化学习建议
六、后续练习路径
语言要适合初中学生和教师共同阅读，建议要具体。
不要编造日期、教材版本、教学进度、学生长期能力或课堂表现。
不要使用 emoji，不要使用 Markdown 表格。
""".strip()

    report = qwen_client.chat(
        [
            {"role": "system", "content": "你是智慧教育学情报告生成智能体。"},
            {"role": "user", "content": prompt},
        ],
        task_type="report",
    )

    return _ensure_required_sections(report, student_id, mastery, error_analyses, overall_performance)


def _ensure_required_sections(
    report: str,
    student_id: str,
    mastery: Dict[str, float],
    error_analyses: List[Dict[str, Any]],
    overall_performance: Dict[str, Any],
) -> str:
    required = ["一、总体表现", "二、知识点掌握情况", "三、主要薄弱点", "四、典型错因分析", "五、个性化学习建议", "六、后续练习路径"]
    if all(section in report for section in required):
        return report

    weak_points = [name for name, score in mastery.items() if score < 0.6]
    typical_errors = "；".join(
        f"{item.get('weak_knowledge')}：{item.get('reason')}" for item in error_analyses
    ) or "暂无明显错因。"

    return f"""学生：{student_id}

一、总体表现
本次共作答 {overall_performance.get("total_questions", 0)} 题，答对 {overall_performance.get("correct_count", 0)} 题，正确率为 {overall_performance.get("accuracy", 0):.0%}。

二、知识点掌握情况
{json.dumps(mastery, ensure_ascii=False)}

三、主要薄弱点
{", ".join(weak_points) if weak_points else "暂未发现明显薄弱知识点。"}

四、典型错因分析
{typical_errors}

五、个性化学习建议
围绕低掌握度知识点进行短题组训练，每题写清公式、步骤依据和检查方法。

六、后续练习路径
先完成基础概念题，再完成计算与应用题，最后进行综合错题复盘。"""
