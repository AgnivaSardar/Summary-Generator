import requests


class PatientHistorySynopsisClient:

    def __init__(
        self,
        api_base_url: str,
        update_url: str | None = None,
        timeout_seconds: int = 30
    ):

        self.update_url = (
            update_url
            or f"{api_base_url.rstrip('/')}/ai-synopsis"
        )

        self.timeout_seconds = timeout_seconds

    def update_synopsis(
        self,
        patient_id: str,
        company_id: str,
        synopsis: str
    ):

        payload = {
            "patientId": patient_id,
            "companyId": company_id,
            "aiSynopsis": synopsis
        }

        response = requests.post(
            self.update_url,
            json=payload,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            timeout=self.timeout_seconds
        )

        if not response.ok:
            raise Exception(
                "Failed to update AI synopsis: "
                f"{response.status_code} - {response.text}"
            )

        if not response.text:
            return {
                "status_code": response.status_code,
                "response": None
            }

        try:
            response_body = response.json()
        except ValueError:
            response_body = response.text

        return {
            "status_code": response.status_code,
            "response": response_body
        }
