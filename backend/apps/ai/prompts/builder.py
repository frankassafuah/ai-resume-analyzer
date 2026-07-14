"""PromptBuilder — assembles provider-neutral chat messages from templates."""
from apps.ai.prompts import templates
from apps.ai.providers.base import Message


class PromptBuilder:
    def build_resume_analysis(
        self, resume_text: str, job_description: str
    ) -> list[Message]:
        user = templates.RESUME_ANALYSIS_USER.format(
            schema=templates.RESUME_ANALYSIS_SCHEMA,
            resume=resume_text.strip(),
            job_description=job_description.strip(),
        )
        return [
            {"role": "system", "content": templates.RESUME_ANALYSIS_SYSTEM},
            {"role": "user", "content": user},
        ]
