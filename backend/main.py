import os
import tempfile
import threading
import uuid
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from claude_evaluator import evaluate_for_job, evaluate_resume
from pdf_extractor import extract_text_from_pdf

load_dotenv()

app = FastAPI(title="Resume Screening Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_jobs: dict = {}

DEFAULT_CRITERIA = [
    {"name": "First-principles & structured thinking", "weight": 30},
    {"name": "Builder mindset & ownership signals",    "weight": 25},
    {"name": "Consulting / strategy background",       "weight": 20},
    {"name": "Communication & stakeholder skills",     "weight": 15},
    {"name": "AI familiarity & tools",                 "weight": 10},
]


# ── Pydantic models ────────────────────────────────────────────────────────

class Criterion(BaseModel):
    name: str
    weight: float


class JobCreate(BaseModel):
    job_title: str
    job_description: str
    criteria: list[Criterion] = Field(
        default_factory=lambda: [Criterion(**c) for c in DEFAULT_CRITERIA]
    )

    @field_validator("criteria")
    @classmethod
    def weights_sum_to_100(cls, criteria):
        total = sum(c.weight for c in criteria)
        if abs(total - 100) > 1.0:
            raise ValueError(f"Criteria weights must sum to 100 (got {total:.1f})")
        return criteria


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/jobs", status_code=201)
def create_job(payload: JobCreate):
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "id": job_id,
        "job_title": payload.job_title,
        "job_description": payload.job_description,
        "criteria": [c.model_dump() for c in payload.criteria],
        "status": "pending",
        "progress": 0,
        "progress_message": "Job created. Waiting for resumes.",
        "resumes": [],
        "results": [],
    }
    return {"id": job_id}


@app.post("/upload/{job_id}")
async def upload_resumes(job_id: str, files: List[UploadFile] = File(...)):
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    job = _jobs[job_id]
    if job["status"] != "pending":
        raise HTTPException(status_code=409, detail="Job already started or completed")

    for f in files:
        if not f.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"'{f.filename}' is not a PDF")
        content = await f.read()
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        try:
            text = extract_text_from_pdf(tmp_path)
        finally:
            os.unlink(tmp_path)
        job["resumes"].append({"filename": f.filename, "text": text or "", "result": None})

    return {"job_id": job_id, "file_count": len(job["resumes"])}


@app.post("/run/{job_id}")
def run_job(job_id: str):
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    job = _jobs[job_id]
    if not job["resumes"]:
        raise HTTPException(status_code=400, detail="No resumes uploaded")
    if job["status"] == "running":
        raise HTTPException(status_code=409, detail="Job already running")

    job["status"] = "running"
    job["progress"] = 0
    job["progress_message"] = f"Starting evaluation of {len(job['resumes'])} candidate(s)..."

    thread = threading.Thread(target=_run_evaluations, args=(job_id,), daemon=True)
    thread.start()
    return {"job_id": job_id, "status": "running"}


def _run_evaluations(job_id: str) -> None:
    job = _jobs[job_id]
    total = len(job["resumes"])

    for i, resume in enumerate(job["resumes"]):
        name = resume["filename"].removesuffix(".pdf").replace("_", " ").title()
        job["progress_message"] = f"Evaluating {name} ({i + 1} of {total})..."
        try:
            result = evaluate_for_job(
                resume_text=resume["text"],
                job_title=job["job_title"],
                job_description=job["job_description"],
                criteria=job["criteria"],
                filename=resume["filename"],
            )
        except Exception as exc:
            result = {
                "candidate_name": name,
                "filename": resume["filename"],
                "score": 0,
                "bucket": "Not Suitable",
                "consulting_background": False,
                "ai_familiarity": "None",
                "experience_years": 0,
                "reasoning": f"Evaluation failed: {exc}",
                "strengths": [],
                "gaps": [str(exc)],
                "builder_signals": [],
                "first_principles_signals": [],
                "key_skills_matched": [],
                "screening_questions": [],
                "red_flags": ["Evaluation error"],
                "interviewer_note": "Could not evaluate this candidate.",
            }
        resume["result"] = result
        job["results"].append(result)
        job["progress"] = int((i + 1) / total * 100)

    job["status"] = "completed"
    job["progress"] = 100
    job["progress_message"] = f"Complete — {total} candidate(s) evaluated."


@app.get("/status/{job_id}")
def get_status(job_id: str):
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    job = _jobs[job_id]
    return {
        "status": job["status"],
        "progress": job["progress"],
        "progress_message": job["progress_message"],
        "total": len(job["resumes"]),
        "completed": sum(1 for r in job["resumes"] if r["result"] is not None),
        "results": job["results"],
    }
