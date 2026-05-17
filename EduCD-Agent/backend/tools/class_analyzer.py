from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd

from tools.diagnosis_tool import diagnose_student


def analyze_class(responses: pd.DataFrame, q_matrix: pd.DataFrame) -> Dict[str, Any]:
    student_ids = sorted(responses["student_id"].unique())
    student_mastery = {
        student_id: diagnose_student(student_id, responses, q_matrix)
        for student_id in student_ids
    }

    knowledge_points = [col for col in q_matrix.columns if col != "question_id"]
    class_average = {}
    for knowledge in knowledge_points:
        values = [mastery[knowledge] for mastery in student_mastery.values()]
        class_average[knowledge] = round(sum(values) / len(values), 2) if values else 0.0

    weak_top3 = sorted(class_average.items(), key=lambda item: item[1])[:3]

    high_risk_students: List[str] = []
    for student_id, mastery in student_mastery.items():
        average_mastery = sum(mastery.values()) / len(mastery) if mastery else 0.0
        if average_mastery < 0.5:
            high_risk_students.append(student_id)

    return {
        "student_mastery": student_mastery,
        "class_average_mastery": class_average,
        "weak_knowledge_top3": weak_top3,
        "high_risk_students": high_risk_students,
    }
