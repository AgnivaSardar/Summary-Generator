from models.clinical_fact import ClinicalFact


class RiskSummaryBuilder:

    def build(
        self,
        facts: list[ClinicalFact]
    ) -> list[str]:

        risks = []

        for fact in facts:

            if (
                fact.category
                == "RISK"
            ):

                risks.append(
                    fact.fact
                )

        return risks