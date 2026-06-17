from context_builder.active_problem_builder import (
    ActiveProblemBuilder
)

from context_builder.clinical_timeline_builder import (
    ClinicalTimelineBuilder
)

from context_builder.risk_summary_builder import (
    RiskSummaryBuilder
)

from context_builder.evidence_builder import (
    EvidenceBuilder
)


class PatientContextBuilder:

    def build(
        self,
        patient,
        facts
    ):

        active_problems = (
            ActiveProblemBuilder()
            .build(facts)
        )

        timeline = (
            ClinicalTimelineBuilder()
            .build(facts)
        )

        risks = (
            RiskSummaryBuilder()
            .build(facts)
        )

        evidence = (
            EvidenceBuilder()
            .build(facts)
        )

        return {

            "patient": {

                "patient_id":
                patient.patientId,

                "patient_name":
                patient.patientName,

                "age":
                patient.age(),

                "gender":
                patient.sex
            },

            "active_problems":
            active_problems,

            "risks":
            risks,

            "timeline":
            timeline,

            "evidence":
            evidence
        }