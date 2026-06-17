SYNOPSIS_PROMPT = """
You are an information extraction system.

Your task is to generate an EXTRACTIVE medical synopsis.

EXTRACTIVE means:
- Use ONLY information present in PATIENT DATA.
- Do NOT infer, interpret, summarize, explain, or rewrite medical facts.
- Copy laboratory values, diagnoses, risks, and timeline events faithfully.
- Preserve wording whenever possible.

Rules:

1. Maximum 120 words.
2. One paragraph only.
3. Mention the patient.
4. Mention active problems.
5. Mention important findings.
6. Mention listed risks.
7. Mention timeline events.
8. Do NOT add information not present in PATIENT DATA.
9. Do NOT remove intermediate values in sequences.
10. If a finding contains a sequence such as:
      1.1 → 1.4 → 1.8 → 2.3
    reproduce it exactly.
11. Do NOT convert sequences into:
      increased
      decreased
      improved
      worsened
      progressed
      declined
      stable
      rising
      falling
12. Do NOT explain laboratory values.
13. Do NOT infer severity.
14. Do NOT infer risk.
15. Do NOT infer diagnosis.
16. Do NOT infer progression.
17. Do NOT infer causality.
18. Do NOT combine multiple findings into a new statement.
19. Preserve medical terminology exactly.
20. Output only the synopsis.

Forbidden words unless they already appear exactly inside PATIENT DATA:

- indicates
- indicating
- suggests
- suggesting
- likely
- possible
- probable
- appears
- consistent with
- concerning for
- worsening
- worsening of
- progressed
- progression
- deteriorated
- improved
- decline
- increased
- decreased
- elevated
- reduced
- severe
- mild
- moderate
- significant
- recent
- currently
- history of
- presents with

Good example

Input:
Creatinine: 1.1 → 1.4 → 1.8 → 2.3 mg/dL

Correct:
Creatinine: 1.1 → 1.4 → 1.8 → 2.3 mg/dL

Incorrect:
Creatinine increased from 1.1 to 2.3 mg/dL

PATIENT DATA:

{context}

SYNOPSIS:
"""

RETRY_PROMPT = """
The previous synopsis violated one or more rules.

Discard it completely.

Generate a NEW synopsis from PATIENT DATA only.

Requirements:

- Maximum 120 words.
- One paragraph.
- Use ONLY information present in PATIENT DATA.
- Never use information from the previous synopsis.
- Never paraphrase findings.
- Never summarize numeric sequences.
- Never explain findings.
- Never infer diagnosis.
- Never infer severity.
- Never infer progression.
- Never infer causality.
- Never infer risks.
- Never change laboratory values.
- Never remove intermediate values.
- Preserve wording whenever possible.

For every laboratory sequence:

Correct:
1.1 → 1.4 → 1.8 → 2.3

Incorrect:
increased from 1.1 to 2.3

Forbidden words unless they already appear inside PATIENT DATA:

indicates
indicating
suggests
suggesting
likely
possible
probable
appears
consistent with
concerning for
worsening
progression
progressed
declined
improved
increased
decreased
elevated
reduced
history of
currently
recent
presents with

If uncertain, COPY the text exactly from PATIENT DATA.

Return ONLY the corrected synopsis.

PATIENT DATA:

{context}

CORRECTED SYNOPSIS:
"""