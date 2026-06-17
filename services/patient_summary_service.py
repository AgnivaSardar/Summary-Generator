from services.patient_context_service import (
    PatientContextService
)

from services.synopsis_generation_service import (
    SynopsisGenerationService
)

from services.patient_history_synopsis_client import (
    PatientHistorySynopsisClient
)

from config.settings import (
    settings
)


class PatientSummaryService:

    def generate(
        self,
        patient_id: str,
        company_id: str | None = None
    ):

        resolved_company_id = (
            company_id
            or settings.DEFAULT_COMPANY_ID
        )

        context = (

            PatientContextService()
            .build_context(
                patient_id,
                resolved_company_id
            )
        )

        summary = (

            SynopsisGenerationService()
            .generate(
                context
            )
        )

        update_result = (
            PatientHistorySynopsisClient(
                settings.API_BASE_URL,
                settings.SYNOPSIS_UPDATE_URL,
                settings.SYNOPSIS_UPDATE_TIMEOUT_SECONDS
            )
            .update_synopsis(
                patient_id,
                resolved_company_id,
                summary
            )
        )

        return {

            "patient_id":
            patient_id,

            "company_id":
            resolved_company_id,

            "summary":
            summary,

            "synopsis_update":
            update_result
        }
