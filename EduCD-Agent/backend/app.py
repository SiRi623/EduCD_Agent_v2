from __future__ import annotations

import os
from typing import Any, Dict, List

import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS

from agents.cot_agent import analyze_wrong_answer
from agents.qwen_client import QwenClient
from agents.reflection_agent import optimize_report
from agents.report_agent import generate_report
from tools.class_analyzer import analyze_class
from tools.data_loader import load_all_data, load_q_matrix, load_questions, load_responses
from tools.diagnosis_tool import diagnose_student


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.json.ensure_ascii = False
CORS(app)

analysis_cache: Dict[str, Dict[str, Any]] = {}


def success_response(data: Any = None, message: str = "请求成功"):
    return jsonify({"success": True, "message": message, "data": data})


def error_response(message: str, status_code: int = 500):
    response = jsonify({"success": False, "message": message, "data": None})
    response.status_code = status_code
    return response


def analyze_student(student_id: str) -> Dict[str, Any]:
    """Run the full first-stage diagnosis chain for one student."""
    questions, q_matrix, responses, knowledge_base = load_all_data()
    student_responses = _get_student_responses(student_id, responses)
    question_map = {question["question_id"]: question for question in questions}

    mastery = diagnose_student(student_id, responses, q_matrix)
    wrong_questions = _build_wrong_questions(student_responses, question_map)

    qwen_client = QwenClient()
    error_analysis = []
    for wrong_question in wrong_questions:
        analysis = analyze_wrong_answer(
            qwen_client=qwen_client,
            wrong_question=wrong_question,
            student_answer=str(wrong_question["student_answer"]),
            mastery=mastery,
            knowledge_base=knowledge_base,
        )
        analysis["question_id"] = wrong_question["question_id"]
        error_analysis.append(analysis)

    overall_performance = _calculate_overall_performance(student_responses)
    original_report = generate_report(
        qwen_client=qwen_client,
        student_id=student_id,
        mastery=mastery,
        error_analyses=error_analysis,
        overall_performance=overall_performance,
    )
    report = optimize_report(
        qwen_client=qwen_client,
        original_report=original_report,
        mastery=mastery,
        error_analyses=error_analysis,
    )

    return {
        "student_id": student_id,
        "mastery": mastery,
        "wrong_questions": wrong_questions,
        "error_analysis": error_analysis,
        "report": report,
    }


def get_cached_analysis(student_id: str) -> Dict[str, Any]:
    if student_id not in analysis_cache:
        analysis_cache[student_id] = analyze_student(student_id)
    return analysis_cache[student_id]


def _get_student_responses(student_id: str, responses: pd.DataFrame) -> pd.DataFrame:
    student_responses = responses[responses["student_id"] == student_id].copy()
    if student_responses.empty:
        raise ValueError(f"未找到学生 {student_id} 的答题记录")
    return student_responses


def _build_wrong_questions(
    student_responses: pd.DataFrame,
    question_map: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    wrong_responses = student_responses[student_responses["is_correct"] == 0]
    wrong_questions: List[Dict[str, Any]] = []

    for _, response in wrong_responses.iterrows():
        question = question_map.get(response["question_id"])
        if not question:
            continue
        wrong_questions.append(
            {
                "question_id": question["question_id"],
                "content": question["content"],
                "student_answer": str(response["student_answer"]),
                "correct_answer": question["correct_answer"],
                "knowledge_points": question["knowledge_points"],
                "difficulty": question.get("difficulty"),
            }
        )

    return wrong_questions


def _calculate_overall_performance(student_responses: pd.DataFrame) -> Dict[str, Any]:
    total_questions = len(student_responses)
    correct_count = int(student_responses["is_correct"].sum())
    accuracy = correct_count / total_questions if total_questions else 0.0
    return {
        "total_questions": total_questions,
        "correct_count": correct_count,
        "wrong_count": total_questions - correct_count,
        "accuracy": accuracy,
    }


@app.route("/api/health", methods=["GET"])
def health_check():
    try:
        return success_response(
            data={"service": "EduCD-Agent", "version": "0.2.0"},
            message="EduCD-Agent backend is running",
        )
    except Exception as exc:
        return error_response(str(exc))


@app.route("/api/students", methods=["GET"])
def get_students():
    try:
        responses = load_responses()
        student_ids = sorted(responses["student_id"].dropna().unique().tolist())
        return success_response(student_ids)
    except Exception as exc:
        return error_response(str(exc))


@app.route("/api/questions", methods=["GET"])
def get_questions():
    try:
        return success_response(load_questions())
    except Exception as exc:
        return error_response(str(exc))


@app.route("/api/diagnose/<student_id>", methods=["GET"])
def diagnose(student_id: str):
    try:
        responses = load_responses()
        q_matrix = load_q_matrix()
        _get_student_responses(student_id, responses)
        mastery = diagnose_student(student_id, responses, q_matrix)
        return success_response({"student_id": student_id, "mastery": mastery})
    except Exception as exc:
        return error_response(str(exc))


@app.route("/api/errors/<student_id>", methods=["GET"])
def get_error_analysis(student_id: str):
    try:
        analysis = get_cached_analysis(student_id)
        return success_response(
            {
                "student_id": student_id,
                "wrong_questions": analysis["wrong_questions"],
                "error_analysis": analysis["error_analysis"],
            }
        )
    except Exception as exc:
        return error_response(str(exc))


@app.route("/api/report/<student_id>", methods=["GET"])
def get_report(student_id: str):
    try:
        analysis = get_cached_analysis(student_id)
        return success_response({"student_id": student_id, "report": analysis["report"]})
    except Exception as exc:
        return error_response(str(exc))


@app.route("/api/full-analysis/<student_id>", methods=["GET"])
def get_full_analysis(student_id: str):
    try:
        return success_response(get_cached_analysis(student_id))
    except Exception as exc:
        return error_response(str(exc))


@app.route("/api/class-summary", methods=["GET"])
def get_class_summary():
    try:
        responses = load_responses()
        q_matrix = load_q_matrix()
        summary = analyze_class(responses, q_matrix)
        weak_top3 = [
            {"knowledge": knowledge, "average_mastery": average_mastery}
            for knowledge, average_mastery in summary["weak_knowledge_top3"]
        ]
        return success_response(
            {
                "class_average_mastery": summary["class_average_mastery"],
                "weak_knowledge_top3": weak_top3,
                "high_risk_students": summary["high_risk_students"],
            }
        )
    except Exception as exc:
        return error_response(str(exc))


@app.route("/api/cache/clear", methods=["GET"])
def clear_cache():
    try:
        analysis_cache.clear()
        return success_response(data=None, message="缓存已清空")
    except Exception as exc:
        return error_response(str(exc))


if __name__ == "__main__":
    print("EduCD-Agent Flask backend is running...")
    print("API base URL: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
