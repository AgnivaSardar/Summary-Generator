class SynopsisContextBuilder:

    MAX_PROBLEMS = 100
    MAX_FINDINGS = 100
    MAX_RISKS = 100
    MAX_TIMELINE = 100

    def build(self, context) -> str:

        patient = context.get("patient", {})

        active_problems = (
            context.get("active_problems", [])
            [: self.MAX_PROBLEMS]
        )

        findings = (
            context.get(
                "important_findings",
                context.get("evidence", [])
            )
            [: self.MAX_FINDINGS]
        )

        risks = (
            context.get("risks", [])
            [: self.MAX_RISKS]
        )

        timeline = (
            context.get("timeline", [])
            [-self.MAX_TIMELINE :]
        )

        medication = context.get("medication", "")
        advice = context.get("advice", "")
        pending_tests = context.get("pending_tests", "")

        patient_name = patient.get(
            "patient_name",
            ""
        )

        age = patient.get(
            "age",
            ""
        )

        gender = patient.get(
            "gender",
            ""
        )

        cleaned_findings = []

        for finding in findings:

            text = str(finding)

            text = text.replace(
                "trend:",
                "values:"
            )

            text = text.replace(
                "Trend:",
                "Values:"
            )

            text = text.replace(
                "increasing:",
                "values:"
            )

            text = text.replace(
                "Increasing:",
                "Values:"
            )

            text = text.replace(
                "decreasing:",
                "values:"
            )

            text = text.replace(
                "Decreasing:",
                "Values:"
            )

            cleaned_findings.append(
                text
            )

        sections = []

        sections.append(
            f"PATIENT: {patient_name} | {age} | {gender}"
        )

        if active_problems:

            sections.append(
                "PROBLEMS: "
                + "; ".join(
                    str(x).strip()
                    for x in active_problems
                    if str(x).strip()
                )
            )

        if cleaned_findings:

            sections.append(
                "IMPORTANT FINDINGS: "
                + "; ".join(
                    str(x).strip()
                    for x in cleaned_findings
                    if str(x).strip()
                )
            )

        if risks:

            sections.append(
                "RISKS: "
                + "; ".join(
                    str(x).strip()
                    for x in risks
                    if str(x).strip()
                )
            )

        if timeline:

            sections.append(
                "TIMELINE: "
                + "; ".join(
                    str(x).strip()
                    for x in timeline
                    if str(x).strip()
                )
            )

        if medication:

            sections.append(
                f"MEDICATION: {medication}"
            )

        if advice:

            sections.append(
                f"ADVICE: {advice}"
            )

        if pending_tests:

            sections.append(
                f"PENDING TESTS: {pending_tests}"
            )

        return "\n\n".join(sections)
