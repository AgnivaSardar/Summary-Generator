
# AI Clinical Synopsis System — Detailed File-Level Overview

This document expands the system overview with explicit, file-level descriptions so engineers and reviewers understand the responsibilities, inputs, outputs, owners, and risks for each major artifact.

---

## Top-level service

**Purpose:** Provide a fast, reliable API that turns a `patient_id` into a physician-facing clinical synopsis.

**Service contract:** `POST /summary/{patient_id}` → `{ summary, facts_used, timing_ms, warnings }`.

**Operational owners:** Core product engineering, clinical informatics, ML engineers (shared).

---

## `main.py`

- Purpose: Application bootstrap and lifecycle manager.
- Responsibilities: Initialize logging, load `settings`, register API routes and middleware, create shared clients (DB, HTTP, Ollama), and start the ASGI server (Uvicorn/Hypercorn).
- When: executed at process start.
- Inputs: environment variables and `config/settings.py` defaults.
- Outputs: running web process exposing the `api/` routes.
- Why this matters: centralizes process-level configuration (timezones, logging levels, feature toggles). Keep heavy work out of `main.py` to avoid slow cold starts.

---

## Environment and dependencies

- `requirements.txt`: pins runtime dependencies. Keep this minimal and pin versions for reproducible CI artifacts.
- `.env`: runtime secrets and environment overrides (never checked in). Typical keys: `OLLAMA_URL`, `OLLAMA_MODEL`, `OLLAMA_TIMEOUT`, `LOG_LEVEL`, `ENVIRONMENT`.

Security note: secrets must be injected at deploy time via the secret manager; never commit API keys.

---

## `config/`

`settings.py`:
- Purpose: Typed settings object (Pydantic) exposing configuration with defaults and validation.
- Key fields: `OLLAMA_URL`, `MODEL_NAME`, `REQUEST_TIMEOUT_MS`, `MAX_CONTEXT_TOKENS`, `HISTORY_DAYS`.
- Best practice: use feature toggles for experimentation and keep environment-specific overrides out of code.

`constants.py`:
- Purpose: Single source of truth for numeric/domain constants used across analyzers and processors (`MAX_FACTS`, `CRITICAL_SCORE`, `DEFAULT_WINDOW_DAYS`).

---

## `api/` (public interface)

`summary_routes.py`:
- Purpose: HTTP endpoint for synopsis generation.
- Responsibilities: request validation (Pydantic schemas), authentication/authorization, request scoping, response formatting, and error mapping.
- Inputs: `patient_id` and optional flags (e.g., `include_evidence`, `verbosity`).
- Outputs: `summary` text plus structured metadata (`facts_count`, `time_ms`, `warnings`).

`patient_routes.py`:
- Purpose: developer and QA endpoints for introspection — raw fetch results, normalized data, intermediate facts, and built context.
- Use cases: clinical review, debugging, and local reproducibility.

Design principle: routes must remain thin; core logic belongs in `services/`.

---

## `services/`

`patient_summary_service.py`:
- Purpose: orchestrator that coordinates the pipeline end-to-end.
- Responsibilities: call fetchers, run normalizers, dispatch processors, run analyzers, build context, call LLM, validate responses, and assemble the final payload.
- Error handling: should return partial results with warnings on non-critical failures (e.g., missing radiology) and fail fast on catastrophic errors (auth failure).

`patient_context_service.py`:
- Purpose: translate scored `ClinicalFact`s into the `PatientContext` object and final prompt.
- Responsibilities: de-duplication, grouping related facts, limiting context size, and generating evidence pointers.

Instrumentation: track time per stage, facts produced per processor, and LLM token counts.

---

## `ingestion/` (adapters)

Design principle: each fetcher is an adapter to one external system and returns typed domain models.

- `patient_fetcher.py`: demographics, identifiers, and encounter metadata. Handles missing identifiers and multiple IDs mapping.
- `diagnosis_fetcher.py`: returns single-source diagnosis entries with codes and free text.
- `medication_fetcher.py`: handles active medications, historic exposures, administration logs, and reconciliation lists.
- `lab_fetcher.py`: returns timestamped `LabResult` entries; includes unit normalization hints. Supports paging or streaming for long histories.
- `pathology_fetcher.py`: pulls finalized pathology reports, IHC markers, and structured conclusions when available.
- `radiology_fetcher.py`: retrieves imaging reports and extracts critical findings (e.g., `pulmonary embolus`, `intracranial hemorrhage`).
- `admission_fetcher.py`: admission/discharge records and acuity markers.
- `procedure_fetcher.py`: discrete procedure events, operative notes and timestamps.

Failure modes: network errors, auth issues, and partial data — fetchers should be resilient and return best-effort data with provenance.

---

## `normalizers/`

Purpose: translate vendor/institution-specific strings into canonical tokens.

- `diagnosis_normalizer.py`: maps text to canonical diagnosis labels and ICD codes where possible. Outputs confidence scores and link to source text.
- `medication_normalizer.py`: normalizes drug names, routes, strengths, and produces canonical drug identifiers.
- `lab_normalizer.py`: canonicalizes lab test names, maps units, and offers converted values to preferred units.

Risks: incorrect normalization leads to systematic misinterpretation. Prefer high-confidence rules and escalate low-confidence matches for review.

---

## `knowledge/` (domain data)

Purpose: centralized clinical knowledge used by normalizers, analyzers, and processors.

- `test_dictionary.json`: canonical lab name mappings and preferred units.
- `diagnosis_dictionary.json`: diagnosis synonym maps and canonical labels.
- `medication_dictionary.json`: medication name maps and strength parsing rules.
- `reference_ranges.json`: age/sex-specific normal ranges and critical thresholds for lab interpretation.
- `severity_rules.json`: rule definitions mapping patterns to severity levels.
- `risk_rules.json`: clinical risk composition rules.

Governance: changes to `knowledge/` must be reviewed by clinical informatics and tracked with changelogs.

---

## `models/`

Purpose: typed Pydantic models that define the shape of data passed between layers.

- `patient.py`: demographics, identifiers, encounter summaries.
- `diagnosis.py`: diagnosis text, codes, onset/offset dates.
- `medication.py`: name, dose, route, frequency, start/stop.
- `lab_result.py`: test name, value, unit, timestamp, reference range pointer.
- `pathology.py` / `radiology.py`: structured report fields with original text.
- `clinical_fact.py`: primary artifact produced by processors. Fields include `fact`, `type`, `severity`, `score`, `evidence`, `first_seen`, `last_seen`, and `source`.
- `processor_result.py`: envelope describing processor output and metrics.

Best practice: use Pydantic validation to fail-fast on malformed inputs.

---

## `analyzers/`

Purpose: score and tag `ClinicalFact`s using deterministic logic.

- `trend_analyzer.py`: fits simple linear/trend heuristics to numeric series and returns `IMPROVING|STABLE|WORSENING` with explanation.
- `abnormality_analyzer.py`: compares values to `reference_ranges.json` and returns `NORMAL|HIGH|LOW|CRITICAL`.
- `severity_analyzer.py`: maps clinical objects into `LOW|MODERATE|HIGH|CRITICAL` severity buckets.
- `priority_analyzer.py`: combines severity, recency, and diagnostic significance to score facts for LLM inclusion.
- `timeline_analyzer.py`: compacts events into readable chronologies for the final synopsis.

Notes: analyzers should be heavily unit-tested and have deterministic outputs to ensure reproducibility.

---

## `processors/`

Purpose: convert normalized records into `ClinicalFact`s — atomic, evidence-backed statements used by context builders.

Contract:
- Input: normalized domain models for the processor's domain.
- Output: `ProcessorResult` containing `ClinicalFact[]`, `errors[]`, and timing metrics.

Key processors (detailed):
- `demographics_processor.py`: returns statements like `75-year-old female` and flags for advanced age.
- `chief_complaint_processor.py`: extracts presenting problems text and timestamps.
- `diagnosis_processor.py`: prioritizes definitive diagnoses and surfaces chronicity and staging information.
- `chronic_condition_processor.py`: synthesizes long-term conditions and indicates control/status.
- `medication_processor.py`: lists current meds, flags omissions and high-risk interactions.
- `admission_processor.py`: summarizes recent admissions and escalation events.
- `procedure_processor.py`: lists key procedural interventions and dates.
- `pathology_processor.py`: extracts final pathology diagnoses, grade, and key IHC markers.
- `radiology_processor.py`: surfaces high-impact imaging findings with dates.
- `oncology_processor.py`: aggregates tumor descriptors, markers, and response info.
- `renal_processor.py`: interprets creatinine/eGFR and produces functional status statements.
- `others...` (cardiology, liver, infection, electrolytes, coagulation): domain-specific fact generation.
- `timeline_processor.py`: creates the patient timeline used in `synopsis_context_builder`.
- `active_problem_processor.py`: produces the top active problems list.
- `risk_processor.py`: outputs compound risk statements (e.g., `High renal progression risk`).
- `priotiy_processor.py` / `priority_processor.py`: final ranking and trimming before context build.

Ownership: clinicians and domain engineers should co-author processor heuristics and approve test fixtures.

---

## `context/`

Purpose: compress and format facts into the LLM prompt.

- `patient_context_builder.py`: collects facts, de-duplicates, groups related entries (labs with diagnoses), and produces `PatientContext` with evidence links.
- `synopsis_context_builder.py`: converts `PatientContext` into the final prompt text per `prompt_template.py`, ensuring token limits are respected and evidence is attached concisely.

Truncation policy: prefer dropping low-priority facts and preserving high-severity, recent evidence.

---

## `llm/`

Purpose: manage LLM communication and safety.

- `ollama_client.py`: network client with timeouts, retries, and optional streaming. Records token usage and latencies.
- `prompt_template.py`: canonical prompt instructions. Version this file and include examples of good/bad outputs for prompt tuning.
- `summary_generator.py`: prepares the prompt, invokes the client, and performs light post-processing (normalize headings, fix whitespace, assert section presence).
- `response_validator.py`: validates clinical completeness (e.g., ensures major diagnoses are present). On failure, either expand the prompt and retry or return a structured warning.

Safety: ensure the validator checks for hallucinations and missing high-evidence diagnoses.

---

## `tests/`

Purpose: validate the pipeline at unit and integration levels.

- Unit tests for processors, normalizers, and analyzers.
- Integration tests for end-to-end flow with mocked fetchers and mocked LLM.
- Regression fixtures for critical patients and edge cases.

CI: run tests on every PR; require clinical sign-off for knowledge changes.

---

## Critical Files to Review First (summary)

- `knowledge/test_dictionary.json`
- `knowledge/reference_ranges.json`
- `analyzers/priority_analyzer.py`
- `processors/diagnosis_processor.py`
- `processors/pathology_processor.py`
- `context/patient_context_builder.py`
- `context/synopsis_context_builder.py`
- `llm/prompt_template.py`
- `llm/summary_generator.py`
- `llm/response_validator.py`

These files are the highest leverage points for clinical correctness, prompt cost, and overall clinician trust.

---

## Performance Targets

- Small patient: 1–3 seconds
- Average patient: 4–8 seconds
- Complex oncology patient: 6–12 seconds

Assumptions: reasonable Ollama throughput and network latency; aggressive caching of stable artifacts improves tail latency.

---

## Developer Guidance

- Add new normalizers/processors with fixtures and unit tests in `tests/`.
- Keep `api/` thin; business rules belong in `services/`.
- Version `knowledge/` files and require clinical review for changes.

---

## One-line summary

This repo is a Clinical Intelligence Engine: transform raw records → prioritized clinical facts → LLM-ready context → physician synopsis.

