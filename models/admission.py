from dataclasses import dataclass
from datetime import date

@dataclass
class Admission:
    admissionDate: date
    desieseDescription: str
    onExamination: str
    diagnosis: str
    pastHistory: str
    doctorMedicine: str
    courseInHospital: str
    doctorAdvice: str
