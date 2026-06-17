import re


class DeterministicSerializer:

    MAX_WORDS = 300

    @staticmethod
    def build(
        context_text: str
    ) -> str:

        text = context_text

        patient = ""
        problems = ""
        findings = ""
        risks = ""
        timeline = ""

        for line in text.splitlines():

            line = line.strip()

            if line.startswith("PATIENT:"):
                patient = line.replace(
                    "PATIENT:",
                    ""
                ).strip()

            elif line.startswith("PROBLEMS:"):
                problems = line.replace(
                    "PROBLEMS:",
                    ""
                ).strip()

            elif line.startswith(
                "IMPORTANT FINDINGS:"
            ):
                findings = line.replace(
                    "IMPORTANT FINDINGS:",
                    ""
                ).strip()

            elif line.startswith("RISKS:"):
                risks = line.replace(
                    "RISKS:",
                    ""
                ).strip()

            elif line.startswith("TIMELINE:"):
                raw_timeline = line.replace(
                    "TIMELINE:",
                    ""
                ).strip()
                real_events = []
                for event in raw_timeline.split(";"):
                    event_stripped = event.strip()
                    if event_stripped in ["Appointment:", "Admission:", "Test:", "Appointment", "Admission", "Test"]:
                        continue
                    if event_stripped.startswith("Appointment:") and not event_stripped.replace("Appointment:", "").strip():
                        continue
                    if event_stripped.startswith("Admission:") and not event_stripped.replace("Admission:", "").strip():
                        continue
                    if event_stripped.startswith("Test:") and not event_stripped.replace("Test:", "").strip():
                        continue
                    real_events.append(event_stripped)
                timeline = "; ".join(real_events) if real_events else ""

        summary_parts = []

        if patient:
            # Try to format "Name | Age | Gender" into a natural language sentence,
            # e.g., "Mr. Rohit Sen is a 22-year-old Male."
            patient_parts = [p.strip() for p in patient.split("|")]
            if len(patient_parts) == 3:
                name, age, gender = patient_parts
                summary_parts.append(
                    f"{name} is a {age}-year-old {gender}."
                )
            else:
                summary_parts.append(
                    f"{patient}."
                )

        if problems:
            summary_parts.append(
                f"Active problems include {problems}."
            )

        if findings:
            summary_parts.append(
                f"Important findings include {findings}."
            )

        if risks:
            summary_parts.append(
                f"Risks include {risks}."
            )

        if timeline:
            timeline_part = (
                f"Timeline includes {timeline}."
            )

            candidate = " ".join(
                summary_parts
                + [timeline_part]
            )

            if (
                len(candidate.split())
                <= DeterministicSerializer.MAX_WORDS
            ):

                summary_parts.append(
                    timeline_part
                )

        summary = " ".join(summary_parts)

        words = summary.split()

        if (
            len(words)
            <= DeterministicSerializer.MAX_WORDS
        ):

            return summary

        return " ".join(
            words[: DeterministicSerializer.MAX_WORDS]
        )
