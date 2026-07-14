"""AI layer tests: providers, registry, prompt parsing, gateway, analyzer."""
import json

import pytest

from apps.ai.exceptions import ProviderError, ResponseParseError
from apps.ai.gateway import AIGateway
from apps.ai.models import AIGenerationLog
from apps.ai.parsers import ResponseParser
from apps.ai.providers import get_provider
from apps.ai.providers.base import AIProvider, ProviderResponse
from apps.ai.schemas import AnalysisResult
from apps.ai.services import ResumeAnalyzer

RESUME = "Senior Python engineer with Django, PostgreSQL and AWS experience."
JOB = "Looking for a Python/Django developer. Docker and GraphQL a plus."


# --- registry / providers -------------------------------------------------
def test_get_provider_returns_fake_by_default():
    assert get_provider("fake").name == "fake"


def test_get_provider_unknown_raises():
    with pytest.raises(ProviderError):
        get_provider("does-not-exist")


def test_fake_provider_returns_schema_valid_json():
    provider = get_provider("fake")
    resp = provider.complete(
        [{"role": "user", "content": RESUME + " " + JOB}], model="fake-strong"
    )
    data = json.loads(resp.content)
    result = AnalysisResult.model_validate(data)
    assert "python" in result.matching_skills
    assert 0 <= result.score <= 100


# --- response parser ------------------------------------------------------
@pytest.fixture
def parser():
    return ResponseParser()


def test_parser_plain_json(parser):
    raw = '{"score": 80, "ats_score": 70, "summary": "ok"}'
    result = parser.parse_resume_analysis(raw)
    assert result.score == 80 and result.summary == "ok"


def test_parser_strips_markdown_fence(parser):
    raw = "```json\n{\"score\": 90, \"ats_score\": 88}\n```"
    assert parser.parse_resume_analysis(raw).score == 90


def test_parser_extracts_json_from_prose(parser):
    raw = "Sure! Here is the result:\n{\"score\": 55, \"ats_score\": 50}\nHope it helps."
    assert parser.parse_resume_analysis(raw).score == 55


def test_parser_clamps_out_of_range_scores(parser):
    result = parser.parse_resume_analysis('{"score": 150, "ats_score": -5}')
    assert result.score == 100 and result.ats_score == 0


def test_parser_raises_on_garbage(parser):
    with pytest.raises(ResponseParseError):
        parser.parse_resume_analysis("no json here at all")


# --- gateway --------------------------------------------------------------
@pytest.mark.django_db
def test_gateway_logs_success():
    gw = AIGateway(provider=get_provider("fake"))
    resp = gw.complete(
        [{"role": "user", "content": RESUME}], model="fake-strong",
        prompt_version="test.v1",
    )
    assert resp.content
    log = AIGenerationLog.objects.get()
    assert log.status == "success" and log.provider == "fake"
    assert log.prompt_version == "test.v1"


@pytest.mark.django_db
def test_gateway_retries_then_logs_error(settings):
    settings.LLM_MAX_RETRIES = 0  # single attempt, no backoff sleeps

    class BoomProvider(AIProvider):
        name = "boom"

        def complete(self, *a, **k) -> ProviderResponse:
            raise RuntimeError("provider down")

    gw = AIGateway(provider=BoomProvider())
    with pytest.raises(ProviderError):
        gw.complete([{"role": "user", "content": "x"}], model="m", prompt_version="v")
    log = AIGenerationLog.objects.get()
    assert log.status == "error" and "provider down" in log.error


# --- analyzer service -----------------------------------------------------
@pytest.mark.django_db
def test_resume_analyzer_returns_result_and_logs():
    result = ResumeAnalyzer().analyze(resume_text=RESUME, job_description=JOB)
    assert isinstance(result, AnalysisResult)
    assert "python" in result.matching_skills
    assert result.summary
    assert AIGenerationLog.objects.filter(status="success").exists()


@pytest.mark.django_db
def test_resume_analyzer_repairs_bad_json(monkeypatch):
    """First call returns garbage, second returns valid JSON -> parsed."""
    calls = {"n": 0}
    good = json.dumps({"score": 77, "ats_score": 70})

    class FlakyProvider(AIProvider):
        name = "flaky"

        def complete(self, *a, **k) -> ProviderResponse:
            calls["n"] += 1
            content = "not json" if calls["n"] == 1 else good
            return ProviderResponse(content=content, model="m", tokens_in=1, tokens_out=1)

    analyzer = ResumeAnalyzer(gateway=AIGateway(provider=FlakyProvider()))
    result = analyzer.analyze(resume_text=RESUME, job_description=JOB)
    assert result.score == 77
    assert calls["n"] == 2  # repair retry happened
