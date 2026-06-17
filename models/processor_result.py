from dataclasses import dataclass, field
from typing import List

from models.clinical_fact import ClinicalFact


@dataclass
class ProcessorResult:
    processor_name: str
    facts: List[ClinicalFact] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    execution_time_ms: int = 0