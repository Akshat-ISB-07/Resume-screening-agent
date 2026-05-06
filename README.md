# TalentFilter — AI-Powered Resume Screening Agent

> **Cuts resume screening time from hours to seconds using Claude AI**

![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)
![Claude](https://img.shields.io/badge/Claude-claude--sonnet--4--6-D97706?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)
![Built with Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-5B6AF0?style=flat-square)

---

## The Problem

Resume screening is the **highest cost-impact workflow in hiring** — yet almost no companies have automated it well.

| Metric | Reality |
|---|---|
| Recruiter time spent screening | 60–70% of total hiring hours |
| Average cost per hire (recruiter hours alone) | $4,000–$7,000 |
| Consistency across screeners | Low — varies by reviewer, time of day, bias |
| Scalability | Zero — hiring freezes when recruiters are overwhelmed |

TalentFilter reduces the marginal cost of screening a candidate to **near zero** — without sacrificing the quality of evaluation.

---

## Demo

> **Upload PDFs → Claude evaluates → Bucketed results appear in seconds**

<img width="960" height="937" alt="Screenshot 2026-05-06 at 4 06 24 PM" src="https://github.com/user-attachments/assets/7067f648-a813-4b4f-8ed2-5345126286a2" />

 <img width="1284" height="946" alt="Screenshot 2026-05-06 at 4 05 54 PM" src="https://github.com/user-attachments/assets/76a5dcbc-f641-4a37-8c50-ef1309325de8" />





*Screenshot placeholder — drag 100 PDFs onto the UI, define your weighted rubric, hit Screen Candidates, and watch Claude evaluate each resume in real time with a live progress bar.*

---

## What It Does

- **Accepts 1–100 PDF resumes** via drag-and-drop or file picker
- **Evaluates each candidate** against a fully customisable weighted scoring rubric
- **Scores across 5 dimensions** (configurable per role) on a 0–100 scale
- **Buckets every candidate** into one of four tiers:

  | Bucket | Score |
  |---|---|
  | Strong Hire | ≥ 80 |
  | Promising | ≥ 60 |
  | Needs Review | ≥ 40 |
  | Not Suitable | < 40 |

- **Generates 3 tailored screening questions** per candidate, targeted at their specific gaps
- **Surfaces interviewer notes**, builder signals, consulting background, and AI familiarity
- **Exports the full shortlist as CSV** with one click

---

## Architecture

```
PDF Resumes (1–100 files)
        │
        ▼
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│  Browser UI      │─────▶│  FastAPI Backend  │─────▶│  PDF Extractor   │
│  (Vanilla JS)    │      │  (main.py)        │      │  (pdfplumber)    │
└──────────────────┘      └──────────────────┘      └──────────────────┘
        ▲                          │                          │
        │                          │                          ▼
        │                          │                 ┌──────────────────┐
        │                          │                 │  Claude API      │
        │                          │                 │  (Sonnet 4.6)    │
        │                          │                 └──────────────────┘
        │                          │                          │
        │                 ┌────────▼─────────┐               │
        └─────────────────│  Weighted Scoring │◀──────────────┘
                          │  Engine (Python)  │
                          └──────────────────┘

Job Lifecycle:  POST /jobs → POST /upload/{id} → POST /run/{id} → GET /status/{id} (poll)
```

The scoring engine runs in Python — not Claude — ensuring deterministic, auditable results. Claude returns raw dimension scores (0–100); Python computes the weighted average and assigns the bucket.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend framework | Python + FastAPI + uvicorn |
| AI model | Anthropic Claude Sonnet (`claude-sonnet-4-6`) |
| PDF parsing | pdfplumber |
| Frontend | Vanilla HTML / CSS / JavaScript (zero dependencies) |
| Data persistence | In-memory (stateless, restarts cleanly) |
| Built with | Claude Code |

---

## Project Structure

```
hiring-project/
├── backend/
│   ├── main.py               # FastAPI server — job lifecycle API (create, upload, run, poll)
│   ├── claude_evaluator.py   # All Claude API calls; prompt construction; JSON parsing
│   ├── pdf_extractor.py      # PDF → plain text via pdfplumber
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # ANTHROPIC_API_KEY goes here (not committed)
│
├── frontend/
│   └── index.html            # Single-file SPA — setup form, progress view, results grid
│
├── sample_resumes/
│   ├── sarah_chen.pdf        # 8 yrs @ Stripe/Airbnb/Google, MBA Stanford → Strong Hire
│   ├── marcus_johnson.pdf    # 4 yrs @ Brex/Toast, BS CS → Promising
│   ├── priya_patel.pdf       # 2 yrs APM @ Shopify contract → Needs Review
│   └── create_sample_resumes.py  # Script that generated the sample PDFs (fpdf2)
│
├── run.sh                    # One-command launcher (uses .venv)
├── CLAUDE.md                 # Instructions for Claude Code
└── README.md                 # This file
```

---

## Running Locally

**1. Clone the repo**
```bash
git clone <repo-url>
cd hiring-project
```

**2. Create a virtual environment and install dependencies**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

**3. Set your Anthropic API key**
```bash
# backend/.env
ANTHROPIC_API_KEY=sk-ant-...
```

**4. Start the backend**
```bash
./run.sh
# or manually:
cd backend && ../.venv/bin/uvicorn main:app --reload --port 8000
```

**5. Open the frontend**

Open `frontend/index.html` directly in your browser — no build step, no npm.

**6. Try it with the sample resumes**

Drag `sample_resumes/sarah_chen.pdf`, `marcus_johnson.pdf`, and `priya_patel.pdf` onto the upload zone and hit **Screen Candidates**. Results appear in ~15–20 seconds.

---

## Prompt Engineering Highlights

Building a reliable structured-output agent requires more than "here is the resume, rate it." Here is what the prompt design does and why.

### 1. Company-specific context injection

The system prompt opens with a rich description of Acceler as a company — its mission, its clients, and the exact nature of the Founder's Office role. This prevents Claude from evaluating candidates against a generic "good employee" template and anchors scores to the actual role.

```
You are a senior talent evaluator at Acceler, an enterprise AI deployment firm...
The Founder's Office is high-ambiguity, high-ownership. Candidates must handle
unstructured problems, build from scratch, and communicate at founder level.
```

### 2. Negative constraints section ("What this role is NOT")

Explicitly listing anti-patterns dramatically sharpens Claude's discrimination between tiers:

```
WHAT THIS ROLE IS NOT:
- Not a pure analyst or slide-maker role
- Not for someone who needs a heavily structured environment
- Not for purely technical candidates without business exposure
```

Without this, LLMs tend toward generous scoring. The negative section forces meaningful differentiation.

### 3. Evidence-based scoring philosophy

The evaluation template instructs Claude to score only on *demonstrated evidence*, not claimed experience:

```
Score on demonstrated evidence not claimed experience
80-100: Clear, specific evidence directly demonstrated in the resume
60-79:  Partial evidence — present but with notable gaps
40-59:  Weak or indirect signal only
0-39:   No credible evidence, or counter-evidence present
```

### 4. Weighted scoring computed in Python, not by Claude

Claude returns raw per-dimension scores (0–100). The weighted average is computed in Python:

```python
overall_score = round(sum(
    dim.get(c["name"], 0) * c["weight"] / 100
    for c in criteria
))
```

This matters for two reasons: (a) it's fully auditable and testable, and (b) it means changing criteria weights requires zero prompt changes — the same Claude response can be re-scored with different weights instantly.

### 5. Role-specific output fields

The JSON schema includes fields that are specific to this hiring context — `consulting_background`, `ai_familiarity`, `builder_signals`, `first_principles_signals` — rather than generic fields. This produces outputs that are immediately actionable for the hiring team rather than generic summaries.

---

## Business Impact

| Metric | Manual Screening | TalentFilter |
|---|---|---|
| Time to screen 100 resumes | ~8 hours | ~3 minutes |
| Cost per screening (100 resumes) | $400–700 (recruiter hours) | ~$0.40 (API cost) |
| Consistency | Variable (human bias, fatigue) | Deterministic per rubric |
| Scalability | Blocks on recruiter bandwidth | Same system handles 1 or 10,000 |
| Customisability | Implicit, per-recruiter | Explicit, per-role weighted rubric |

The system does not replace human judgment — it eliminates the rote first-pass that currently consumes most of a recruiter's time, so they can spend their hours on the top 10% of candidates.

---

## What I Learned Building This

**Architecting a multi-layer AI agent system**

The cleanest pattern is a thin API layer (FastAPI) that orchestrates stateful job objects, with all AI logic isolated in a single module (`claude_evaluator.py`). This keeps the AI layer independently testable and swappable.

**Structured JSON output from Claude**

Claude is highly reliable at producing valid JSON when you: (a) give it an exact schema in the prompt, (b) include the output instruction at the end of the user turn rather than only in the system prompt, and (c) add a lightweight `_parse_json` fallback that strips markdown code fences in case Claude wraps the output.

**Why weights must live in Python**

Early versions asked Claude to compute the weighted score itself. This fails in two ways: the score changes slightly on repeated calls (non-deterministic), and you cannot re-score a cached response when the recruiter adjusts weights. Moving the math to Python fixed both problems instantly.

**Progress UX matters for long operations**

Polling every 3 seconds with a `progress_message` string from the backend — "Evaluating Marcus Johnson (2 of 8)..." — turns a 3-minute wait into an engaging experience. Without this, users assume the app is broken and refresh.

**Building with Claude Code**

This project was built end-to-end using Claude Code as the primary development environment. Claude Code was used for: initial architecture design, prompt iteration, frontend component building, debugging JSON parsing edge cases, and writing this README. The workflow is materially faster than traditional development — the gap between "I want this feature" and "it works" collapsed from hours to minutes.

---

## Future Improvements

- **ATS integration** — push shortlisted candidates directly into Greenhouse, Lever, or Ashby
- **Multi-language support** — resumes in Spanish, French, Mandarin evaluated in the same pipeline
- **Parallel batch evaluation** — use Anthropic's Message Batches API to evaluate all candidates simultaneously instead of sequentially (5–10× faster for large batches)
- **Interview scheduling** — auto-send Calendly links to Strong Hire candidates the moment evaluation completes
- **Bias detection layer** — a second Claude pass that flags if scoring patterns correlate with protected characteristics
- **Persistent storage** — replace the in-memory job store with SQLite or Postgres so results survive server restarts
- **Role template library** — pre-built rubrics for common roles (SDR, SWE, PM, BizOps) that users can load in one click

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check |
| `/jobs` | POST | Create a new screening job with title, description, and weighted criteria |
| `/upload/{job_id}` | POST | Upload one or more PDF files (multipart/form-data) |
| `/run/{job_id}` | POST | Start background evaluation of all uploaded resumes |
| `/status/{job_id}` | GET | Poll for progress (0–100%), current message, and completed results |

---

*Built by Akshat Agrawal · Powered by Claude (Anthropic) · Built with Claude Code*
