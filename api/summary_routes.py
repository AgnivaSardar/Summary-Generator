import time
from fastapi import APIRouter, HTTPException, status

from services.patient_context_service import (
    PatientContextService
)

from services.patient_summary_service import (
    PatientSummaryService
)

router = APIRouter()


class RateLimiter:
    def __init__(self, max_rpm: int = 5, max_rpd: int = 20):
        self.max_rpm = max_rpm
        self.max_rpd = max_rpd
        self.request_times = []

    def check_rate_limit(self):
        now = time.time()
        # Filter requests older than 24 hours
        self.request_times = [t for t in self.request_times if now - t < 86400]

        # Check RPD limit
        if len(self.request_times) >= self.max_rpd:
            retry_after = int(86400 - (now - self.request_times[0]))
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded (daily quota: {self.max_rpd} requests). Please retry after {retry_after} seconds."
            )

        # Check RPM limit
        recent_requests = [t for t in self.request_times if now - t < 60]
        if len(recent_requests) >= self.max_rpm:
            retry_after = int(60 - (now - recent_requests[0]))
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded (minute quota: {self.max_rpm} requests). Please retry after {retry_after} seconds."
            )

        # Record the successful request timestamp
        self.request_times.append(now)


rate_limiter = RateLimiter()


@router.get(
    "/context/{patient_id:path}"
)
def generate_context(
    patient_id: str,
    company_id: str | None = None,
    companyId: str | None = None
):
    resolved_company_id = company_id or companyId
    print(f"[DEBUG] generate_context: patient_id={patient_id}, company_id={resolved_company_id}")

    service = (
        PatientContextService()
    )

    context = (
        service.build_context(
            patient_id,
            resolved_company_id
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
    company_id: str | None = None,
    companyId: str | None = None
):
    rate_limiter.check_rate_limit()

    resolved_company_id = company_id or companyId
    print(f"[DEBUG] generate_summary: patient_id={patient_id}, company_id={resolved_company_id}")

    service = (
        PatientSummaryService()
    )

    return (
        service.generate(
            patient_id,
            resolved_company_id
        )
    )
