import sys
import io

# Reconfigure stdout/stderr to UTF-8 to handle unicode characters like → on Windows
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import time

from llm.summary_generator import (
    SummaryGenerator
)


def run_test(
    test_name: str,
    context: dict
):

    print(
        "\n" +
        "=" * 80
    )

    print(
        f"RUNNING TEST: {test_name}"
    )

    print(
        "=" * 80
    )

    print(
        f"Context Size: "
        f"{len(str(context))} chars"
    )

    start = time.time()

    try:

        summary = (
            SummaryGenerator()
            .generate(
                context
            )
        )

        total_time = (
            time.time()
            - start
        )

        print(
            "\n===== GENERATED SUMMARY =====\n"
        )

        print(summary)

        print(
            "\n===== METRICS ====="
        )

        print(
            f"Total Time: "
            f"{total_time:.2f}s"
        )

        print(
            f"Summary Length: "
            f"{len(summary)} chars"
        )

    except Exception as e:

        print(
            f"\nERROR: {e}"
        )


# =========================================================
# TEST 1
# SIMPLE PATIENT
# =========================================================

simple_patient = {

    "patient": {

        "patient_name": "Anita Sharma",

        "age": 52,

        "gender": "Female"
    },

    "active_problems": [

        "Diabetes Mellitus",

        "Elevated Creatinine"
    ],

    "risks": [

        "Renal Risk"
    ],

    "timeline": [

        "2024 Diagnosed with Diabetes"
    ],

    "evidence": [

        "Creatinine 1.58 mg/dL"
    ]
}


# =========================================================
# TEST 2
# COMPLEX CKD + DIABETES
# =========================================================

complex_patient = {

    "patient": {

        "patient_name": "Mrs. Anita Sharma",

        "age": 67,

        "gender": "Female"
    },

    "active_problems": [

        "Type 2 Diabetes Mellitus",

        "Chronic Kidney Disease Stage 3",

        "Hypertension",

        "Coronary Artery Disease",

        "Hypothyroidism",

        "Iron Deficiency Anemia",

        "Hyperkalemia",

        "Diabetic Nephropathy",

        "Congestive Heart Failure"
    ],

    "risks": [

        "Renal Failure Risk",

        "Cardiovascular Event Risk",

        "Heart Failure Exacerbation Risk",

        "Hyperkalemia Risk",

        "Anemia Progression Risk"
    ],

    "timeline": [

        "2014 Diagnosed with Type 2 Diabetes Mellitus",

        "2017 Diagnosed with Hypertension",

        "2019 Underwent Coronary Angioplasty",

        "2021 Diagnosed with CKD Stage 2",

        "2022 Creatinine started worsening",

        "2023 Hospitalized for Heart Failure",

        "2024 CKD progressed to Stage 3",

        "2025 Hyperkalemia detected"
    ],

    "evidence": [

        "Creatinine trend: 1.1 → 1.4 → 1.8 → 2.3 mg/dL",

        "eGFR trend: 62 → 54 → 41 → 33 mL/min",

        "HbA1c: 9.4%",

        "Potassium: 6.1 mmol/L",

        "Hemoglobin: 8.7 g/dL",

        "TSH: 11.4 mIU/L",

        "Urine Albumin-Creatinine Ratio: 640 mg/g",

        "NT-proBNP: 3200 pg/mL",

        "Ejection Fraction: 38%",

        "Blood Pressure: 170/100 mmHg"
    ]
}


# =========================================================
# TEST 3
# VERY COMPLEX MULTI-ORGAN PATIENT
# =========================================================

critical_patient = {

    "patient": {

        "patient_name": "Mrs. Anita Sharma",

        "age": 72,

        "gender": "Female"
    },

    "active_problems": [

        "Type 2 Diabetes Mellitus",

        "CKD Stage 4",

        "Heart Failure",

        "Coronary Artery Disease",

        "Atrial Fibrillation",

        "Hypothyroidism",

        "Anemia",

        "Hypertension",

        "Proteinuria",

        "Hyperkalemia",

        "Peripheral Neuropathy",

        "Diabetic Retinopathy"
    ],

    "important_findings": [

        "Creatinine 3.2 mg/dL",

        "eGFR 18 mL/min",

        "HbA1c 10.1%",

        "Potassium 6.5 mmol/L",

        "Hemoglobin 7.9 g/dL",

        "Albuminuria 1400 mg/g",

        "EF 30%",

        "BNP 5100 pg/mL",

        "Blood Pressure 182/108"
    ],

    "risks": [

        "ESRD Risk",

        "Dialysis Requirement Risk",

        "Cardiac Arrest Risk",

        "Acute Heart Failure Risk",

        "Stroke Risk",

        "Hospitalization Risk",

        "Mortality Risk"
    ],

    "timeline": [

        "2010 Diabetes",

        "2013 Hypertension",

        "2015 CAD",

        "2017 Angioplasty",

        "2019 CKD",

        "2021 CHF",

        "2022 Proteinuria",

        "2023 AF",

        "2024 Hyperkalemia",

        "2025 CKD Stage 4"
    ]
}


# =========================================================
# TEST 4
# HUGE STRESS TEST
# =========================================================

stress_patient = {

    "patient": {

        "patient_name": "Rajesh Verma",

        "age": 78,

        "gender": "Male"
    },

    "active_problems": [

        f"Condition {i}"

        for i in range(1, 51)
    ],

    "risks": [

        f"Risk {i}"

        for i in range(1, 21)
    ],

    "timeline": [

        f"Event {i}"

        for i in range(1, 51)
    ],

    "important_findings": [

        f"Finding {i}"

        for i in range(1, 101)
    ]
}


# =========================================================
# RUN TESTS
# =========================================================

if __name__ == "__main__":

    run_test(
        "Simple Patient",
        simple_patient
    )

    run_test(
        "Complex CKD Patient",
        complex_patient
    )

    run_test(
        "Critical Multi-System Patient",
        critical_patient
    )

    run_test(
        "Stress Test Patient",
        stress_patient
    )