from dataclasses import dataclass
from datetime import date

@dataclass
class Appointment:
    onExamination: str
    doctorMedicine: str
    doctorAdvice: str
    appointmentDate: date
    chiefComplaints: str
    diagnosis: str
