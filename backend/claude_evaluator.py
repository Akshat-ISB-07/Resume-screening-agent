import json
import time
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are a senior talent evaluator at Acceler, an enterprise AI deployment firm that helps large organizations move from AI experimentation to real operational impact. You evaluate candidates for the Founder's Office Associate role — a 0-to-1 builder position working directly with founders across GTM, product, and client strategy.

COMPANY CONTEXT:
Acceler works with enterprise leadership teams to identify high-ROI AI opportunities, design solutions, and deploy AI at scale. The Founder's Office is high-ambiguity, high-ownership. Candidates must handle unstructured problems, build from scratch, and communicate at founder and executive level.

WHAT THIS ROLE IS NOT:
- Not a pure analyst or slide-maker role
- Not for someone who needs a heavily structured environment
- Not for purely technical candidates without business exposure
- Not for candidates who cannot demonstrate ownership

EVALUATION PHILOSOPHY:
- Score on demonstrated evidence not claimed experience
- Builder mindset AND structured thinking must both be present
- Strong executor but weak strategic thinker = Needs Review not Strong Hire
- 1-2 years consulting is ideal
- AI familiarity is a plus but not a dealbreaker"""

EVAL_TEMPLATE = """
ROLE: {job_title}

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

SCORING RUBRIC (score each dimension independently 0-100):
{rubric}

Evaluate this candidate for Acceler's Founder's Office Associate role.
Be specific — reference actual content from their resume.
Do NOT include an overall score — return dimension scores only.

Respond ONLY with a valid JSON object:
{{
  "candidate_name": "<full name from resume or Unknown>",
  "consulting_background": <true or false>,
  "ai_familiarity": "<None | Basic | Intermediate | Advanced>",
  "experience_years": <integer>,
  "reasoning": "<3-4 sentences specific to this candidate>",
  "strengths": ["<evidence-based strength 1>", "<strength 2>", "<strength 3>"],
  "gaps": ["<specific gap vs this role>", "<gap 2 if any>"],
  "builder_signals": ["<specific evidence of 0-to-1 building>"],
  "first_principles_signals": ["<specific evidence of structured thinking>"],
  "key_skills_matched": ["<skill 1>", "<skill 2>", "<skill 3>"],
  "screening_questions": [
    "<Question probing a specific gap from THIS candidate>",
    "<Question probing ability to handle ambiguity>",
    "<Question probing AI familiarity and real usage>"
  ],
  "red_flags": ["<concern if any, else empty list>"],
  "interviewer_note": "<One sentence for the hiring manager>",
  "dimension_scores": {{
    {dimension_keys}
  }}
}}

Per-dimension scoring guidance:
- 80-100: Clear, specific evidence directly demonstrated in the resume
- 60-79: Partial evidence — present but with notable gaps
- 40-59: Weak or indirect signal only
- 0-39: No credible evidence, or counter-evidence present
"""


def _build_message(
    resume_text: str,
    job_description: str,
    job_title: str = "Founder's Office Associate",
    rubric: str = "Evaluate overall fit for the role.",
    dimension_keys: str = '"Overall fit": <0-100>',
) -> dict:
    return {
        "role": "user",
        "content": EVAL_TEMPLATE.format(
            job_title=job_title,
            job_description=job_description,
            resume_text=resume_text[:8000],
            rubric=rubric,
            dimension_keys=dimension_keys,
        ),
    }


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.rsplit("```", 1)[0].strip()
    return json.loads(text)


def evaluate_for_job(
    resume_text: str,
    job_title: str,
    job_description: str,
    criteria: list[dict],
    filename: str,
) -> dict:
    rubric = "\n".join(f"- {c['name']} (weight: {c['weight']}%)" for c in criteria)
    dimension_keys = ",\n    ".join(f'"{c["name"]}": <0-100>' for c in criteria)

    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[_build_message(
            resume_text, job_description,
            job_title=job_title,
            rubric=rubric,
            dimension_keys=dimension_keys,
        )],
    )
    data = _parse_json(response.content[0].text)

    # Compute overall_score dynamically from the job's criteria weights
    dim = data.get("dimension_scores", {})
    overall_score = round(sum(
        dim.get(c["name"], 0) * c["weight"] / 100
        for c in criteria
    ))
    data["score"] = overall_score
    data["dimension_scores"] = dim  # ensure key exists even if Claude omitted it

    # Bucket by computed score
    if overall_score >= 80:
        data["bucket"] = "Strong Hire"
    elif overall_score >= 60:
        data["bucket"] = "Promising"
    elif overall_score >= 40:
        data["bucket"] = "Needs Review"
    else:
        data["bucket"] = "Not Suitable"

    if not data.get("candidate_name") or data["candidate_name"].strip().lower() == "unknown":
        data["candidate_name"] = (
            filename.removesuffix(".pdf").replace("_", " ").replace("-", " ").title()
        )
    data["filename"] = filename
    return data


def evaluate_resume(resume_text: str, job_description: str) -> dict:
    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[_build_message(resume_text, job_description)],
    )
    return _parse_json(response.content[0].text)


def evaluate_resumes_batch(resumes: list[dict]) -> list[dict]:
    """Bulk-evaluate resumes using the Anthropic Message Batches API.

    Each item in `resumes` must have keys: "resume_text", "job_description".
    Returns results in the same order as input.
    """
    requests = [
        anthropic.types.message_create_params.Request(
            custom_id=str(i),
            params=anthropic.types.MessageCreateParamsNonStreaming(
                model=MODEL,
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                messages=[_build_message(r["resume_text"], r["job_description"])],
            ),
        )
        for i, r in enumerate(resumes)
    ]

    batch = client.messages.batches.create(requests=requests)

    while batch.processing_status == "in_progress":
        time.sleep(5)
        batch = client.messages.batches.retrieve(batch.id)

    id_to_result: dict[str, dict] = {}
    for result in client.messages.batches.results(batch.id):
        if result.result.type == "succeeded":
            try:
                id_to_result[result.custom_id] = json.loads(
                    result.result.message.content[0].text
                )
            except json.JSONDecodeError:
                id_to_result[result.custom_id] = {"error": "Invalid JSON from model"}
        else:
            id_to_result[result.custom_id] = {"error": f"Batch item failed: {result.result.type}"}

    return [id_to_result.get(str(i), {"error": "Missing result"}) for i in range(len(resumes))]
