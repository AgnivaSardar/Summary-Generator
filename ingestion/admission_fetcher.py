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
        url = f"{self.api_base_url}/admissions?patientId={patient_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
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
