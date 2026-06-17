import requests
from datetime import date, datetime

from models.appointment import Appointment

class AppointmentFetcher:
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    def fetch(self, patient_id):
        return [
            Appointment(
                onExamination=item.get("onExamination", ""),
                doctorMedicine=item.get("doctorMedicine", ""),
                doctorAdvice=item.get("doctorAdvice", ""),
                appointmentDate=self._parse_date(
                    item.get("appointmentDate")
                ),
                chiefComplaints=item.get("chiefComplaints", ""),
                diagnosis=item.get("diagnosis", "")
            )
            for item in self.fetch_appointment_history(patient_id)
        ]

    def fetch_appointment_history(self, patient_id):
        url = f"{self.api_base_url}/appointments?patientId={patient_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch appointment history: {response.status_code} - {response.text}")

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
