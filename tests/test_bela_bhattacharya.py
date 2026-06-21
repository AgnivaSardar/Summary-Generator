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
from llm.summary_generator import SummaryGenerator
from llm.prompt_template import SYNOPSIS_PROMPT
from parsers.medicine_parser import MedicineParser
from normalizers.text_cleaner import TextCleaner


def make_test(name, date_str, result, range_str):
    y, m, d = map(int, date_str.split("-"))
    return TestResult(testName=name, testDate=date(y, m, d), testResult=str(result), testRange=range_str)


def _print_context_metrics(patient_context, context_text, prompt):
    try:
        patient_ctx_size = len(str(patient_context))
    except Exception:
        patient_ctx_size = -1

    print("\n===== CONTEXT / PROMPT METRICS =====")
    print(f"Patient Context Size (chars): {patient_ctx_size}")
    print(f"Context Text Size (chars): {len(context_text)}")
    print(f"Total Prompt Size (chars): {len(prompt)}")
    print("====================================")


def run_bela_bhattacharya_synopsis():
    print("Initializing Patient data for Mrs. BELA BHATTACHARYA...")

    # 1. Patient Details
    patient = Patient(
        patientId="NCRI/26/3174",
        dob=date(1951, 5, 21),  # Age 75 relative to 2026
        sex="Female",
        contactNo="9732578398",
        patientName="Mrs BELA BHATTACHARYA",
        address="KALIBARI MORE, GOBARDANGA (M) HABRA-I, P.S.- GOBARDANGA, P.O.- GOABRDANGA, PIN- 743252",
    )

    # 2. Appointment Details (21-05-2026)
    appointments = [
        Appointment(
            appointmentDate=date(2026, 5, 21),
            chiefComplaints=(
                "C/O ABDOMINAL DISTENSION, BLEEDING PV X 2MONTHS. KNOWN DM, HTN, HYPOTHYROID, TAKING MEDS. "
                "NO SIGNIFICANT FAMILY HISTORY. NO ALLERGY. H/O FEMUR # RIGHT 1MONTH BACK, OPERATED."
            ),
            diagnosis="B/L ADNEXAL MASS UNDER EVALUATION",
            onExamination=(
                "C/O ABDOMINAL DISTENSION, BLEEDING PV X 2MONTHS. KNOWN DM, HTN, HYPOTHYROID, TAKING MEDS. "
                "NO SIGNIFICANT FAMILY HISTORY. NO ALLERGY. H/O FEMUR # RIGHT 1MONTH BACK, OPERATED."
            ),
            doctorMedicine=(
                "Tab Galvus Met 50/500 1 tab twice daily\n"
                "Tab Thyronom 50 mcg 1 tab BBF\n"
                "Ensure Protein Powder 1 servings twice daily"
            ),
            doctorAdvice=(
                "CECT TAP\n"
                "USG GUIDED ASPIRATION OF ASCITIC FLUID(DIAGNOSTIC AND THERAPEUTIC, SEND FOR CYTOLOGY AND CELL BLOCK)\n"
                "BLOOD FOR CBC,RFT,PT,APTT,SEROLOGY\n"
                "REFER TO CARDIOLOGY FOR OPINION\n"
                "REFER TO DR A.SEN GEN MED FOR OPINION\n"
                "Blood for FBS before next visit"
            ),
        )
    ]

    # 3. Admission Details (21-05-2026)
    admissions = [
        Admission(
            admissionDate=date(2026, 5, 21),
            desieseDescription=(
                "LARGE BILATERAL ADNEXAL MASS SUGGESTIVE OF POORLY DIFFERENTIATED NEUROENDOCRINE TUMOR"
            ),
            diagnosis=(
                "LARGE BILATERAL ADNEXAL MASS SUGGESTIVE OF POORLY DIFFERENTIATED NEUROENDOCRINE TUMOR"
            ),
            onExamination="C/O ABDOMINAL DISTENSION, BLEEDING PV X 2MONTHS",
            pastHistory=(
                "KNOWN DM,HTN,HYPOTHYROID,TAKING MEDS NO SIGNIFICANT FAMILY HISTORY NO ALLERGY H/O FEMUR # RIGHT 1MONTH BACK, OPERATED"
            ),
            doctorMedicine="",
            courseInHospital=(
                "PATIENT WAS ADMITTED WITH ABDOMINAL DISTENSION. CECT ABDOMEN REPORTED LARGE BILATERAL "
                "ADNEXAL MASS. BIOPSY WAS SUPPORTIVE OF POORLY DIFFERENTIATED NEUROENDOCRINE CARCINOMA. "
                "RYLES TUBE FEEDING WAS STARTED. DJ STENTING WAS DONE IN VIEW OF OBSTRUCTIVE UROPATHY. "
                "CARDIOLOGY REFERRAL WAS DONE IN VIEW OF DEEP VEIN THROMBOSIS AND ADVICE WAS FOLLOWED "
                "ACCORDINGLY. MEDICAL ONCOLOGY REFERRAL WAS DONE AND PATIENT WAS DEEMED NOT FIT FOR ANY "
                "CYTOTOXIC THERAPY. SHE WAS PLANNED OR PALLIATIVE CARE ONLY. LIMB PHYSIOTHERAPY WAS DONE IN "
                "VIEW OF RIGHT HIP SURGERY DONE IN APRIL-2026 (OUTSIDE). NEPHROLOGY REFERRAL WAS DONE IN VIEW "
                "OF DECREASED URINE OUTPUT AND ADVICE WAS FOLLOWED ACCORDINGLY, HER CONDITION HAS "
                "IMPROVED AND SHE IS NOW BEING DISCHARGED IN SYMPTOMATICALLY BETTER CONDITION WITH "
                "FOLLOWING ADVICE."
            ),
            doctorAdvice="NONE",
        )
    ]

    # 4. Lab Test Results
    tests = [
        # --- 21-05-2026 ---
        make_test("UREA", "2026-05-21", 38, "15 - 45"),
        make_test("CREATININE", "2026-05-21", 1.44, "0.57 - 1.11"),
        make_test("SODIUM", "2026-05-21", 138, "136 - 146"),
        make_test("POTASSIUM", "2026-05-21", 2.9, "3.4 - 4.4"),
        make_test("ERYTHROCYTIC", "2026-05-21", 3.62, "4.5 - 6.5"),
        make_test("LEUCOCYTIC", "2026-05-21", 13120, "4000 - 11000"),
        make_test("HAEMOGLOBIN", "2026-05-21", 9.5, "12.0 - 15.0"),
        make_test("PCV", "2026-05-21", 32.6, "40 - 54"),
        make_test("MCH", "2026-05-21", 26.2, "27 - 32"),
        make_test("MCV", "2026-05-21", 90.1, "83 - 101"),
        make_test("MCHC", "2026-05-21", 29.1, "31.5 - 34.5"),
        make_test("NEUTROPHIL", "2026-05-21", 83, "40 - 75"),
        make_test("LYMPHOCYTE", "2026-05-21", 11, "20 - 45"),
        make_test("MONOCYTE", "2026-05-21", 5, "2 - 10"),
        make_test("BASOPHIL", "2026-05-21", 0, "0 - 1"),
        make_test("EOSINOPHIL", "2026-05-21", 1, "1 - 6"),
        make_test("ANC", "2026-05-21", 10889, "2500 - 7500"),
        make_test("AEC", "2026-05-21", 131, "30 - 350"),
        make_test("AMC", "2026-05-21", 656, "200 - 800"),
        make_test("ALC", "2026-05-21", 1443, "800 - 5000"),
        make_test("PLATELET COUNT", "2026-05-21", 2.88, "1.5 - 4.1"),
        make_test("PT TEST PLASMA", "2026-05-21", 14.4, "10 - 15"),
        make_test("PT CONTROL PLASMA", "2026-05-21", 13.0, "11.8 - 11.8"),
        make_test("PT RATIO", "2026-05-21", 1.1, "0.8 - 1.1"),
        make_test("PT INR", "2026-05-21", 1.13, "1.04 - 1.04"),
        make_test("APTT", "2026-05-21", 20.3, "26 - 40"),
        make_test("APTT CONTROL PLASMA", "2026-05-21", 29.0, "31.2 - 31.2"),
        make_test("APTT RATIO", "2026-05-21", 0.7, "1.07 - 1.07"),
        make_test("HIV I/II AB AND P24 AG", "2026-05-21", 0.10, "0.0 - 1.0"),
        make_test("ANTI HCV", "2026-05-21", 0.10, "0.0 - 1.0"),
        make_test("HBSAG", "2026-05-21", 0.10, "0.0 - 1.0"),

        # --- 23-05-2026 ---
        make_test("ERYTHROCYTIC", "2026-05-23", 3.90, "4.5 - 6.5"),
        make_test("LEUCOCYTIC", "2026-05-23", 19410, "4000 - 11000"),
        make_test("HAEMOGLOBIN", "2026-05-23", 10.4, "12.0 - 15.0"),
        make_test("PCV", "2026-05-23", 35.3, "40 - 54"),
        make_test("MCH", "2026-05-23", 26.7, "27 - 32"),
        make_test("MCV", "2026-05-23", 90.5, "83 - 101"),
        make_test("MCHC", "2026-05-23", 29.5, "31.5 - 34.5"),
        make_test("NEUTROPHIL", "2026-05-23", 91, "40 - 75"),
        make_test("LYMPHOCYTE", "2026-05-23", 6, "20 - 45"),
        make_test("MONOCYTE", "2026-05-23", 3, "2 - 10"),
        make_test("BASOPHIL", "2026-05-23", 0, "0 - 1"),
        make_test("EOSINOPHIL", "2026-05-23", 0, "1 - 6"),
        make_test("ANC", "2026-05-23", 17663, "2500 - 7500"),
        make_test("AEC", "2026-05-23", 0, "30 - 350"),
        make_test("AMC", "2026-05-23", 582, "200 - 800"),
        make_test("ALC", "2026-05-23", 1164, "800 - 5000"),
        make_test("PLATELET COUNT", "2026-05-23", 3.20, "1.5 - 4.1"),
        make_test("UREA", "2026-05-23", 48, "15 - 45"),
        make_test("CREATININE", "2026-05-23", 1.64, "0.57 - 1.11"),
        make_test("SODIUM", "2026-05-23", 140, "136 - 146"),
        make_test("POTASSIUM", "2026-05-23", 3.4, "3.4 - 4.4"),

        # --- 24-05-2026 ---
        make_test("CREATININE", "2026-05-24", 1.55, "0.57 - 1.11"),
        make_test("POTASSIUM", "2026-05-24", 3.7, "3.4 - 4.4"),
        make_test("D-DIMER", "2026-05-24", 7927.7, "0 - 200"),

        # --- 25-05-2026 ---
        make_test("ERYTHROCYTIC", "2026-05-25", 3.77, "4.5 - 6.5"),
        make_test("LEUCOCYTIC", "2026-05-25", 22440, "4000 - 11000"),
        make_test("HAEMOGLOBIN", "2026-05-25", 10.1, "12.0 - 15.0"),
        make_test("PCV", "2026-05-25", 34.4, "40 - 54"),
        make_test("MCH", "2026-05-25", 26.8, "27 - 32"),
        make_test("MCV", "2026-05-25", 91.2, "83 - 101"),
        make_test("MCHC", "2026-05-25", 29.4, "31.5 - 34.5"),
        make_test("NEUTROPHIL", "2026-05-25", 89, "40 - 75"),
        make_test("LYMPHOCYTE", "2026-05-25", 7, "20 - 45"),
        make_test("MONOCYTE", "2026-05-25", 4, "2 - 10"),
        make_test("BASOPHIL", "2026-05-25", 0, "0 - 1"),
        make_test("EOSINOPHIL", "2026-05-25", 0, "1 - 6"),
        make_test("ANC", "2026-05-25", 19971, "2500 - 7500"),
        make_test("AEC", "2026-05-25", 0, "30 - 350"),
        make_test("AMC", "2026-05-25", 897, "200 - 800"),
        make_test("ALC", "2026-05-25", 1570, "800 - 5000"),
        make_test("PLATELET COUNT", "2026-05-25", 3.05, "1.5 - 4.1"),
        make_test("UREA", "2026-05-25", 68, "15 - 45"),
        make_test("CREATININE", "2026-05-25", 1.56, "0.57 - 1.11"),
        make_test("SODIUM", "2026-05-25", 141, "136 - 146"),
        make_test("POTASSIUM", "2026-05-25", 3.4, "3.4 - 4.4"),
        make_test("BILIRUBIN TOTAL", "2026-05-25", 0.49, "0.2 - 1.2"),
        make_test("BILIRUBIN DIRECT", "2026-05-25", 0.18, "0.1 - 0.5"),
        make_test("BILIRUBIN INDIRECT", "2026-05-25", 0.31, "0.0 - 1.0"),
        make_test("SGOT/AST", "2026-05-25", 67, "5 - 34"),
        make_test("SGPT/ALT", "2026-05-25", 10, "0 - 55"),
        make_test("ALKALINE PHOSPHATASE", "2026-05-25", 98, "40 - 150"),
        make_test("PROTEIN TOTAL", "2026-05-25", 6.74, "6.0 - 8.0"),
        make_test("ALBUMIN", "2026-05-25", 3.59, "3.2 - 4.6"),
        make_test("GLOBULIN", "2026-05-25", 3.15, "2.0 - 3.2"),

        # --- 26-05-2026 ---
        make_test("CREATININE", "2026-05-26", 1.65, "0.57 - 1.11"),
        make_test("HAEMOGLOBIN", "2026-05-26", 9.6, "12.0 - 15.0"),
        make_test("LEUCOCYTIC", "2026-05-26", 20110, "4000 - 11000"),
        make_test("NEUTROPHIL", "2026-05-26", 89, "40 - 75"),
        make_test("LYMPHOCYTE", "2026-05-26", 7, "20 - 45"),
        make_test("MONOCYTE", "2026-05-26", 4, "2 - 10"),
        make_test("EOSINOPHIL", "2026-05-26", 0, "1 - 6"),
        make_test("BASOPHIL", "2026-05-26", 0, "0 - 1"),
        make_test("PLATELET COUNT", "2026-05-26", 3.10, "1.5 - 4.1"),
        make_test("POTASSIUM", "2026-05-26", 3.4, "3.4 - 4.4"),
        make_test("SODIUM", "2026-05-26", 142, "136 - 146"),

        # --- 29-05-2026 ---
        make_test("CREATININE", "2026-05-29", 1.44, "0.57 - 1.11"),
        make_test("UREA", "2026-05-29", 54, "15 - 45"),
        make_test("SODIUM", "2026-05-29", 139, "136 - 146"),
        make_test("POTASSIUM", "2026-05-29", 4.3, "3.4 - 4.4"),
        make_test("ERYTHROCYTIC", "2026-05-29", 3.56, "4.5 - 6.5"),
        make_test("LEUCOCYTIC", "2026-05-29", 15680, "4000 - 11000"),
        make_test("HAEMOGLOBIN", "2026-05-29", 9.6, "12.0 - 15.0"),
        make_test("PCV", "2026-05-29", 32.7, "40 - 54"),
        make_test("MCH", "2026-05-29", 27.0, "27 - 32"),
        make_test("MCV", "2026-05-29", 91.9, "83 - 101"),
        make_test("MCHC", "2026-05-29", 29.4, "31.5 - 34.5"),
        make_test("NEUTROPHIL", "2026-05-29", 87, "40 - 75"),
        make_test("LYMPHOCYTE", "2026-05-29", 10, "20 - 45"),
        make_test("MONOCYTE", "2026-05-29", 2, "2 - 10"),
        make_test("BASOPHIL", "2026-05-29", 0, "0 - 1"),
        make_test("EOSINOPHIL", "2026-05-29", 1, "1 - 6"),
        make_test("ANC", "2026-05-29", 13641, "2500 - 7500"),
        make_test("AEC", "2026-05-29", 156, "30 - 350"),
        make_test("AMC", "2026-05-29", 313, "200 - 800"),
        make_test("ALC", "2026-05-29", 1568, "800 - 5000"),
        make_test("PLATELET COUNT", "2026-05-29", 3.20, "1.5 - 4.1"),

        # --- 30-05-2026 ---
        make_test("TSH", "2026-05-30", 11.8, "0.27 - 4.2"),

        # --- 31-05-2026 ---
        make_test("UREA", "2026-05-31", 51, "15 - 45"),
        make_test("CREATININE", "2026-05-31", 1.58, "0.57 - 1.11"),
        make_test("SODIUM", "2026-05-31", 137, "136 - 146"),
        make_test("POTASSIUM", "2026-05-31", 4.2, "3.4 - 4.4"),
        make_test("ERYTHROCYTIC", "2026-05-31", 3.48, "4.5 - 6.5"),
        make_test("LEUCOCYTIC", "2026-05-31", 19930, "4000 - 11000"),
        make_test("HAEMOGLOBIN", "2026-05-31", 11.3, "12.0 - 15.0"),
        make_test("PCV", "2026-05-31", 31.7, "40 - 54"),
        make_test("MCH", "2026-05-31", 32.5, "27 - 32"),
        make_test("MCV", "2026-05-31", 91.1, "83 - 101"),
        make_test("MCHC", "2026-05-31", 35.6, "31.5 - 34.5"),
        make_test("NEUTROPHIL", "2026-05-31", 91, "40 - 75"),
        make_test("LYMPHOCYTE", "2026-05-31", 4, "20 - 45"),
        make_test("MONOCYTE", "2026-05-31", 4, "2 - 10"),
        make_test("BASOPHIL", "2026-05-31", 0, "0 - 1"),
        make_test("EOSINOPHIL", "2026-05-31", 1, "1 - 6"),
        make_test("ANC", "2026-05-31", 18136, "2500 - 7500"),
        make_test("AEC", "2026-05-31", 199, "30 - 350"),
        make_test("AMC", "2026-05-31", 797, "200 - 800"),
        make_test("ALC", "2026-05-31", 797, "800 - 5000"),
        make_test("PLATELET COUNT", "2026-05-31", 3.10, "1.5 - 4.1"),
        make_test("BILIRUBIN TOTAL", "2026-05-31", 0.47, "0.2 - 1.2"),
        make_test("BILIRUBIN DIRECT", "2026-05-31", 0.14, "0.1 - 0.5"),
        make_test("BILIRUBIN INDIRECT", "2026-05-31", 0.33, "0.0 - 1.0"),
        make_test("SGOT/AST", "2026-05-31", 60, "5 - 34"),
        make_test("SGPT/ALT", "2026-05-31", 11, "0 - 55"),
        make_test("ALKALINE PHOSPHATASE", "2026-05-31", 88, "40 - 150"),
        make_test("PROTEIN TOTAL", "2026-05-31", 5.39, "6.0 - 8.0"),
        make_test("ALBUMIN", "2026-05-31", 2.98, "3.2 - 4.6"),
        make_test("GLOBULIN", "2026-05-31", 2.41, "2.0 - 3.2"),

        # --- 01-06-2026 ---
        make_test("SERUM CALCIUM", "2026-06-01", 10.9, "8.8 - 10.0"),
        make_test("MAGNESIUM", "2026-06-01", 1.80, "1.6 - 2.3"),
        make_test("SERUM PHOSPHORUS", "2026-06-01", 2.33, "2.5 - 4.5"),

        # --- 03-06-2026 ---
        make_test("UREA", "2026-06-03", 60, "15 - 45"),
        make_test("CREATININE", "2026-06-03", 1.58, "0.57 - 1.11"),
        make_test("SODIUM", "2026-06-03", 140, "136 - 146"),
        make_test("POTASSIUM", "2026-06-03", 4.2, "3.4 - 4.4"),

        # Non-numeric test indicators to populate timeline events
        TestResult(
            testName="USG GUIDED TRUCU BIOPSY",
            testDate=date(2026, 5, 22),
            testResult="Large areas of necrosis with focal area shows poorly differentiated malignant neoplasm",
            testRange="",
        ),
        TestResult(
            testName="IHC FINAL DIAGNOSIS PANEL",
            testDate=date(2026, 5, 26),
            testResult=(
                "On immunohistochemistry, the tumor cells are positive for synaptophysin, chromogranin, "
                "CD56 and INSM-1, while negative for Pax-8; supports the impression. Ki-67 proliferation "
                "index is around 80%"
            ),
            testRange="",
        ),
    ]

    # 5. Process Facts (mimicking PatientContextService)
    facts = []

    test_result = TestProcessor().process(tests)
    facts.extend(test_result.facts)

    appointment_result = AppointmentProcessor().process(appointments)
    facts.extend(appointment_result.facts)

    admission_result = AdmissionProcessor().process(admissions)
    facts.extend(admission_result.facts)

    timeline_result = TimelineProcessor().process(appointments, admissions, tests)
    facts.extend(timeline_result.facts)

    risk_result = RiskProcessor().process(facts)
    facts.extend(risk_result.facts)

    # 6. Gather chronological medications and advice
    med_events = []
    for app in appointments:
        if getattr(app, "appointmentDate", None) and getattr(app, "doctorMedicine", "").strip():
            med_events.append((app.appointmentDate, app.doctorMedicine))
    for adm in admissions:
        if getattr(adm, "admissionDate", None) and getattr(adm, "doctorMedicine", "").strip():
            med_events.append((adm.admissionDate, adm.doctorMedicine))
    med_events.sort(key=lambda x: x[0])

    advice_events = []
    for app in appointments:
        if getattr(app, "appointmentDate", None) and getattr(app, "doctorAdvice", "").strip():
            advice_events.append((app.appointmentDate, app.doctorAdvice))
    for adm in admissions:
        if getattr(adm, "admissionDate", None) and getattr(adm, "doctorAdvice", "").strip():
            advice_events.append((adm.admissionDate, adm.doctorAdvice))
    advice_events.sort(key=lambda x: x[0])

    med_strings = []
    for dt, med in med_events:
        dt_str = dt.strftime("%d-%m-%Y")
        cleaned_med = MedicineParser.clean_and_translate(med)
        if cleaned_med:
            med_strings.append(f"{dt_str}: {cleaned_med}")
    all_medications = "; ".join(med_strings)

    advice_strings = []
    for dt, adv in advice_events:
        dt_str = dt.strftime("%d-%m-%Y")
        cleaned_adv = TextCleaner.clean(adv)
        if cleaned_adv:
            advice_strings.append(f"{dt_str}: {cleaned_adv}")
    all_advice = "; ".join(advice_strings)

    # Gather Pending Tests
    pending_set = set()
    for t in tests:
        res = getattr(t, "testResult", None)
        if res is None or not str(res).strip():
            pending_set.add((t.testDate, t.testName))
    pending_tests = sorted(list(pending_set), key=lambda x: x[0])
    pending_strings = []
    for dt, name in pending_tests:
        dt_str = dt.strftime("%d-%m-%Y")
        pending_strings.append(f"{name} on {dt_str}")
    all_pending = "; ".join(pending_strings)

    # 7. Build Structured Patient Context
    patient_context = PatientContextBuilder().build(
        patient=patient,
        facts=facts,
        latest_medicine=all_medications,
        latest_advice=all_advice,
        pending_tests=all_pending,
    )

    print("\n===== STRUCTURED PATIENT CONTEXT =====")
    print(patient_context)

    # 8. Render LLM Context block
    context_text = SynopsisContextBuilder().build(patient_context)
    print("\n===== CONTEXT SENT TO LLM =====")
    print(context_text)

    # Build prompt (like SummaryGenerator.generate) so we can print its size
    prompt = SYNOPSIS_PROMPT.replace("{context}", context_text)
    _print_context_metrics(
        patient_context=patient_context,
        context_text=context_text,
        prompt=prompt,
    )

    print("\n===== PROMPT (preview first 700 chars) =====")
    print(prompt[:700])
    if len(prompt) > 700:
        print("\n===== PROMPT (preview last 700 chars) =====")
        print(prompt[-700:])
    print("============================================")

    # 9. Generate Synopsis via LLM
    print("\nGenerating AI Clinical Synopsis...")
    import time

    try:
        start = time.time()
        summary = SummaryGenerator().generate(patient_context)
        total_wait_s = time.time() - start

        print(f"\nWaiting/Generate Time (wall time): {total_wait_s:.2f}s")
        print("\n===== GENERATED SYNOPSIS =====")
        print(summary)
        print(f"Summary Length: {len(summary)} chars")
        print("===============================")

    except Exception as e:
        print(f"\n[ERROR] Synopsis generation failed: {repr(e)}")
        raise


if __name__ == "__main__":
    run_bela_bhattacharya_synopsis()

