from dataclasses import dataclass, field
from typing import List

from models.clinical_fact import ClinicalFact


@dataclass
class PatientContext:
    patient_id: str
    demographics: List[str] = field(default_factory=list)
    diagnoses: List[str] = field(default_factory=list)
    medications: List[str] = field(default_factory=list)
    active_problems: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    timeline: List[str] = field(default_factory=list)
    facts: List[ClinicalFact] = field(default_factory=list)