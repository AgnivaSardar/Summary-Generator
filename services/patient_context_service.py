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
        patient_id: str
    ):

        # --------------------
        # Fetch Data
        # --------------------

        patient = (
            PatientFetcher(
                settings.API_BASE_URL
            ).fetch(patient_id)
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

        # --------------------
        # Process Data
        # --------------------

        facts = []

        test_result = (
            TestProcessor()
            .process(tests)
        )

        facts.extend(
            test_result.facts
        )

        appointment_result = (
            AppointmentProcessor()
            .process(appointments)
        )

        facts.extend(
            appointment_result.facts
        )

        admission_result = (
            AdmissionProcessor()
            .process(admissions)
        )

        facts.extend(
            admission_result.facts
        )

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

        risk_result = (
            RiskProcessor()
            .process(facts)
        )

        facts.extend(
            risk_result.facts
        )

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