# TODO

## Router / company_id issue investigation
- [x] Verify FastAPI router registration in `main.py`.
- [x] Verify `api/summary_routes.py` accepts `company_id` and forwards to services.
- [x] Verify `PatientSummaryService.generate()` resolves `company_id` correctly.
- [x] Trace `company_id` usage through context building.
- [x] Identify ingestion gap: `AppointmentFetcher` and `AdmissionFetcher` ignore `company_id`.

## Planned code fixes (after confirming company is only required for patient ingestion)
- [ ] Add support for `companyId` alias in `api/summary_routes.py` (query param compatibility).
- [ ] Add brief debug logging in the route to confirm resolved `company_id`.
- [ ] Run `pytest` and ensure tests pass.


