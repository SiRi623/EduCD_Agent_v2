from __future__ import annotations

from typing import Dict

import pandas as pd

from models.dina import SimpleDINA


def diagnose_student(student_id: str, responses: pd.DataFrame, q_matrix: pd.DataFrame) -> Dict[str, float]:
    student_responses = responses[responses["student_id"] == student_id].copy()
    if student_responses.empty:
        raise ValueError(f"未找到学生 {student_id} 的答题记录")

    return SimpleDINA().diagnose(student_responses, q_matrix)
