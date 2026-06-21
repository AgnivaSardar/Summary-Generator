SYNOPSIS_PROMPT = """
Generate a grounded, professional clinical synopsis from PATIENT DATA only.

Structure your output exactly as follows (using markdown headers and bullet points):

# Clinical Synopsis for [Patient Name] ([Age] / [Gender])

## Active Diagnoses & Status
* **Primary**: (Synthesize primary diagnosis, e.g. pelvic mass biopsy results, IHC markers, Ki-67 index).
* **Secondary**: (List secondary chronic diseases and past surgeries with dates).
* **Complications**: (List any complications detected during hospital course, e.g. DVT, obstructive uropathy, DJ stenting).

## Key Lab / Finding Trends
* **Renal**: (Synthesize kidney function findings, highlighting AKI, creatinine peaks, and current status).
* **Hematology**: (Synthesize blood counts, highlighting leukocytosis, absolute neutrophil counts, hemoglobin/anemia).
* **Thyroid**: (Synthesize thyroid status, e.g. TSH levels).
* **Electrolytes/Other**: (Synthesize other key abnormal values, e.g., potassium, sodium, calcium, D-Dimer if not listed elsewhere).

## Plan & Treatment
* **Active Meds**: (List active/discharge medications).
* **Discharge Advice**: (List recommended advice, referrals, and follow-ups).
* **Care Status**: (List oncology referral recommendations, eligibility for chemotherapy, and palliative care plans).

Rules:
- Start with the exact patient name from the PATIENT line.
- Write in a highly synthesized, professional physician tone.
- Do not list normal or stable lab values unless they are clinically relevant.
- Do not use numeric lists (like 1., 2.). Use bullet points (*).
- Preserve exact medical terms, years, and numeric values from the context.
- Output only the synopsis with the headers above.

PATIENT DATA:
{context}

SYNOPSIS:
"""

RETRY_PROMPT = """
Previous synopsis failed validation.

VALIDATION ERROR:
{error}

PREVIOUS SYNOPSIS:
{previous_synopsis}

Return a corrected grounded clinical synopsis from PATIENT DATA only.

Structure your output exactly as follows (using markdown headers and bullet points):

# Clinical Synopsis for [Patient Name] ([Age] / [Gender])

## Active Diagnoses & Status
* **Primary**: (Synthesize primary diagnosis, e.g. pelvic mass biopsy results, IHC markers, Ki-67 index).
* **Secondary**: (List secondary chronic diseases and past surgeries with dates).
* **Complications**: (List any complications detected during hospital course, e.g. DVT, obstructive uropathy, DJ stenting).

## Key Lab / Finding Trends
* **Renal**: (Synthesize kidney function findings, highlighting AKI, creatinine peaks, and current status).
* **Hematology**: (Synthesize blood counts, highlighting leukocytosis, absolute neutrophil counts, hemoglobin/anemia).
* **Thyroid**: (Synthesize thyroid status, e.g. TSH levels).
* **Electrolytes/Other**: (Synthesize other key abnormal values, e.g., potassium, sodium, calcium, D-Dimer if not listed elsewhere).

## Plan & Treatment
* **Active Meds**: (List active/discharge medications).
* **Discharge Advice**: (List recommended advice, referrals, and follow-ups).
* **Care Status**: (List oncology referral recommendations, eligibility for chemotherapy, and palliative care plans).

Rules:
- Start with the exact patient name from the PATIENT line.
- Write in a highly synthesized, professional physician tone.
- Do not list normal or stable lab values unless they are clinically relevant.
- Do not use numeric lists (like 1., 2.). Use bullet points (*).
- Preserve exact medical terms, years, and numeric values from the context.
- Output only the synopsis with the headers above.

PATIENT DATA:
{context}

CORRECTED SYNOPSIS:
"""
