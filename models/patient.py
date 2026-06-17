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

    # Optional field returned/used by the downstream service.
    # Keeping it in the model avoids missing-attribute issues when
    # serialization/updates are added.
    aiSynopsis: str | None = None


    def age(self) -> int:
        return (
            date.today().year - self.dob.year
        )