from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ClinicalFact:
    id: str
    category: str
    fact: str
    severity: str
    priority_score: int
    evidence: List[str] = field(default_factory=list)
    trend: Optional[str] = None
    source: Optional[str] = None
    risk_tags: List[str] = field(default_factory=list)
    active: bool = True