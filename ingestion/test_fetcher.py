import requests
from datetime import date, datetime

from models.test_result import TestResult

class TestFetcher:
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    def fetch(self, patient_id):
        return [
            TestResult(
                testName=item.get("testName", ""),
                testDate=self._parse_date(item.get("testDate")),
                testResult=item.get("testResult", ""),
                testRange=item.get("testRange", "")
            )
            for item in self.fetch_test_history(patient_id)
        ]

    def fetch_test_history(self, patient_id):
        url = f"{self.api_base_url}/test-results?patientId={patient_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch test history: {response.status_code} - {response.text}")

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
