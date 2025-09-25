# Plataforma de Cortes Automáticos de Vídeo

Sistema completo (backend + frontend) para ingestão de vídeos, transcrição, seleção automática de destaques, corte preciso via FFmpeg e disponibilização dos clipes com legendas e miniaturas.

## Visão Geral

- **Backend**: FastAPI, RQ/Redis, FFmpeg, Whisper (fallback local), OpenAI (opcional), Prometheus, logs estruturados.
- **Frontend**: React + Vite + Tailwind, hospedado via Nginx.
- **Armazenamento**: sistema de arquivos local (`/data`).
- **Fila**: Redis + RQ para pipeline assíncrono.

Fluxo principal:
1. Upload de vídeo ou (opcional) envio de URL.
2. Job é criado e enfileirado.
3. Worker executa pipeline: `ffprobe` → `Whisper` → heurística/LLM → cortes via FFmpeg → gera SRT/VTT e thumbnail.
4. API expõe status e links de download; frontend realiza polling.

## Estrutura do Repositório

```
backend/
  app/
    ... módulos FastAPI, workers, storage, vídeo
  tests/
frontend/
  src/
    ... SPA React
```

## Requisitos

- Docker + Docker Compose (uso recomendado).
- FFmpeg instalado localmente (para executar testes).
- Python 3.11 + Node 20 se executar sem Docker.

## Variáveis de Ambiente

Copie `.env.example` para `.env` e ajuste conforme necessidade. Variáveis principais:

- `API_KEY`: chave obrigatória para todas as rotas.
- `REDIS_URL`: apontando para instância Redis.
- `LLM_*`: configurações para seleção via OpenAI (opcional, heurística será usada sem chave).
- `DATA_DIR`: diretório para armazenamento dos arquivos gerados.

## Execução com Docker Compose

```bash
cp .env.example .env
docker compose up -d --build
```

Serviços expostos:
- Backend FastAPI: http://localhost:8000 (Swagger em `/docs`).
- Frontend: http://localhost:3000.
- Redis: porta 6379 (interno).

## Execução Local (sem Docker)

Backend:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Worker:
```bash
python -m app.workers.queue
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Testes e Qualidade

```bash
make test      # pytest com cobertura
make lint      # ruff
make fmt       # ruff format
```

Cobertura mínima de 70% garantida pelos testes existentes (unidade e API). Testes geram vídeos sintéticos via FFmpeg.

## API

Requer header `X-API-Key`. Rotas principais:

- `POST /jobs`: upload multipart (`file`) ou JSON com `source_url` (somente documentado; backend retorna erro caso `URL_FETCH_ENABLED=false`).
- `GET /jobs/{job_id}`: status, progresso e links de download dos clipes.
- `POST /jobs/{job_id}/recut`: reutiliza materiais para gerar novos cortes.
- `DELETE /jobs/{job_id}`: remove job.
- `GET /health`, `GET /metrics`.

Erros seguem formato `{ "code": "...", "message": "..." }`.

## Frontend

SPA em React com páginas:
- Upload/URL de vídeo.
- Progresso com polling a cada 5s.
- Resultados com player e botões de download.

Configuração via variáveis Vite:
- `VITE_API_URL`
- `VITE_API_KEY`

## Observabilidade

- Logs JSON com `structlog`.
- Métricas Prometheus expostas via `prometheus-fastapi-instrumentator`.
- Endpoint `/health` com status do Redis e versão do FFmpeg.

## Limitações e Roadmap

- Download de vídeos por URL ainda não implementado (requer ativar `URL_FETCH_ENABLED` e integrar com yt-dlp).
- Armazenamento local; suporte S3 pode ser adicionado via `storage` interface.
- Webhooks documentados mas não implementados neste MVP.
- CI/CD: configure secrets (API keys, registry) antes de habilitar pipelines de build/push.

## Exemplos

```bash
curl -X POST http://localhost:8000/jobs \
  -H "X-API-Key: changeme" \
  -F file=@sample.mp4

curl -H "X-API-Key: changeme" http://localhost:8000/jobs/<JOB_ID>
```

## Licença

Uso educacional/demonstrativo.
