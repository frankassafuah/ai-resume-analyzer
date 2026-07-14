"""Offline provider — the default.

Returns deterministic, schema-valid resume-analysis JSON derived from the prompt
text, so the entire pipeline (and its tests) runs with no API keys or network.
It intentionally lives behind the same interface as the real providers.
"""
import json

from apps.ai.providers.base import AIProvider, Message, ProviderResponse

# A small skill vocabulary used to make the fake output track the input.
_KNOWN_SKILLS = [
    "python", "django", "fastapi", "flask", "react", "vue", "typescript",
    "javascript", "aws", "gcp", "azure", "docker", "kubernetes", "postgresql",
    "mysql", "redis", "celery", "sql", "graphql", "rest", "git", "ci/cd",
    "terraform", "kafka", "spark",
]


class FakeProvider(AIProvider):
    name = "fake"

    def complete(
        self,
        messages: list[Message],
        *,
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 2000,
        json_mode: bool = True,
        timeout: int = 60,
    ) -> ProviderResponse:
        blob = "\n".join(m.get("content", "") for m in messages).lower()
        present = [s for s in _KNOWN_SKILLS if s in blob]
        missing = [s for s in ("docker", "kubernetes", "graphql") if s not in present][:3]

        score = min(95, 50 + len(present) * 5)
        result = {
            "score": score,
            "ats_score": min(90, 60 + len(present) * 3),
            "matching_skills": present,
            "missing_skills": missing,
            "keywords": present[:10],
            "strengths": [
                "Relevant technical skills present in the resume.",
                "Clear, ATS-readable structure.",
            ],
            "weaknesses": (
                [f"Missing exposure to {', '.join(missing)}."] if missing else
                ["Could quantify impact with more metrics."]
            ),
            "summary": (
                f"Candidate matches roughly {score}% of the role based on overlapping "
                f"skills ({', '.join(present[:5]) or 'general experience'})."
            ),
            "recommendations": [
                "Add measurable achievements (numbers, %).",
                *([f"Gain or highlight {s} experience." for s in missing]),
            ],
        }
        content = json.dumps(result)
        return ProviderResponse(
            content=content,
            model=model,
            tokens_in=len(blob) // 4,
            tokens_out=len(content) // 4,
            raw={"provider": "fake"},
        )
