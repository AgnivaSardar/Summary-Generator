import requests

class PatientFetcher:
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    def fetch_patient_history(self, patient_id, company_id):
        url = f"{self.api_base_url}/patient-details?patientId={patient_id}&companyId={company_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch patient history: {response.status_code} - {response.text}")