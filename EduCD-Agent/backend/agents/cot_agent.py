from __future__ import annotations

import json
from typing import Any, Dict, List

from agents.qwen_client import QwenClient


ERROR_TYPES = {
    "ConceptError",
    "FormulaError",
    "CalculationError",
    "StepJumpError",
    "TransferError",
    "CarelessError",
}


def analyze_wrong_answer(
    qwen_client: QwenClient,
    wrong_question: Dict[str, Any],
    student_answer: str,
    mastery: Dict[str, float],
    knowledge_base: Dict[str, Any],
) -> Dict[str, Any]:
    knowledge_points = wrong_question["knowledge_points"]
    kb_items = {point: knowledge_base.get(point, {}) for point in knowledge_points}

    prompt = f"""
请作为智慧教育认知诊断智能体，对学生错题做思维链层面的可解释错因分析。
只输出合法 JSON，不要输出 Markdown。

题目ID：{wrong_question["question_id"]}
题目内容：{wrong_question["content"]}
相关知识点：{", ".join(knowledge_points)}
学生答案：{student_answer}
正确答案：{wrong_question["correct_answer"]}
知识点掌握度：{json.dumps({k: mastery.get(k, 0.0) for k in knowledge_points}, ensure_ascii=False)}
知识库：{json.dumps(kb_items, ensure_ascii=False)}

JSON 字段必须包括：
error_type, weak_knowledge, thinking_breakpoint, reason, suggestion, confidence
error_type 必须从以下类别选择：
ConceptError, FormulaError, CalculationError, StepJumpError, TransferError, CarelessError
""".strip()

    raw = qwen_client.chat(
        [
            {"role": "system", "content": "你是面向初中数学认知诊断的错因分析智能体。"},
            {"role": "user", "content": prompt},
        ],
        task_type="cot",
    )
    return _safe_parse_error_analysis(raw, knowledge_points, mastery)


def _safe_parse_error_analysis(
    raw: str,
    knowledge_points: List[str],
    mastery: Dict[str, float] | None = None,
) -> Dict[str, Any]:
    try:
        data = json.loads(_extract_json_text(raw))
    except json.JSONDecodeError:
        data = {
            "error_type": "StepJumpError",
            "weak_knowledge": knowledge_points[0] if knowledge_points else "未知知识点",
            "thinking_breakpoint": "模型返回内容不是合法 JSON，系统已用兜底规则生成分析。",
            "reason": raw.strip()[:120] or "未能获得有效错因说明。",
            "suggestion": "回到题目条件，逐步写出公式、变形依据和检查过程。",
            "confidence": 0.5,
        }

    if data.get("error_type") not in ERROR_TYPES:
        data["error_type"] = "StepJumpError"
    data.setdefault("weak_knowledge", knowledge_points[0] if knowledge_points else "未知知识点")
    data.setdefault("thinking_breakpoint", "关键步骤不够清晰。")
    data.setdefault("reason", "需要结合步骤进一步复盘。")
    data.setdefault("suggestion", "建议补全解题步骤并进行答案检验。")
    data.setdefault("confidence", 0.5)
    data["weak_knowledge"] = _normalize_weak_knowledge(
        data.get("weak_knowledge"),
        knowledge_points,
        mastery or {},
    )

    try:
        data["confidence"] = max(0.0, min(1.0, float(data["confidence"])))
    except (TypeError, ValueError):
        data["confidence"] = 0.5

    return data


def _normalize_weak_knowledge(
    value: Any,
    knowledge_points: List[str],
    mastery: Dict[str, float],
) -> List[str]:
    if isinstance(value, list):
        normalized = [str(item).strip() for item in value if str(item).strip()]
        if normalized:
            return normalized

    if isinstance(value, str) and value.strip():
        separators = ["，", ",", "、", ";", "；"]
        parts = [value.strip()]
        for separator in separators:
            if separator in value:
                parts = [part.strip() for part in value.split(separator)]
                break
        normalized = [part for part in parts if part]
        if normalized:
            return normalized

    candidates = knowledge_points or list(mastery.keys())
    if not candidates:
        return ["未知知识点"]

    weakest = min(candidates, key=lambda point: mastery.get(point, 0.0))
    return [weakest]


def _extract_json_text(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text
