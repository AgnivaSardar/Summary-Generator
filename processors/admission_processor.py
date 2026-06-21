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

        admissions_sorted = sorted(
            admissions,
            key=lambda a: a.admissionDate
            if getattr(a, "admissionDate", None) is not None
            else 0
        )

        latest_admission = admissions_sorted[-1] if admissions_sorted else None

        for admission in admissions:

            if admission.diagnosis:

                facts.append(

                    ClinicalFact(

                        id=
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
                        90,

                        evidence=[
                            TextCleaner.clean(admission.diagnosis)
                        ]
                    )
                )

            if getattr(admission, "desieseDescription", ""):

                facts.append(

                    ClinicalFact(

                        id=
                        "ADMISSION_DISEASE_DESC",

                        category=
                        "DIAGNOSIS",

                        fact=
                        TextCleaner
                        .clean(
                            admission
                            .desieseDescription
                        ),

                        severity=
                        "MODERATE",

                        priority_score=
                        80,

                        evidence=[
                            TextCleaner.clean(admission.desieseDescription)
                        ]
                    )
                )

            if getattr(admission, "onExamination", ""):

                facts.append(

                    ClinicalFact(

                        id=
                        "ADMISSION_EXAMINATION",

                        category=
                        "EXAMINATION",

                        fact=
                        TextCleaner
                        .clean(
                            admission
                            .onExamination
                        ),

                        severity=
                        "LOW",

                        priority_score=
                        75,

                        evidence=[
                            TextCleaner.clean(admission.onExamination)
                        ]
                    )
                )

            if (
                admission
                .pastHistory
            ):

                facts.append(

                    ClinicalFact(

                        id=
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
                        90,

                        evidence=[
                            TextCleaner.clean(admission.pastHistory)
                        ]
                    )
                )

            if (
                admission
                .courseInHospital
            ):

                facts.append(

                    ClinicalFact(

                        id=
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
                        95,

                        evidence=[
                            TextCleaner.clean(admission.courseInHospital)
                        ]
                    )
                )

        # Add latest medication and advice.
        if latest_admission:

            if getattr(latest_admission, "doctorMedicine", ""):
                from parsers.medicine_parser import MedicineParser
                translated_med = MedicineParser.clean_and_translate(latest_admission.doctorMedicine)
                facts.append(
                    ClinicalFact(
                        id="ADMISSION_MEDICATION",
                        category="MEDICATION",
                        fact=translated_med,
                        severity="LOW",
                        priority_score=35,
                        evidence=[
                            translated_med
                        ]
                    )
                )

            if getattr(latest_admission, "doctorAdvice", ""):
                facts.append(
                    ClinicalFact(
                        id="ADMISSION_ADVICE",
                        category="ADVICE",
                        fact=TextCleaner.clean(latest_admission.doctorAdvice),
                        severity="LOW",
                        priority_score=30,
                        evidence=[
                            TextCleaner.clean(latest_admission.doctorAdvice)
                        ]
                    )
                )

        return ProcessorResult(

            processor_name=
            "AdmissionProcessor",

            facts=facts
        )
