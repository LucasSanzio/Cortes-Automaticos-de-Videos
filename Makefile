.PHONY: up down logs dev test lint fmt frontend

up:
docker compose up -d --build

down:
docker compose down -v

logs:
docker compose logs -f api worker

dev:
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
cd backend && pytest -q --maxfail=1 --disable-warnings --cov=app

lint:
ruff check backend/app backend/tests

fmt:
ruff format backend/app backend/tests

frontend:
cd frontend && npm install && npm run dev
