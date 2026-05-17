from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def load_questions(path: Path | None = None) -> List[Dict[str, Any]]:
    file_path = path or DATA_DIR / "questions.json"
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_q_matrix(path: Path | None = None) -> pd.DataFrame:
    file_path = path or DATA_DIR / "q_matrix.csv"
    return pd.read_csv(file_path)


def load_responses(path: Path | None = None) -> pd.DataFrame:
    file_path = path or DATA_DIR / "responses.csv"
    responses = pd.read_csv(file_path)
    responses["is_correct"] = responses["is_correct"].astype(int)
    return responses


def load_knowledge_base(path: Path | None = None) -> Dict[str, Any]:
    file_path = path or DATA_DIR / "knowledge_base.json"
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_all_data() -> Tuple[List[Dict[str, Any]], pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    return load_questions(), load_q_matrix(), load_responses(), load_knowledge_base()
