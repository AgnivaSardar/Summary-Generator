import requests
from datetime import date, datetime

from models.patient import Patient

class PatientFetcher:
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    def fetch(self, patient_id, company_id):
        patient_data = self.fetch_patient_history(
            patient_id,
            company_id
        )

        if isinstance(patient_data, list):
            patient_data = patient_data[0] if patient_data else {}

        return Patient(
            patientId=patient_data.get("patientId", patient_id),
            dob=self._parse_date(patient_data.get("dob")),
            sex=patient_data.get("sex", ""),
            contactNo=patient_data.get("contactNo", ""),
            patientName=patient_data.get("patientName", ""),
            address=patient_data.get("address", "")
        )

    def fetch_patient_history(self, patient_id, company_id):
        url = (
            f"{self.api_base_url}/patient-details?"
            f"patientId={patient_id}&"
            f"companyId={company_id}"
        )

        response = requests.get(url)
        if response.status_code == 200:
            return response.json()

        raise Exception(
            f"Failed to fetch patient history: {response.status_code} - {response.text}"
        )


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
