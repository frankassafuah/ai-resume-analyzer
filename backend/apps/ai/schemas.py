"""Pydantic schemas for AI structured output.

The model is instructed to return JSON matching `AnalysisResult`; the
ResponseParser validates against this, so downstream code always gets a
well-formed, typed result regardless of which provider produced it.
"""
from pydantic import BaseModel, Field, field_validator


def _clamp_score(v: int) -> int:
    return max(0, min(100, int(v)))


class AnalysisResult(BaseModel):
    score: int = Field(description="Overall match score 0-100")
    ats_score: int = Field(description="ATS/formatting score 0-100")
    matching_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    summary: str = ""
    recommendations: list[str] = Field(default_factory=list)

    @field_validator("score", "ats_score", mode="before")
    @classmethod
    def _validate_score(cls, v: object) -> int:
        try:
            return _clamp_score(v)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return 0

    @field_validator(
        "matching_skills", "missing_skills", "keywords",
        "strengths", "weaknesses", "recommendations",
        mode="before",
    )
    @classmethod
    def _coerce_list(cls, v: object) -> list[str]:
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return [str(x).strip() for x in v if str(x).strip()]  # type: ignore[union-attr]
