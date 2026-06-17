from dataclasses import dataclass
from datetime import date

@dataclass
class Patient:
    patientId: str
    dob: date
    sex: str
    contactNo: str
    patientName: str
    address: str

    def age(self) -> int:
        return (
            date.today().year - self.dob.year
        )