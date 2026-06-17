import sys
import io
from datetime import date
from pathlib import Path

# Reconfigure stdout/stderr to UTF-8 to handle unicode characters like → on Windows
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Setup PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from models.admission import Admission
from models.appointment import Appointment
from models.test_result import TestResult
from processors.admission_processor import AdmissionProcessor
from processors.appointment_processor import AppointmentProcessor
from processors.test_processor import TestProcessor
from context_builder.synopsis_context_builder import SynopsisContextBuilder
from context_builder.patient_context_builder import PatientContextBuilder


def test_test_processor_with_trends():
    print("Testing TestProcessor with trends...")
    tests = [
        TestResult(
            testName="GLUCOSE RANDOM",
            testDate=date(2025, 3, 28),
            testResult="55",
            testRange="60 - 100"
        ),
        TestResult(
            testName="UREA",
            testDate=date(2025, 3, 28),
            testResult="5",
            testRange="0 - 6"
        ),
        TestResult(
            testName="GLUCOSE RANDOM",
            testDate=date(2025, 3, 28),
            testResult="66",
            testRange="60 - 100"
        )
    ]

    result = TestProcessor().process(tests)
    facts_dict = {f.id: f for f in result.facts}

    assert "TEST_GLUCOSE RANDOM" in facts_dict, "GLUCOSE RANDOM not processed"
    assert "TEST_UREA" in facts_dict, "UREA not processed"

    glucose_fact = facts_dict["TEST_GLUCOSE RANDOM"]
    print("Glucose Evidence:", glucose_fact.evidence)
    assert glucose_fact.evidence == ["GLUCOSE RANDOM trend: 55 → 66"], f"Expected trend, got {glucose_fact.evidence}"

    urea_fact = facts_dict["TEST_UREA"]
    print("Urea Evidence:", urea_fact.evidence)
    assert urea_fact.evidence == ["UREA value: 5"], f"Expected single latest value, got {urea_fact.evidence}"

    print("TestProcessor with trends passed!")


def test_admission_and_appointment_processors_all_fields():
    print("Testing Admission and Appointment processors with all fields...")
    admissions = [
        Admission(
            admissionDate=date(2025, 1, 1),
            desieseDescription="Severe diabetes exacerbation",
            onExamination="BP 140/90, HR 88",
            diagnosis="Diabetes Mellitus",
            pastHistory="Hypertension for 5 years",
            doctorMedicine="Metformin 500mg BD",
            courseInHospital="Improved on IV insulin",
            doctorAdvice="Regular checkup and low sugar diet"
        )
    ]

    appointments = [
        Appointment(
            onExamination="Pulse regular, chest clear",
            doctorMedicine="Metformin 1000mg OD, Amlodipine 5mg",
            doctorAdvice="Avoid fatty foods",
            appointmentDate=date(2025, 2, 1),
            chiefComplaints="Mild fatigue",
            diagnosis="Essential Hypertension"
        )
    ]

    # Test AdmissionProcessor
    adm_result = AdmissionProcessor().process(admissions)
    adm_fact_ids = [f.id for f in adm_result.facts]
    print("Admission Facts IDs:", adm_fact_ids)
    
    assert "ADMISSION_DIAGNOSIS" in adm_fact_ids
    assert "ADMISSION_DISEASE_DESC" in adm_fact_ids
    assert "ADMISSION_EXAMINATION" in adm_fact_ids
    assert "PAST_HISTORY" in adm_fact_ids
    assert "HOSPITAL_COURSE" in adm_fact_ids
    assert "ADMISSION_MEDICATION" in adm_fact_ids
    assert "ADMISSION_ADVICE" in adm_fact_ids

    # Verify evidence list is populated
    for fact in adm_result.facts:
        assert len(fact.evidence) > 0, f"Evidence is empty for admission fact {fact.id}"

    # Test AppointmentProcessor
    app_result = AppointmentProcessor().process(appointments)
    app_fact_ids = [f.id for f in app_result.facts]
    print("Appointment Facts IDs:", app_fact_ids)

    assert "COMPLAINT" in app_fact_ids
    assert "APPOINTMENT_EXAMINATION" in app_fact_ids
    assert "DIAGNOSIS" in app_fact_ids
    assert "APPOINTMENT_MEDICATION" in app_fact_ids
    assert "APPOINTMENT_ADVICE" in app_fact_ids

    # Verify evidence list is populated
    for fact in app_result.facts:
        assert len(fact.evidence) > 0, f"Evidence is empty for appointment fact {fact.id}"

    print("Admission and Appointment processors with all fields passed!")


class DummyPatient:
    def __init__(self):
        self.patientId = "123"
        self.patientName = "Test Patient"
        self.sex = "Male"
    
    def age(self):
        return 40


def test_context_builder():
    print("Testing context builders...")
    patient = DummyPatient()
    
    # Process test data to get facts
    tests = [
        TestResult(
            testName="GLUCOSE RANDOM",
            testDate=date(2025, 3, 28),
            testResult="55",
            testRange="60 - 100"
        )
    ]
    test_facts = TestProcessor().process(tests).facts

    context = PatientContextBuilder().build(
        patient=patient,
        facts=test_facts,
        latest_medicine="Metformin 1000mg OD",
        latest_advice="Drink plenty of water"
    )

    assert context["medication"] == "Metformin 1000mg OD"
    assert context["advice"] == "Drink plenty of water"

    prompt_context = SynopsisContextBuilder().build(context)
    print("Prompt context string:\n", prompt_context)
    
    assert "MEDICATION: Metformin 1000mg OD" in prompt_context
    assert "ADVICE: Drink plenty of water" in prompt_context

    print("Context builders test passed!")


if __name__ == "__main__":
    test_test_processor_with_trends()
    print("-" * 50)
    test_admission_and_appointment_processors_all_fields()
    print("-" * 50)
    test_context_builder()
    print("-" * 50)
    print("ALL TESTS PASSED!")
