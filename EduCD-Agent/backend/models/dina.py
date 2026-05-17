from __future__ import annotations

from typing import Dict

import pandas as pd


class SimpleDINA:
    """A rule-based approximation of DINA for the first CLI demo."""

    def diagnose(self, student_responses: pd.DataFrame, q_matrix: pd.DataFrame) -> Dict[str, float]:
        knowledge_points = [col for col in q_matrix.columns if col != "question_id"]
        mastery: Dict[str, float] = {}

        merged = student_responses.merge(q_matrix, on="question_id", how="left")

        for knowledge in knowledge_points:
            related_answers = merged[merged[knowledge] == 1]
            total_count = len(related_answers)
            if total_count == 0:
                mastery[knowledge] = 0.0
                continue

            correct_count = int(related_answers["is_correct"].sum())
            mastery[knowledge] = round(correct_count / total_count, 2)

        return mastery
