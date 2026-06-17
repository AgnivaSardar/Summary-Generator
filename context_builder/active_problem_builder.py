from models.clinical_fact import ClinicalFact


class ActiveProblemBuilder:

    def build(
        self,
        facts: list[ClinicalFact]
    ) -> list[str]:

        active_facts = []

        for fact in facts:

            if fact.severity in [
                "HIGH",
                "CRITICAL"
            ]:

                active_facts.append(
                    fact
                )

        active_facts.sort(

            key=lambda x:
            x.priority_score,

            reverse=True
        )

        return [

            fact.fact

            for fact in active_facts[:15]
        ]