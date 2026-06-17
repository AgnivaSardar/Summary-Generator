# TODO

## Router / company_id issue investigation
- [x] Verify FastAPI router registration in `main.py`.
- [x] Verify `api/summary_routes.py` accepts `company_id` and forwards to services.
- [x] Verify `PatientSummaryService.generate()` resolves `company_id` correctly.
- [x] Trace `company_id` usage through context building.
- [x] Identify ingestion gap: `AppointmentFetcher` and `AdmissionFetcher` ignore `company_id`.

## Planned code fixes
- [ ] Update `services/patient_context_service.py` to pass `company_id` into appointment/admission fetchers.
- [ ] Update `ingestion/appointment_fetcher.py` to accept `company_id` and include it in `/appointments` query.
- [ ] Update `ingestion/admission_fetcher.py` to accept `company_id` and include it in `/admissions` query.
- [ ] Run `pytest` and ensure tests pass.

