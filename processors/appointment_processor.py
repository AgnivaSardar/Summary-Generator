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

        # Sort by appointmentDate so "latest" items are first.
        # appointmentDate may be a date object; if it's missing, fall back to minimal ordering.
        appointments_sorted = sorted(
            appointments,
            key=lambda a: a.appointmentDate
            if getattr(a, "appointmentDate", None) is not None
            else 0
        )

        latest_appointment = appointments_sorted[-1] if appointments_sorted else None

        for appointment in appointments:

            if (
                appointment
                .chiefComplaints
            ):

                facts.append(

                    ClinicalFact(

                        id=
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
                        20,

                        evidence=[
                            TextCleaner.clean(appointment.chiefComplaints)
                        ]
                    )
                )

            if getattr(appointment, "onExamination", ""):

                facts.append(

                    ClinicalFact(

                        id=
                        "APPOINTMENT_EXAMINATION",

                        category=
                        "EXAMINATION",

                        fact=
                        TextCleaner
                        .clean(
                            appointment
                            .onExamination
                        ),

                        severity=
                        "LOW",

                        priority_score=
                        15,

                        evidence=[
                            TextCleaner.clean(appointment.onExamination)
                        ]
                    )
                )

            if (
                appointment
                .diagnosis
            ):

                facts.append(

                    ClinicalFact(

                        id=
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
                        50,

                        evidence=[
                            TextCleaner.clean(appointment.diagnosis)
                        ]
                    )
                )

        # Add latest medication and advice so they appear in evidence/timeline.
        if latest_appointment:

            if getattr(latest_appointment, "doctorMedicine", ""):
                from parsers.medicine_parser import MedicineParser
                translated_med = MedicineParser.clean_and_translate(latest_appointment.doctorMedicine)
                facts.append(
                    ClinicalFact(
                        id="APPOINTMENT_MEDICATION",
                        category="MEDICATION",
                        fact=translated_med,
                        severity="LOW",
                        priority_score=35,
                        evidence=[
                            translated_med
                        ]
                    )
                )

            if getattr(latest_appointment, "doctorAdvice", ""):
                facts.append(
                    ClinicalFact(
                        id="APPOINTMENT_ADVICE",
                        category="ADVICE",
                        fact=TextCleaner.clean(latest_appointment.doctorAdvice),
                        severity="LOW",
                        priority_score=30,
                        evidence=[
                            TextCleaner.clean(latest_appointment.doctorAdvice)
                        ]
                    )
                )

        return ProcessorResult(

            processor_name=
            "AppointmentProcessor",

            facts=facts
        )
