from dataclasses import dataclass
from datetime import date

@dataclass
class TestResult:
    testName: str
    testDate: date
    testResult: str
    testRange: str

    