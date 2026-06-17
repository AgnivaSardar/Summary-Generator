from models.clinical_fact import (
    ClinicalFact
)

from models.processor_result import (
    ProcessorResult
)


class TimelineProcessor:

    def process(
        self,
        appointments,
        admissions,
        tests
    ):

        events = []

        from normalizers.text_cleaner import TextCleaner

        for a in appointments:

            events.append({

                "date":
                a.appointmentDate,

                "event":
                f"Appointment: "
                f"{a.diagnosis}"
            })

            if getattr(a, "doctorMedicine", ""):
                from parsers.medicine_parser import MedicineParser
                events.append({
                    "date": a.appointmentDate,
                    "event": f"Medication: {MedicineParser.clean_and_translate(a.doctorMedicine)}"
                })

            if getattr(a, "doctorAdvice", ""):
                events.append({
                    "date": a.appointmentDate,
                    "event": f"Advice: {TextCleaner.clean(a.doctorAdvice)}"
                })

        for a in admissions:

            events.append({

                "date":
                a.admissionDate,

                "event":
                f"Admission: "
                f"{a.diagnosis}"
            })

            if getattr(a, "doctorMedicine", ""):
                from parsers.medicine_parser import MedicineParser
                events.append({
                    "date": a.admissionDate,
                    "event": f"Medication: {MedicineParser.clean_and_translate(a.doctorMedicine)}"
                })

            if getattr(a, "doctorAdvice", ""):
                events.append({
                    "date": a.admissionDate,
                    "event": f"Advice: {TextCleaner.clean(a.doctorAdvice)}"
                })

        for t in tests:

            events.append({

                "date":
                t.testDate,

                "event":
                f"Test: "
                f"{t.testName}"
            })

        events.sort(
            key=lambda x:
            x["date"]
        )

        fact = ClinicalFact(

            id="TIMELINE",

            category="TIMELINE",

            fact="Clinical timeline",

            severity="LOW",

            priority_score=10,

            evidence=[
                e["event"]
                for e in events
            ]
        )

        return ProcessorResult(

            processor_name=
            "TimelineProcessor",

            facts=[fact]
        )
