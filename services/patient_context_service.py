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
        # Build Structured Context
        # --------------------


        structured_context = (

            PatientContextBuilder()
            .build(
                patient,
                facts
            )
        )

        return structured_context
