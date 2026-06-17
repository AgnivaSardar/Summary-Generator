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
