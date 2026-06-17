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
        from urllib.parse import quote

        patient_id_q = quote(str(patient_id), safe="")
        url = f"{self.api_base_url}/test-results?patientId={patient_id_q}"
        response = requests.get(url)

        print("[DEBUG] TestFetcher URL:", url)
        print("[DEBUG] TestFetcher status:", response.status_code)
        if response.status_code != 200:
            print("[DEBUG] TestFetcher body snippet:", response.text[:1000])

        if response.status_code == 200:

            body = response.json()
            print("[DEBUG] TestFetcher json type:", type(body))
            if isinstance(body, dict):
                print("[DEBUG] TestFetcher json keys:", list(body.keys())[:20])
            if isinstance(body, list):
                print("[DEBUG] TestFetcher list length:", len(body))
            return body

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
