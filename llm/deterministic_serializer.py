import re


class DeterministicSerializer:

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
                timeline = line.replace(
                    "TIMELINE:",
                    ""
                ).strip()

        summary_parts = []

        if patient:
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
            summary_parts.append(
                f"Timeline includes {timeline}."
            )

        return " ".join(summary_parts)