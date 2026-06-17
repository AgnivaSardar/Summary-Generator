from models.clinical_fact import ClinicalFact


class ClinicalTimelineBuilder:

    def build(
        self,
        facts: list[ClinicalFact]
    ) -> list[str]:

        timeline = []

        for fact in facts:

            if (
                fact.category
                == "TIMELINE"
            ):

                timeline.extend(
                    fact.evidence
                )

        return timeline