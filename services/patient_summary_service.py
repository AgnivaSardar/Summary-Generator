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

        try:
            context = (
                PatientContextService()
                .build_context(
                    patient_id,
                    resolved_company_id
                )
            )
        except Exception as e:
            print("[ERROR] PatientContextService.build_context failed:", repr(e))
            raise

        try:
            summary = (
                SynopsisGenerationService()
                .generate(
                    context
                )
            )
        except Exception as e:
            print("[ERROR] SynopsisGenerationService.generate failed:", repr(e))
            raise

        return {
            "patient_id": patient_id,
            "company_id": resolved_company_id,
            "summary": summary
        }



