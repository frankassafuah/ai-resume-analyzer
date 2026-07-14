"""Versioned prompt templates.

Bumping a prompt = bump its version string; the version is logged with every
generation (AIGenerationLog) for reproducibility and regression tracking.
"""

RESUME_ANALYSIS_VERSION = "analysis.resume.v1"

# The exact JSON contract we ask the model to fill (mirrors AnalysisResult).
RESUME_ANALYSIS_SCHEMA = """{
  "score": <int 0-100 overall match>,
  "ats_score": <int 0-100 ATS/formatting readability>,
  "matching_skills": [<skills present in BOTH resume and job>],
  "missing_skills": [<skills the job requires but the resume lacks>],
  "keywords": [<important keywords from the job description>],
  "strengths": [<candidate strengths for THIS role>],
  "weaknesses": [<gaps or red flags for THIS role>],
  "summary": "<2-3 sentence tailored summary>",
  "recommendations": [<concrete, actionable improvements>]
}"""

RESUME_ANALYSIS_SYSTEM = (
    "You are an expert technical recruiter and an ATS (Applicant Tracking System) "
    "engine. You objectively evaluate how well a resume matches a specific job "
    "description. You are precise, unbiased, and never invent experience the "
    "candidate does not have. You respond with a single valid JSON object and "
    "nothing else — no prose, no markdown fences."
)

RESUME_ANALYSIS_USER = """Analyze the RESUME against the JOB DESCRIPTION and return \
ONLY a JSON object matching exactly this schema:

{schema}

Rules:
- Scores are integers between 0 and 100.
- Skills/keywords are short strings; do not duplicate entries.
- Base everything strictly on the provided text.

=== RESUME ===
{resume}

=== JOB DESCRIPTION ===
{job_description}
"""
