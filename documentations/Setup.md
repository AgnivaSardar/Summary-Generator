# Setup and Run Guide

This guide covers the commands needed to install, configure, run, test, and call the AI Clinical Synopsis Service.

## Prerequisites

- Python 3.10 or newer.
- Access to the upstream patient-history backend used by `API_BASE_URL`.
- Either a local Ollama server and model, or a Gemini API key.

## Install

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks virtualenv activation, run this once for the current terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Environment

Create a `.env` file in the project root:

```env
API_BASE_URL=http://localhost:3000
DEFAULT_COMPANY_ID=00262
SYNOPSIS_UPDATE_URL=
SYNOPSIS_UPDATE_TIMEOUT_SECONDS=30
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.1-flash-lite
LOG_LEVEL=INFO
```

Notes:

- `API_BASE_URL` is required. The service calls this backend for patient details, tests, appointments, admissions, and synopsis updates.
- `DEFAULT_COMPANY_ID` is used when no `company_id` query parameter is supplied.
- `SYNOPSIS_UPDATE_URL` is optional. If blank, the service posts generated synopsis data to `{API_BASE_URL}/ai-synopsis`.
- If `GEMINI_API_KEY` is set, Gemini is used for generation.
- If `GEMINI_API_KEY` is blank, Ollama is used through `OLLAMA_URL` and `OLLAMA_MODEL`.

## Start Ollama

Skip this section when using Gemini.

```powershell
ollama serve
ollama pull qwen3:8b
```

You can quickly verify Ollama:

```powershell
python tests\test_ollama.py
```

## Start the API

```powershell
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Local service URLs:

- Root: `http://localhost:8000/`
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
- Health: `http://localhost:8000/api/v1/health`
- Ping: `http://localhost:8000/api/v1/ping`
- Context generation: `GET http://localhost:8000/api/v1/context/{patient_id}`
- Summary generation: `POST http://localhost:8000/api/v1/summary/{patient_id}`

## Call Examples

Health check:

```powershell
curl.exe http://localhost:8000/api/v1/health
```

Root check:

```powershell
curl.exe http://localhost:8000/
```

Build deterministic context for a patient:

```powershell
curl.exe "http://localhost:8000/api/v1/context/25%2F7?company_id=00262"
```

Generate and persist a synopsis:

```powershell
curl.exe -X POST "http://localhost:8000/api/v1/summary/25%2F7?company_id=00262" -H "Accept: application/json"
```

Patient IDs that contain `/` must be URL encoded. For example, `25/7` becomes `25%2F7`, and `NCRI/26/3174` becomes `NCRI%2F26%2F3174`.

You can also call the summary endpoint through the helper script:

```powershell
$env:THIS_SERVICE_BASE_URL="http://localhost:8000"
$env:PATIENT_ID="25/7"
$env:COMPANY_ID="00262"
python tests\test_summary_api_generator.py
```

## Run Local Test Scripts

Most files under `tests/` are executable smoke or regression scripts:

```powershell
python tests\test_new_features.py
python tests\test_bela_bhattacharya.py
python tests\test_summary_generator.py
```

When using pytest-compatible tests:

```powershell
python -m pytest
```

## Upstream Backend Endpoints Expected

The configured `API_BASE_URL` should expose these endpoints:

- `GET /patient-details?patientId={patient_id}&companyId={company_id}`
- `GET /test-results?patientId={patient_id}`
- `GET /appointments?patientId={patient_id}`
- `GET /admissions?patientId={patient_id}`
- `POST /ai-synopsis` unless `SYNOPSIS_UPDATE_URL` overrides it

The synopsis update payload is:

```json
{
  "patientId": "25/7",
  "companyId": "00262",
  "aiSynopsis": "Generated synopsis text"
}
```

## Troubleshooting

- Missing environment values usually fail during app import because `API_BASE_URL`, `OLLAMA_URL`, and `OLLAMA_MODEL` are required settings.
- If a summary call returns `429`, the in-memory limiter has allowed 15 requests per minute or 500 requests per day for the current process.
- If using Ollama, confirm `OLLAMA_URL` is reachable and the configured model has been pulled.
- If using Gemini, confirm `GEMINI_API_KEY` is present and `GEMINI_MODEL` is valid for the key.
