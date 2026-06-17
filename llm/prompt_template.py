SYNOPSIS_PROMPT = """
Generate a grounded clinical synopsis from PATIENT DATA only.

Rules:
- Aim for an optimum synopsis around 300 words when enough data exists.
- One paragraph.
- Start with the patient identity in natural language.
- Use the exact patient name from the PATIENT line.
- Use this style when data is available:
  "Mrs. Anita Sharma is a 67-year-old Female with Type 2 Diabetes Mellitus,
  Chronic Kidney Disease Stage 3, and Hypertension..."
- Write a readable clinical paragraph, not a raw copied list.
- Group the paragraph as: patient identity, active problems, important
  findings, listed risks (if present), relevant timeline, medications (if present), and doctor advice (if present).
- Preserve medical terms, years, risks, and numeric values exactly.
- Preserve numeric sequences exactly, including all intermediate values.
- For sequence findings, copy the full sequence exactly as written.
- Do not rewrite "1.1 -> 1.4 -> 1.8 -> 2.3" as "from 1.1 to 2.3".
- Keep risk names exactly, including the word "Risk".
- Example: write "Renal Failure Risk", not "Renal Failure".
- Copy timeline events as complete phrases from TIMELINE.
- Do not assign a year to a condition unless that exact year-condition
  pairing appears in TIMELINE.
- Do not rewrite "2024 CKD progressed to Stage 3" as "CKD Stage 3 in 2024".
- Include the exact numeric values and/or trends of all laboratory tests (e.g. 'GLUCOSE RANDOM value: 142') in the synopsis findings. Do not omit or summarize the numeric values of tests even if the test name or its high/low status is mentioned elsewhere.
- If RISKS is provided in PATIENT DATA, mention it, e.g. "risks include [risks]".
- Do not mention risks or write "risks include" if RISKS is not provided in PATIENT DATA.
- If MEDICATION is provided in PATIENT DATA, mention all listed medications near the end, preserving their dates exactly, e.g. "medications include [medications with dates]".
- Do not mention medications or write "medications include" if MEDICATION is not provided in PATIENT DATA.
- If ADVICE is provided in PATIENT DATA, mention all doctor advice near the end, preserving their dates exactly, e.g. "doctor advice includes [advice with dates]".
- Do not mention doctor advice or write "doctor advice includes" if ADVICE is not provided in PATIENT DATA.
- Do not infer, explain, or add facts.
- Do not use interpretation words such as indicating, suggests,
  likely, possible, evidence of, reflecting, progressive, significant,
  declined, increased, decreased, or history of unless the exact word
  appears in PATIENT DATA.
- You may use light connecting words such as "with", "and", "including",
  "findings include", "risks include", "timeline includes", "medications include",
  and "doctor advice includes".
- For very large or repetitive PATIENT DATA, do not enumerate every item (such as timeline events).
- Select the most important active problems, risks, and timeline items. However, you MUST always include all laboratory test results and their exact values/trends.
- Finish with a complete item or sentence; do not stop mid-value or mid-word.
- Output only the synopsis.

Forbidden unless already present in PATIENT DATA:
indicates, indicating, suggests, suggesting, likely, possible, probable,
appears, consistent with, concerning for, worsening, progressed,
progression, deteriorated, improved, decline, increased, decreased,
elevated, reduced, severe, mild, moderate, significant, recent,
currently, history of, presents with.

Good style (when risks, medications, and advice are present in PATIENT DATA):
Mrs. Anita Sharma is a 67-year-old Female with Type 2 Diabetes Mellitus,
Chronic Kidney Disease Stage 3, and Hypertension. Important findings
include Creatinine values: 1.1 -> 1.4 -> 1.8 -> 2.3 mg/dL and eGFR
values: 62 -> 54 -> 41 -> 33 mL/min. Risks include Renal Failure Risk.
Medications include Tab A on 01-08-2025 and Cap B on 28-11-2025. Doctor
advice includes LFT on 01-08-2025 and daily walk on 28-11-2025.

Good style (when risks, medications, and advice are absent in PATIENT DATA):
Mrs. Anita Sharma is a 67-year-old Female with Type 2 Diabetes Mellitus,
Chronic Kidney Disease Stage 3, and Hypertension. Important findings
include Creatinine values: 1.1 -> 1.4 -> 1.8 -> 2.3 mg/dL and eGFR
values: 62 -> 54 -> 41 -> 33 mL/min.

Bad style:
Creatinine increased from 1.1 to 2.3 mg/dL. Renal Failure is present.
CKD Stage 3 in 2025.
CKD Stage 3 in 2024.

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
Aim for an optimum synopsis around 300 words when enough data exists.
One paragraph. Start with patient identity in natural language.
Write a readable clinical paragraph, not a raw copied list.
Use the exact patient name from the PATIENT line.
Group the paragraph as: patient identity, active problems, important
findings, listed risks (if present), relevant timeline, medications (if present), and doctor advice (if present).
Copy exact medical terms, dates, risks, numeric values, and sequences
where possible. Do not infer, explain, summarize sequences, change
numbers, drop intermediate values, or add facts.
Keep risk names exactly, including the word "Risk".
Do not rewrite sequences as "from X to Y"; copy the full sequence.
Copy timeline events as complete phrases from TIMELINE.
Do not assign a year to a condition unless that exact year-condition
pairing appears in TIMELINE.
Do not rewrite "2024 CKD progressed to Stage 3" as "CKD Stage 3 in 2024".
Include the exact numeric values and/or trends of all laboratory tests (e.g. 'GLUCOSE RANDOM value: 142') in the synopsis findings. Do not omit or summarize the numeric values of tests even if the test name or its high/low status is mentioned elsewhere.
If RISKS is provided in PATIENT DATA, mention it, e.g. "risks include [risks]".
Do not mention risks if RISKS is not provided in PATIENT DATA.
If MEDICATION is provided in PATIENT DATA, mention all listed medications near the end, preserving their dates exactly, e.g. "medications include [medications with dates]".
Do not mention medications if MEDICATION is not provided in PATIENT DATA.
If ADVICE is provided in PATIENT DATA, mention all doctor advice near the end, preserving their dates exactly, e.g. "doctor advice includes [advice with dates]".
Do not mention doctor advice if ADVICE is not provided in PATIENT DATA.
Do not use interpretation words such as indicating, suggests, likely,
possible, evidence of, reflecting, progressive, significant, declined,
increased, decreased, or history of unless the exact word appears in
PATIENT DATA.
For very large or repetitive PATIENT DATA, do not enumerate every item. However, you MUST always include all laboratory test results and their exact values/trends.
Finish with a complete item or sentence. Output only the synopsis.

PATIENT DATA:
{context}

CORRECTED SYNOPSIS:
"""
