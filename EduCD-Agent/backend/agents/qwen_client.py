from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class QwenClient:
    """Qwen client with automatic mock fallback for local demos."""

    def __init__(self, model: str = "qwen3.6-plus") -> None:
        self.model = model
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.mock_mode = not bool(self.api_key)
        self._client = None

        if self.api_key:
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def status_text(self) -> str:
        return "mock 模式" if self.mock_mode else f"真实 Qwen API 模式，模型：{self.model}"

    def chat(self, messages: List[Dict[str, str]], task_type: str = "general") -> str:
        if self.mock_mode:
            return self._mock_response(task_type, messages)

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            self.mock_mode = True
            print(f"[QwenClient] 真实调用失败，已切换到 mock 模式：{exc}")
            return self._mock_response(task_type, messages)

    def _mock_response(self, task_type: str, messages: List[Dict[str, str]]) -> str:
        user_content = messages[-1]["content"] if messages else ""

        if task_type == "cot":
            weak = self._extract_mock_field(user_content, "相关知识点", "相关知识点")
            payload = {
                "error_type": "CalculationError",
                "weak_knowledge": weak,
                "thinking_breakpoint": "在公式或代数变形后没有进行关键校验，导致答案与题意不一致。",
                "reason": "学生对核心知识点已有部分认识，但步骤书写和结果检查不足。",
                "suggestion": "建议先复述题目条件，再按公式或等式性质逐步计算，最后用代入或单位检查验证。",
                "confidence": 0.78,
            }
            return json.dumps(payload, ensure_ascii=False)

        if task_type == "report":
            return (
                "一、总体表现\n"
                "学生完成了本次诊断中的全部题目，基础题有一定正确率，但在综合理解和规范表达上仍有波动。\n\n"
                "二、知识点掌握情况\n"
                "一元一次方程、等式性质和分式运算表现较好；三角形面积、函数图像和几何证明需要重点巩固。\n\n"
                "三、主要薄弱点\n"
                "薄弱点集中在公式理解、坐标代入和证明过程完整性。\n\n"
                "四、典型错因分析\n"
                "错题显示学生容易跳过中间步骤，导致公式漏用、计算结果未检验或证明依据不足。\n\n"
                "五、个性化学习建议\n"
                "建议每天安排 15 分钟进行错题复盘，重点写出每一步的依据和检查方式。\n\n"
                "六、后续练习路径\n"
                "先练基础公式与代数计算，再练函数代入和几何证明，最后完成混合题巩固。"
            )

        if task_type == "reflection":
            return ""

        return "这是 mock 模式下的模拟回复。"

    @staticmethod
    def _extract_mock_field(text: str, label: str, fallback: str) -> str:
        for line in text.splitlines():
            if line.startswith(label):
                return line.split("：", 1)[-1].strip()
        return fallback
