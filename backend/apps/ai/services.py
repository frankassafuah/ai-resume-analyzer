"""AI service: resume analysis orchestration.

`ResumeAnalyzer.analyze` is the provider-agnostic capability: build the prompt,
call the gateway, parse+validate the response into an `AnalysisResult`. On a
parse failure it issues one repair retry before giving up. It returns a typed
result — persistence is the caller's concern (see analysis.AnalysisService).
"""
from django.conf import settings

from apps.ai.exceptions import ResponseParseError
from apps.ai.gateway import AIGateway
from apps.ai.parsers import ResponseParser
from apps.ai.prompts.builder import PromptBuilder
from apps.ai.prompts.templates import RESUME_ANALYSIS_VERSION
from apps.ai.schemas import AnalysisResult
from apps.common.services import BaseService


class ResumeAnalyzer(BaseService):
    prompt_version = RESUME_ANALYSIS_VERSION

    def __init__(
        self,
        gateway: AIGateway | None = None,
        builder: PromptBuilder | None = None,
        parser: ResponseParser | None = None,
    ) -> None:
        super().__init__()
        self.gateway = gateway or AIGateway()
        self.builder = builder or PromptBuilder()
        self.parser = parser or ResponseParser()

    def analyze(
        self, *, resume_text: str, job_description: str, user=None, analysis=None
    ) -> AnalysisResult:
        messages = self.builder.build_resume_analysis(resume_text, job_description)
        model = settings.LLM_MODEL_STRONG

        resp = self.gateway.complete(
            messages,
            model=model,
            prompt_version=self.prompt_version,
            json_mode=True,
            user=user,
            analysis=analysis,
        )
        try:
            return self.parser.parse_resume_analysis(resp.content)
        except ResponseParseError:
            self.logger.warning("Analysis parse failed; issuing one repair retry.")
            repair = messages + [
                {
                    "role": "user",
                    "content": "Your previous reply was not valid JSON. Respond with "
                    "ONLY the JSON object described, nothing else.",
                }
            ]
            resp = self.gateway.complete(
                repair,
                model=model,
                prompt_version=self.prompt_version,
                json_mode=True,
                user=user,
                analysis=analysis,
            )
            return self.parser.parse_resume_analysis(resp.content)
