# AI Model Evaluation & Regression Detection Platform

A web platform that runs repeatable tests against LLMs, measures quality, latency and estimated cost, compares a new run against a baseline, and flags regressions with explainable, configurable rules.

> **Status:** Phase 1 complete (backend foundation, database, dataset APIs). Evaluation engine, regression detection and dashboard are in progress.

## Tech stack
Python, FastAPI, SQLAlchemy, Alembic, PostgreSQL, pytest, Docker. Planned: React, TypeScript, Vite, Tailwind, Recharts.

## Prerequisites
- Python 3.11+
- Docker Desktop
- Git

## Setup
```bash
git clone https://github.com/saurabh192005/ai-eval-regression-platform.git
cd ai-eval-regression-platform/backend

python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
# source .venv/bin/activate       # macOS/Linux

pip install -r requirements.txt
copy .env.example .env            # cp .env.example .env on macOS/Linux

docker run -d --name evaldb -e POSTGRES_PASSWORD=pass -e POSTGRES_DB=evaldb -p 5432:5432 postgres:16

alembic upgrade head
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs for Swagger UI.

## Environment variables
| Variable | Description |
|---|---|
| `DATABASE_URL` | SQLAlchemy URL, e.g. `postgresql+psycopg://postgres:pass@localhost:5432/evaldb` |

## Run tests
```bash
cd backend
pytest -v
```

## API examples
```bash
# Create a dataset
curl -X POST http://127.0.0.1:8000/api/v1/datasets \
  -H "Content-Type: application/json" \
  -d '{"name": "sample", "description": "demo"}'

# Add test cases
curl -X POST http://127.0.0.1:8000/api/v1/datasets/1/test-cases \
  -H "Content-Type: application/json" \
  -d '[{"input_text": "What is 2+2? Answer with just the number.", "expected_output": "4"}]'
```

## Endpoints (Phase 1)
| Method | Path | Description |
|---|---|---|
| GET | `/health` | Service health |
| GET | `/health/db` | Database connectivity |
| POST | `/api/v1/datasets` | Create dataset |
| GET | `/api/v1/datasets` | List datasets |
| GET | `/api/v1/datasets/{id}` | Get dataset |
| POST | `/api/v1/datasets/{id}/test-cases` | Add test cases |
| GET | `/api/v1/datasets/{id}/test-cases` | List test cases |

## Roadmap
- [x] Phase 1: Backend foundation and database
- [ ] Phase 2: Evaluation engine
- [ ] Phase 3: Baseline comparison and regression detection
- [ ] Phase 4: React dashboard
- [ ] Phase 5: Integration, CI and deployment

## License
MIT, see [LICENSE](LICENSE).