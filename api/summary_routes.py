from fastapi import APIRouter

from services.patient_context_service import (
    PatientContextService
)

from services.patient_summary_service import (
    PatientSummaryService
)

router = APIRouter()


@router.get(
    "/context/{patient_id:path}"
)
def generate_context(
    patient_id: str,
    company_id: str | None = None
):

    service = (
        PatientContextService()
    )

    context = (
        service.build_context(
            patient_id,
            company_id
        )
    )

    return {
        "patient_id":
        patient_id,

        "context":
        context
    }


@router.post(
    "/summary/{patient_id:path}"
)
def generate_summary(
    patient_id: str,
    company_id: str | None = None
):

    service = (
        PatientSummaryService()
    )

    return (
        service.generate(
            patient_id,
            company_id
        )
    )
