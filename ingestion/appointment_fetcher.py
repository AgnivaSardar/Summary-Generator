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
        from urllib.parse import quote

        normalized_patient_id = (
            patient_id
            if str(patient_id).startswith("DEM/")
            else f"DEM/{patient_id}"
        )

        patient_id_q = quote(str(normalized_patient_id), safe="")
        url = f"{self.api_base_url}/appointments?patientId={patient_id_q}"
        response = requests.get(url)

        print("[DEBUG] AppointmentFetcher URL:", url)
        print("[DEBUG] AppointmentFetcher status:", response.status_code)
        if response.status_code != 200:
            print("[DEBUG] AppointmentFetcher body snippet:", response.text[:1000])

        if response.status_code == 200:

            body = response.json()
            print("[DEBUG] AppointmentFetcher json type:", type(body))
            if isinstance(body, dict):
                print("[DEBUG] AppointmentFetcher json keys:", list(body.keys())[:20])
            if isinstance(body, list):
                print("[DEBUG] AppointmentFetcher list length:", len(body))
            return body

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
