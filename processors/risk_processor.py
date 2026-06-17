from models.clinical_fact import (
    ClinicalFact
)

from models.processor_result import (
    ProcessorResult
)

from analyzers.risk_analyzer import (
    RiskAnalyzer
)


class RiskProcessor:

    def process(
        self,
        facts
    ):

        findings = []

        for fact in facts:

            findings.append(
                fact.fact
            )

        risks = (
            RiskAnalyzer()
            .detect_risks(
                findings
            )
        )

        risk_facts = []

        for risk in risks:

            risk_facts.append(

                ClinicalFact(

                    fact_id=
                    f"RISK_{risk}",

                    category=
                    "RISK",

                    fact=risk,

                    severity=
                    "HIGH",

                    priority_score=
                    80
                )
            )

        return ProcessorResult(

            processor_name=
            "RiskProcessor",

            facts=risk_facts
        )