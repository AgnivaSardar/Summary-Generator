from services.patient_context_service import (
    PatientContextService
)

from services.synopsis_generation_service import (
    SynopsisGenerationService
)


class PatientSummaryService:

    def generate(
        self,
        patient_id: str
    ):

        context = (

            PatientContextService()
            .build_context(
                patient_id
            )
        )

        summary = (

            SynopsisGenerationService()
            .generate(
                context
            )
        )

        return {

            "patient_id":
            patient_id,

            "summary":
            summary
        }