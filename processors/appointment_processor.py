from models.appointment import Appointment

from models.clinical_fact import (
    ClinicalFact
)

from models.processor_result import (
    ProcessorResult
)

from normalizers.text_cleaner import (
    TextCleaner
)


class AppointmentProcessor:

    def process(
        self,
        appointments:
        list[Appointment]
    ):

        facts = []

        for appointment in appointments:

            if (
                appointment
                .chiefComplaints
            ):

                facts.append(

                    ClinicalFact(

                        fact_id=
                        "COMPLAINT",

                        category=
                        "COMPLAINT",

                        fact=
                        TextCleaner
                        .clean(
                            appointment
                            .chiefComplaints
                        ),

                        severity=
                        "LOW",

                        priority_score=
                        20
                    )
                )

            if (
                appointment
                .diagnosis
            ):

                facts.append(

                    ClinicalFact(

                        fact_id=
                        "DIAGNOSIS",

                        category=
                        "DIAGNOSIS",

                        fact=
                        TextCleaner
                        .clean(
                            appointment
                            .diagnosis
                        ),

                        severity=
                        "MODERATE",

                        priority_score=
                        50
                    )
                )

        return ProcessorResult(

            processor_name=
            "AppointmentProcessor",

            facts=facts
        )