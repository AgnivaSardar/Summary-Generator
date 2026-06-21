# AI Clinical Synopsis Service Overview

This project exposes a FastAPI service that turns patient-history data into a physician-facing clinical synopsis. It fetches patient records from an upstream backend, converts raw visits, admissions, and tests into structured clinical facts, builds a deterministic LLM context, generates a synopsis with Gemini or Ollama, validates the response, and posts the synopsis back to the backend.

## Runtime Contract

- `GET /` returns application name, version, and status.
- `GET /api/v1/health` returns service health.
- `GET /api/v1/ping` returns a simple ping response.
- `GET /api/v1/context/{patient_id}` returns the structured context used for synopsis generation.
- `POST /api/v1/summary/{patient_id}` generates a synopsis and posts it to the backend.

The route parameter is declared as a path parameter, so patient IDs containing `/` must be URL encoded by callers.

## Top-Level Files

- `main.py`: creates the FastAPI app, registers health and summary routers, and exposes the root endpoint.
- `requirements.txt`: Python package dependencies for running and testing the service.
- `.env`: local runtime configuration. This file should contain backend URLs, model settings, and optional Gemini credentials. Do not commit secrets.
- `README.md`: short project entry point with links to setup and overview documentation.

## Configuration

`config/settings.py` defines typed settings with `pydantic-settings`.

Required values:

- `API_BASE_URL`: upstream patient-history backend base URL.
- `OLLAMA_URL`: local or remote Ollama base URL.
- `OLLAMA_MODEL`: Ollama model name used when Gemini is not configured.

Optional/defaulted values:

- `APP_NAME`: defaults to `AI Clinical Synopsis Service`.
- `APP_VERSION`: defaults to `1.0.0`.
- `DEFAULT_COMPANY_ID`: defaults to `00262`.
- `SYNOPSIS_UPDATE_URL`: overrides the default synopsis update endpoint.
- `SYNOPSIS_UPDATE_TIMEOUT_SECONDS`: defaults to `30`.
- `GEMINI_API_KEY`: when set, generation uses Gemini instead of Ollama.
- `GEMINI_MODEL`: defaults to `gemini-3.1-flash-lite`.
- `LOG_LEVEL`: defaults to `INFO`.

`config/constants.py` and `config/logging_config.py` hold shared constants and logging setup.

## API Layer

`api/health_routes.py` defines lightweight operational endpoints:

- `GET /api/v1/health`
- `GET /api/v1/ping`

`api/summary_routes.py` defines the main product endpoints:

- `GET /api/v1/context/{patient_id:path}` builds and returns structured patient context.
- `POST /api/v1/summary/{patient_id:path}` builds context, generates the synopsis, posts it to the backend, and returns the generated summary.

The summary route includes an in-memory rate limiter with defaults of 5 requests per minute and 20 requests per day per running process.

## Ingestion Layer

The fetchers in `ingestion/` adapt upstream API responses into internal dataclass models.

- `patient_fetcher.py`: calls `GET /patient-details?patientId=...&companyId=...` and returns a `Patient`.
- `test_fetcher.py`: calls `GET /test-results?patientId=...` and returns `TestResult` records.
- `appointment_fetcher.py`: calls `GET /appointments?patientId=...` and returns `Appointment` records.
- `admission_fetcher.py`: calls `GET /admissions?patientId=...` and returns `Admission` records.

These fetchers parse ISO dates and `dd-mm-yyyy` dates, URL-encode patient IDs where needed, and raise exceptions for non-200 upstream responses.

## Models

`models/` contains dataclasses passed between pipeline layers.

- `patient.py`: patient demographics and identifiers.
- `test_result.py`: test name, date, result, and reference range.
- `appointment.py`: appointment date, complaints, diagnosis, examination, medications, and advice.
- `admission.py`: admission details, diagnosis, hospital course, medications, and advice.
- `clinical_fact.py`: normalized evidence-backed fact used by processors, context builders, analyzers, and LLM prompts.
- `processor_result.py`: processor output envelope containing facts and related processing data.
- `patient_context.py`: structured context model helpers.

## Normalizers and Parsers

`normalizers/` and `parsers/` clean raw clinical text and extract structured values.

- `text_cleaner.py`: cleans noisy text.
- `test_name_normalizer.py`: maps test names through `knowledge/test_dictionary.json`.
- `medicine_normalizer.py` and `medicine_parser.py`: normalize and clean medication strings.
- `diagnosis_normalizer.py`: maps diagnosis synonyms through `knowledge/diagnosis_dictionary.json`.
- `test_value_parser.py`: extracts numeric and textual test values.
- `range_parser.py`: parses reference ranges.

## Analyzers

`analyzers/` assigns interpretation, severity, priority, and risk signals.

- `abnormality_analyzer.py`: classifies test values against ranges.
- `severity_analyzer.py`: uses severity rules from `knowledge/severity_rules.json` and custom rules.
- `trend_analyzer.py`: detects simple trends in repeated test values.
- `priority_analyzer.py`: ranks facts for downstream context inclusion.
- `risk_analyzer.py`: applies compound rules from `knowledge/risk_rules.json`.
- `timeline_analyzer.py` and `evidence_extractor.py`: support timeline/evidence-oriented processing.

## Processors

`processors/` converts fetched records into `ClinicalFact` objects.

- `test_processor.py`: processes labs and test reports, including abnormality, severity, trends, and priorities.
- `appointment_processor.py`: extracts appointment complaints, diagnosis, examination, medication, and advice facts.
- `admission_processor.py`: extracts admission diagnosis, examination, history, hospital course, medication, and advice facts.
- `timeline_processor.py`: produces chronological events from appointments, admissions, and tests.
- `risk_processor.py`: derives risk facts from existing facts.
- `priority_processor.py`: wraps priority handling for processor results.

## Context Builders

`context_builder/` compresses processor output into structured and text context.

- `patient_context_builder.py`: builds the main structured dictionary containing patient details, active problems, risks, timeline, evidence, medication, advice, and pending tests.
- `synopsis_context_builder.py`: renders the structured context into the prompt-ready text block.
- `active_problem_builder.py`, `clinical_timeline_builder.py`, `risk_summary_builder.py`, and `evidence_builder.py`: build focused context sections.

## LLM Layer

`llm/` handles prompt creation, model calls, validation, and formatting.

- `summary_generator.py`: orchestrates context rendering, prompt construction, generation, validation, and final formatting.
- `prompt_template.py`: stores the synopsis prompt and retry prompt.
- `ollama_client.py`: calls `POST {OLLAMA_URL}/api/generate`.
- `gemini_client.py`: calls Google Gemini `generateContent` when `GEMINI_API_KEY` is configured.
- `response_validator.py`: validates numbers and timeline years against the source context.
- `fact_checker.py`: checks generated text against source facts.
- `response_formatter.py`: normalizes final output formatting.
- `deterministic_serializer.py`: creates a deterministic fallback summary when there is no meaningful clinical content.

## Services

`services/` connects the whole workflow.

- `patient_context_service.py`: fetches patient data, runs processors, collects medications/advice/pending tests, and builds structured context.
- `synopsis_generation_service.py`: delegates synopsis creation to `SummaryGenerator`.
- `patient_history_synopsis_client.py`: posts the generated synopsis to the upstream backend.
- `patient_summary_service.py`: end-to-end orchestration for `POST /summary/{patient_id}`.

## Knowledge Data

`knowledge/` contains JSON dictionaries and rule sets used by normalizers and analyzers.

- `test_dictionary.json`
- `medicine_dictionary.json`
- `diagnosis_dictionary.json`
- `severity_rules.json`
- `custom_severity_rules.json`
- `risk_rules.json`

Changes here can alter clinical interpretation, so they should be reviewed carefully.

## Tests and Local Scripts

`tests/` contains script-style checks and regression scenarios.

- `test_ollama.py`: smoke test for a local Ollama server.
- `test_summary_api_generator.py`: calls the running FastAPI summary endpoint.
- `test_summary_generator.py`: directly exercises the summary generator with sample contexts.
- `test_new_features.py`: exercises processors and context builders for newer behavior.
- `test_bela_bhattacharya.py`: full local regression scenario using hand-built patient, appointment, admission, and test data.

Some scripts call live model services, so make sure `.env` and Ollama or Gemini are configured before running them.

## Request Flow

1. Caller sends `POST /api/v1/summary/{patient_id}?company_id=...`.
2. `PatientSummaryService` resolves the company ID.
3. `PatientContextService` fetches patient details, tests, appointments, and admissions from `API_BASE_URL`.
4. Processors convert raw records into clinical facts.
5. Risk, timeline, medication, advice, and pending-test summaries are assembled.
6. `PatientContextBuilder` creates structured context.
7. `SummaryGenerator` renders context text and fills the synopsis prompt.
8. Gemini is used if `GEMINI_API_KEY` exists; otherwise Ollama is used.
9. Validators compare generated output against the source context.
10. `PatientHistorySynopsisClient` posts the synopsis to `SYNOPSIS_UPDATE_URL` or `{API_BASE_URL}/ai-synopsis`.
11. The API returns `patient_id`, `company_id`, and `summary`.

## Operational Notes

- The service is synchronous. Long upstream calls or model calls will hold the request open.
- The in-memory rate limiter resets when the process restarts and is not shared across multiple workers.
- Debug logging currently prints fetched record counts, sample records, prompt previews, and raw model responses.
- The context endpoint is useful for debugging upstream data and processor output without calling the LLM.
- For local usage, see `documentations/Setup.md`.
