from __future__ import annotations

import json
from typing import Any, Dict, List

from agents.qwen_client import QwenClient


def optimize_report(
    qwen_client: QwenClient,
    original_report: str,
    mastery: Dict[str, float],
    error_analyses: List[Dict[str, Any]],
) -> str:
    if qwen_client.mock_mode:
        return _append_self_check_note(original_report)

    prompt = f"""
请对以下学情报告进行自检和优化。

检查重点：
1. 是否与知识点掌握度矛盾
2. 是否过度推断学生能力
3. 学习建议是否过于笼统
4. 语言是否适合学生理解

知识点掌握度：{json.dumps(mastery, ensure_ascii=False)}
错因分析列表：{json.dumps(error_analyses, ensure_ascii=False)}
原始报告：
{original_report}

请直接输出优化后的完整报告，保留六个一级标题。
不要编造日期、教材版本、教学进度、学生长期能力或课堂表现。
不要使用 emoji，不要使用 Markdown 表格。
""".strip()

    optimized = qwen_client.chat(
        [
            {"role": "system", "content": "你是智慧教育报告自检和优化智能体。"},
            {"role": "user", "content": prompt},
        ],
        task_type="reflection",
    )

    if not optimized.strip() or qwen_client.mock_mode:
        return _append_self_check_note(original_report)
    if _has_report_risk(optimized):
        return _build_local_checked_report(mastery, error_analyses)
    return optimized


def _append_self_check_note(report: str) -> str:
    return (
        f"{report}\n\n"
        "系统自检说明：当前未使用真实 Qwen API 进行报告二次优化；系统已基于本地规则保留原报告。"
        "请重点核对低掌握度知识点、错因类型和学习建议是否与学生实际情况一致。"
    )


def _has_report_risk(report: str) -> bool:
    risky_terms = [
        "生成日期",
        "2024",
        "2025",
        "2026",
        "教材进度",
        "人教版",
        "尚未系统讲授",
        "长期",
        "空间想象",
        "逻辑思维差",
        "不认真",
    ]
    return any(term in report for term in risky_terms)


def _build_local_checked_report(mastery: Dict[str, float], error_analyses: List[Dict[str, Any]]) -> str:
    weak_points = [name for name, score in mastery.items() if score < 0.6]
    strong_points = [name for name, score in mastery.items() if score >= 0.8]
    error_lines = []
    for item in error_analyses:
        error_lines.append(
            f"- {item.get('question_id', '未知题目')}：{item.get('weak_knowledge', '未知知识点')}，"
            f"错因类型 {item.get('error_type', '未知')}。{item.get('reason', '')}"
        )

    mastery_lines = "\n".join(f"- {name}：{score:.2f}" for name, score in mastery.items())
    weak_text = "、".join(weak_points) if weak_points else "暂未发现明显薄弱知识点"
    strong_text = "、".join(strong_points) if strong_points else "暂无特别突出的高掌握度知识点"
    error_text = "\n".join(error_lines) if error_lines else "本次没有错题记录。"

    return f"""一、总体表现
本次诊断显示，学生在 {strong_text} 上表现较稳定；需要重点关注 {weak_text}。以下结论只依据本次答题数据，不推断学生长期能力。

二、知识点掌握情况
{mastery_lines}

三、主要薄弱点
当前低掌握度知识点为：{weak_text}。建议优先处理这些知识点对应的公式、概念和步骤书写问题。

四、典型错因分析
{error_text}

五、个性化学习建议
先从低掌握度知识点开始复盘。每道错题按“题目条件、所用公式或定理、关键计算步骤、答案检查”四步重写一遍。

六、后续练习路径
第一步，完成基础概念和公式题；第二步，完成同类变式题；第三步，把本次错题隔天重做；第四步，每周整理一次仍然出错的知识点。

系统自检说明：真实模型报告包含可能过度推断或虚构的信息，系统已自动改写为基于本次诊断数据的保守版本。"""
