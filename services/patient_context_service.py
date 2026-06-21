from ingestion.patient_fetcher import (
    PatientFetcher
)

from ingestion.test_fetcher import (
    TestFetcher
)

from ingestion.appointment_fetcher import (
    AppointmentFetcher
)

from ingestion.admission_fetcher import (
    AdmissionFetcher
)

from processors.test_processor import (
    TestProcessor
)

from processors.appointment_processor import (
    AppointmentProcessor
)

from processors.admission_processor import (
    AdmissionProcessor
)

from processors.timeline_processor import (
    TimelineProcessor
)

from processors.risk_processor import (
    RiskProcessor
)

from context_builder.patient_context_builder import (
    PatientContextBuilder
)

from config.settings import settings


class PatientContextService:

    def build_context(
        self,
        patient_id: str,
        company_id: str | None = None
    ):

        # --------------------
        # Fetch Data
        # --------------------

        patient = (
            PatientFetcher(
                settings.API_BASE_URL
            ).fetch(
                patient_id,
                company_id
                or settings.DEFAULT_COMPANY_ID
            )
        )

        tests = (
            TestFetcher(
                settings.API_BASE_URL
            ).fetch(patient_id)
        )

        appointments = (
            AppointmentFetcher(
                settings.API_BASE_URL
            ).fetch(patient_id)
        )

        admissions = (
            AdmissionFetcher(
                settings.API_BASE_URL
            ).fetch(patient_id)
        )

        # Debug: confirm ingestion returned facts for this patient
        print("[DEBUG] Ingestion sizes:")
        print("  tests:", len(tests))
        print("  appointments:", len(appointments))
        print("  admissions:", len(admissions))

        # Print a single sample to verify expected field names
        if tests:
            print("  test sample:", tests[0].__dict__)
        if appointments:
            print("  appointment sample:", appointments[0].__dict__)
        if admissions:
            print("  admission sample:", admissions[0].__dict__)


        # --------------------
        # Process Data
        # --------------------

        facts = []

        try:

            test_result = (
                TestProcessor()
                .process(tests)
            )

            facts.extend(
                test_result.facts
            )

        except Exception as e:
            print("[ERROR] TestProcessor failed:", repr(e))
            raise

        try:

            appointment_result = (
                AppointmentProcessor()
                .process(appointments)
            )

            facts.extend(
                appointment_result.facts
            )

        except Exception as e:
            print("[ERROR] AppointmentProcessor failed:", repr(e))
            raise

        try:

            admission_result = (
                AdmissionProcessor()
                .process(admissions)
            )

            facts.extend(
                admission_result.facts
            )

        except Exception as e:
            print("[ERROR] AdmissionProcessor failed:", repr(e))
            raise

        try:

            timeline_result = (
                TimelineProcessor()
                .process(
                    appointments,
                    admissions,
                    tests
                )
            )

            facts.extend(
                timeline_result.facts
            )

        except Exception as e:
            print("[ERROR] TimelineProcessor failed:", repr(e))
            raise

        try:

            risk_result = (
                RiskProcessor()
                .process(facts)
            )

            facts.extend(
                risk_result.facts
            )

        except Exception as e:
            print("[ERROR] RiskProcessor failed:", repr(e))
            raise

        # --------------------
        # Find All Medications and Advice chronologically
        # --------------------
        med_events = []
        for app in appointments:
            if getattr(app, "appointmentDate", None) and getattr(app, "doctorMedicine", "").strip():
                med_events.append((app.appointmentDate, app.doctorMedicine))
        for adm in admissions:
            if getattr(adm, "admissionDate", None) and getattr(adm, "doctorMedicine", "").strip():
                med_events.append((adm.admissionDate, adm.doctorMedicine))

        med_events.sort(key=lambda x: x[0])

        advice_events = []
        for app in appointments:
            if getattr(app, "appointmentDate", None) and getattr(app, "doctorAdvice", "").strip():
                advice_events.append((app.appointmentDate, app.doctorAdvice))
        for adm in admissions:
            if getattr(adm, "admissionDate", None) and getattr(adm, "doctorAdvice", "").strip():
                advice_events.append((adm.admissionDate, adm.doctorAdvice))

        advice_events.sort(key=lambda x: x[0])

        from parsers.medicine_parser import MedicineParser
        from normalizers.text_cleaner import TextCleaner

        med_strings = []
        for dt, med in med_events:
            dt_str = dt.strftime("%d-%m-%Y")
            cleaned_med = MedicineParser.clean_and_translate(med)
            if cleaned_med:
                med_strings.append(f"{dt_str}: {cleaned_med}")
        all_medications = "; ".join(med_strings)

        advice_strings = []
        for dt, adv in advice_events:
            dt_str = dt.strftime("%d-%m-%Y")
            cleaned_adv = TextCleaner.clean(adv)
            if cleaned_adv:
                advice_strings.append(f"{dt_str}: {cleaned_adv}")
        all_advice = "; ".join(advice_strings)

        # --------------------
        # Find Pending Tests
        # --------------------
        pending_set = set()
        for t in tests:
            res = getattr(t, "testResult", None)
            if res is None or not str(res).strip():
                pending_set.add((t.testDate, t.testName))

        pending_tests = sorted(list(pending_set), key=lambda x: x[0])
        pending_strings = []
        for dt, name in pending_tests:
            dt_str = dt.strftime("%d-%m-%Y")
            pending_strings.append(f"{name} on {dt_str}")
        all_pending = "; ".join(pending_strings)

        # --------------------
        # Build Structured Context
        # --------------------


        structured_context = (

            PatientContextBuilder()
            .build(
                patient,
                facts,
                latest_medicine=all_medications,
                latest_advice=all_advice,
                pending_tests=all_pending
            )
        )

        return structured_context
