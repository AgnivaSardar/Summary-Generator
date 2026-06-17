import requests
from datetime import date, datetime

from models.admission import Admission

class AdmissionFetcher:
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    def fetch(self, patient_id):
        return [
            Admission(
                admissionDate=self._parse_date(
                    item.get("admissionDate")
                ),
                desieseDescription=item.get(
                    "desieseDescription",
                    ""
                ),
                onExamination=item.get("onExamination", ""),
                diagnosis=item.get("diagnosis", ""),
                pastHistory=item.get("pastHistory", ""),
                doctorMedicine=item.get("doctorMedicine", ""),
                courseInHospital=item.get("courseInHospital", ""),
                doctorAdvice=item.get("doctorAdvice", "")
            )
            for item in self.fetch_admission_history(patient_id)
        ]

    def fetch_admission_history(self, patient_id):
        from urllib.parse import quote

        patient_id_q = quote(str(patient_id), safe="")
        url = f"{self.api_base_url}/admissions?patientId={patient_id_q}"
        response = requests.get(url)

        print("[DEBUG] AdmissionFetcher URL:", url)
        print("[DEBUG] AdmissionFetcher status:", response.status_code)
        if response.status_code != 200:
            print("[DEBUG] AdmissionFetcher body snippet:", response.text[:1000])

        if response.status_code == 200:

            body = response.json()
            print("[DEBUG] AdmissionFetcher json type:", type(body))
            if isinstance(body, dict):
                print("[DEBUG] AdmissionFetcher json keys:", list(body.keys())[:20])
            if isinstance(body, list):
                print("[DEBUG] AdmissionFetcher list length:", len(body))
            return body

        else:
            raise Exception(f"Failed to fetch admission history: {response.status_code} - {response.text}")

    def _parse_date(self, value):
        if isinstance(value, date):
            return value

        if not value:
            return date.today()

        text = str(value).split("T")[0]

        try:
            return date.fromisoformat(text)
        except ValueError:
            return datetime.strptime(text, "%d-%m-%Y").date()
