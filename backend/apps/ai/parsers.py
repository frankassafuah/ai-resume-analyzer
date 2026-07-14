"""ResponseParser — turns raw model text into a validated `AnalysisResult`.

Handles the common ways models wrap JSON (markdown fences, leading prose) and
validates against the pydantic schema. Raises `ResponseParseError` on failure so
the service can trigger a repair retry.
"""
import json
import re

from pydantic import ValidationError

from apps.ai.exceptions import ResponseParseError
from apps.ai.schemas import AnalysisResult

_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


class ResponseParser:
    def parse_resume_analysis(self, raw: str) -> AnalysisResult:
        data = self._extract_json(raw)
        try:
            return AnalysisResult.model_validate(data)
        except ValidationError as exc:
            raise ResponseParseError(f"Schema validation failed: {exc}") from exc

    def _extract_json(self, raw: str) -> dict:
        if not raw or not raw.strip():
            raise ResponseParseError("Empty model response.")

        text = raw.strip()
        # Prefer a fenced code block if present.
        fence = _FENCE_RE.search(text)
        if fence:
            text = fence.group(1).strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Fallback: grab the outermost {...} span.
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError as exc:
                raise ResponseParseError(f"Invalid JSON in response: {exc}") from exc
        raise ResponseParseError("No JSON object found in model response.")
