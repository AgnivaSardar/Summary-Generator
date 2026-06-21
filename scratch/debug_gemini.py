import sys
import io
import requests
from datetime import date
from pathlib import Path

# Setup PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from models.patient import Patient
from models.admission import Admission
from models.appointment import Appointment
from models.test_result import TestResult
from processors.test_processor import TestProcessor
from processors.appointment_processor import AppointmentProcessor
from processors.admission_processor import AdmissionProcessor
from processors.timeline_processor import TimelineProcessor
from processors.risk_processor import RiskProcessor
from context_builder.patient_context_builder import PatientContextBuilder
from context_builder.synopsis_context_builder import SynopsisContextBuilder
from llm.prompt_template import SYNOPSIS_PROMPT
from config.settings import settings

def make_test(name, date_str, result, range_str):
    y, m, d = map(int, date_str.split("-"))
    return TestResult(testName=name, testDate=date(y, m, d), testResult=str(result), testRange=range_str)

def main():
    patient = Patient(
        patientId="NCRI/26/3174",
        dob=date(1951, 5, 21),
        sex="Female",
        contactNo="9732578398",
        patientName="Mrs BELA BHATTACHARYA",
        address="KALIBARI MORE, GOBARDANGA (M) HABRA-I, P.S.- GOBARDANGA, P.O.- GOABRDANGA, PIN- 743252"
    )

    appointments = [
        Appointment(
            appointmentDate=date(2026, 5, 21),
            chiefComplaints="C/O ABDOMINAL DISTENSION, BLEEDING PV X 2MONTHS...",
            diagnosis="B/L ADNEXAL MASS UNDER EVALUATION",
            onExamination="C/O ABDOMINAL DISTENSION...",
            doctorMedicine="Tab Galvus Met 50/500 1 tab twice daily",
            doctorAdvice="CECT TAP"
        )
    ]

    admissions = [
        Admission(
            admissionDate=date(2026, 5, 21),
            desieseDescription="LARGE BILATERAL ADNEXAL MASS SUGGESTIVE OF POORLY DIFFERENTIATED NEUROENDOCRINE TUMOR",
            diagnosis="LARGE BILATERAL ADNEXAL MASS SUGGESTIVE OF POORLY DIFFERENTIATED NEUROENDOCRINE TUMOR",
            onExamination="C/O ABDOMINAL DISTENSION",
            pastHistory="KNOWN DM,HTN",
            doctorMedicine="",
            courseInHospital="PATIENT WAS ADMITTED WITH ABDOMINAL DISTENSION...",
            doctorAdvice="NONE"
        )
    ]

    tests = [
        make_test("UREA", "2026-05-21", 38, "15 - 45"),
        make_test("CREATININE", "2026-05-21", 1.44, "0.57 - 1.11"),
        make_test("SODIUM", "2026-05-21", 138, "136 - 146"),
        make_test("POTASSIUM", "2026-05-21", 2.9, "3.4 - 4.4")
    ]

    facts = []
    facts.extend(TestProcessor().process(tests).facts)
    facts.extend(AppointmentProcessor().process(appointments).facts)
    facts.extend(AdmissionProcessor().process(admissions).facts)
    facts.extend(TimelineProcessor().process(appointments, admissions, tests).facts)
    facts.extend(RiskProcessor().process(facts).facts)

    patient_context = PatientContextBuilder().build(patient, facts, "Tab Galvus Met 50/500", "CECT TAP", "")
    context_text = SynopsisContextBuilder().build(patient_context)
    prompt = SYNOPSIS_PROMPT.replace("{context}", context_text)

    print(f"DEBUG Prompt length: {len(prompt)} chars")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={settings.GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.0,
            "topP": 0.2,
            "topK": 10,
            "maxOutputTokens": 8192
        }
    }
    
    r = requests.post(url, json=payload)
    print("Status:", r.status_code)
    print("Response JSON:")
    print(r.text)

if __name__ == "__main__":
    main()
