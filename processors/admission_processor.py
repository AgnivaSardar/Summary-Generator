from models.admission import Admission

from models.clinical_fact import (
    ClinicalFact
)

from models.processor_result import (
    ProcessorResult
)

from normalizers.text_cleaner import (
    TextCleaner
)


class AdmissionProcessor:

    def process(
        self,
        admissions:
        list[Admission]
    ):

        facts = []

        for admission in admissions:

            if admission.diagnosis:

                facts.append(

                    ClinicalFact(

                        fact_id=
                        "ADMISSION_DIAGNOSIS",

                        category=
                        "DIAGNOSIS",

                        fact=
                        TextCleaner
                        .clean(
                            admission
                            .diagnosis
                        ),

                        severity=
                        "HIGH",

                        priority_score=
                        70
                    )
                )

            if (
                admission
                .pastHistory
            ):

                facts.append(

                    ClinicalFact(

                        fact_id=
                        "PAST_HISTORY",

                        category=
                        "HISTORY",

                        fact=
                        TextCleaner
                        .clean(
                            admission
                            .pastHistory
                        ),

                        severity=
                        "LOW",

                        priority_score=
                        30
                    )
                )

            if (
                admission
                .courseInHospital
            ):

                facts.append(

                    ClinicalFact(

                        fact_id=
                        "HOSPITAL_COURSE",

                        category=
                        "COURSE",

                        fact=
                        TextCleaner
                        .clean(
                            admission
                            .courseInHospital
                        ),

                        severity=
                        "LOW",

                        priority_score=
                        25
                    )
                )

        return ProcessorResult(

            processor_name=
            "AdmissionProcessor",

            facts=facts
        )