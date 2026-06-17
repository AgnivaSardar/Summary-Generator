from fastapi import APIRouter

from services.patient_context_service import (
    PatientContextService
)

router = APIRouter()


@router.get(
    "/context/{patient_id}"
)
def generate_context(
    patient_id: str
):

    service = (
        PatientContextService()
    )

    context = (
        service.build_context(
            patient_id
        )
    )

    return {
        "patient_id":
        patient_id,

        "context":
        context
    }