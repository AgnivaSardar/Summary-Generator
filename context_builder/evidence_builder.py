from models.clinical_fact import ClinicalFact


class EvidenceBuilder:

    def build(
        self,
        facts: list[ClinicalFact]
    ) -> list[str]:

        evidence = []

        facts_sorted = sorted(

            facts,

            key=lambda x:
            x.priority_score,

            reverse=True
        )

        for fact in facts_sorted[:20]:

            if fact.id == "TIMELINE":
                continue

            if fact.category in ["MEDICATION", "ADVICE"]:
                continue

            if fact.id in ["APPOINTMENT_MEDICATION", "ADMISSION_MEDICATION", "APPOINTMENT_ADVICE", "ADMISSION_ADVICE"]:
                continue

            evidence.extend(
                fact.evidence
            )

        return evidence