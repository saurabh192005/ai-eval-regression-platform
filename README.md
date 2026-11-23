# AI Model Evaluation & Regression Detection Platform

A web platform that runs repeatable tests against LLMs, measures quality, latency and estimated cost, compares a new run against a baseline, and flags regressions with explainable, configurable rules.

> **Status:** Phases 1-2 complete (backend, database, dataset APIs, evaluation engine). Regression detection and dashboard are in progress.

## Tech stack
Python, FastAPI, SQLAlchemy, Alembic, PostgreSQL, pytest, Docker, Groq API. Planned: React, TypeScript, Vite, Tailwind, Recharts.

## Prerequisites
- Python 3.11+
- Docker Desktop
- Git
- A free Groq API key from [console.groq.com](https://console.groq.com)

## Setup
```bash
git clone https://github.com/saurabh192005/ai-eval-regression-platform.git
cd ai-eval-regression-platform/backend

python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
# source .venv/bin/activate       # macOS/Linux

pip install -r requirements.txt
copy .env.example .env            # cp .env.example .env on macOS/Linux
# then edit .env and set GROQ_API_KEY=<your key>

docker run -d --name evaldb -e POSTGRES_PASSWORD=pass -e POSTGRES_DB=evaldb -p 5432:5432 postgres:16

alembic upgrade head
python -m scripts.seed_benchmark  # loads the 25-case sample benchmark
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs for Swagger UI.

## Environment variables
| Variable | Description |
|---|---|
| `DATABASE_URL` | SQLAlchemy URL, e.g. `postgresql+psycopg://postgres:pass@localhost:5432/evaldb` |
| `GROQ_API_KEY` | Groq API key. Keep it in `.env`, never commit it |

## Run tests
```bash
cd backend
pytest -v
```

## Usage
1. `GET /api/v1/datasets` and note the `id` of `basic-benchmark`.
2. Start a run (returns 202 immediately, runs in the background):
```bash
curl -X POST http://127.0.0.1:8000/api/v1/evaluations \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 1, "model_name": "openai/gpt-oss-20b"}'
```
3. Poll `GET /api/v1/evaluations/{id}` until `status` is `completed`.
4. Read `GET /api/v1/evaluations/{id}/metrics` and `/results`.

Create your own dataset:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/datasets \
  -H "Content-Type: application/json" \
  -d '{"name": "my-dataset", "description": "demo"}'

curl -X POST http://127.0.0.1:8000/api/v1/datasets/1/test-cases \
  -H "Content-Type: application/json" \
  -d '[{"input_text": "What is 2+2? Answer with just the number.", "expected_output": "4"}]'
```

## Endpoints
| Method | Path | Description |
|---|---|---|
| GET | `/health` | Service health |
| GET | `/health/db` | Database connectivity |
| POST | `/api/v1/datasets` | Create dataset |
| GET | `/api/v1/datasets` | List datasets |
| GET | `/api/v1/datasets/{id}` | Get dataset |
| POST | `/api/v1/datasets/{id}/test-cases` | Add test cases |
| GET | `/api/v1/datasets/{id}/test-cases` | List test cases |
| POST | `/api/v1/evaluations` | Start an evaluation run |
| GET | `/api/v1/evaluations/{id}` | Run status and metadata |
| GET | `/api/v1/evaluations/{id}/results` | Per-test-case results |
| GET | `/api/v1/evaluations/{id}/metrics` | Aggregated metrics |

## Metrics
| Metric | Meaning |
|---|---|
| `correctness_rate` | Share of answered cases that match the expected output (exact match, evaluator `exact_match_v2`) |
| `error_rate` | Share of cases where the provider call failed. Failures are never counted as wrong answers |
| `latency_ms_avg / median / p95` | End-to-end provider call time |
| `total_tokens` | Provider-reported input + output tokens |
| `estimated_cost_usd` | Estimated from token counts and a dated price table (`app/core/pricing.py`) |

## Project structure
```
backend/
  app/
    api/v1/        # route handlers
    core/          # settings, pricing
    db/            # engine, session
    evaluators/    # exact match, metrics
    models/        # SQLAlchemy entities
    providers/     # LLM provider adapter (Groq)
    schemas/       # Pydantic models
    services/      # evaluation run logic
  alembic/         # migrations
  scripts/         # seed script
  tests/
datasets/          # sample benchmark
docs/              # schema and API docs
```

## Roadmap
- [x] Phase 1: Backend foundation and database
- [x] Phase 2: Evaluation engine
- [ ] Phase 3: Baseline comparison and regression detection
- [ ] Phase 4: React dashboard
- [ ] Phase 5: Integration, CI and deployment

## Known limitations
- Exact-match scoring only suits short, deterministic answers. Open-ended tasks need a different evaluator.
- LLM outputs can vary between runs, so small differences on a 25-case benchmark may be noise.
- Costs are estimates, not billed amounts.
- Only one provider (Groq) is supported, and the free tier is rate-limited.

## License
MIT, see [LICENSE](LICENSE).