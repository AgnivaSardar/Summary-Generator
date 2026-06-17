import requests

class AppointmentFetcher:
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    def fetch_appointment_history(self, patient_id):
        url = f"{self.api_base_url}/appointments?patientId={patient_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch appointment history: {response.status_code} - {response.text}")