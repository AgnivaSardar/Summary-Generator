from collections import defaultdict

from models.test_result import TestResult
from models.clinical_fact import ClinicalFact
from models.processor_result import ProcessorResult

from parsers.test_value_parser import TestValueParser
from parsers.range_parser import RangeParser

from normalizers.test_name_normalizer import (TestNameNormalizer)

from analyzers.abnormality_analyzer import (AbnormalityAnalyzer)
from analyzers.severity_analyzer import (SeverityAnalyzer)
from analyzers.trend_analyzer import (TrendAnalyzer)
from analyzers.priority_analyzer import (PriorityAnalyzer)


class TestProcessor:

    def __init__(self):

        self.normalizer = (TestNameNormalizer())
        self.severity = (SeverityAnalyzer())

    def process(self,tests: list[TestResult]) -> ProcessorResult:
        
        facts = []

        grouped = defaultdict(list)

        for test in tests:

            normalized = (self.normalizer.normalize(test.testName))

            grouped[normalized["canonical_name"]].append(test)

        for (test_name,records) in grouped.items():

            latest = sorted(records, key=lambda x: x.testDate)[-1]
            parsed_value = (TestValueParser.parse(latest.testResult))
            parsed_range = (RangeParser.parse(latest.testRange))

            if (parsed_value["type"]!= "numeric"):
                continue

            value = (parsed_value["value"])

            abnormality = (AbnormalityAnalyzer.analyze(value, parsed_range["min"], parsed_range["max"]))

            severity = (self.severity.analyze_range_based(value, parsed_range["min"], parsed_range["max"]))

            priority = (PriorityAnalyzer.calculate_score(severity, normalized["category"]))

            facts.append(

                ClinicalFact(

                    fact_id=f"TEST_{test_name}",

                    category=
                    normalized["category"],

                    fact=
                    f"{test_name} "
                    f"{abnormality}",

                    severity = severity,

                    priority_score = priority,

                    evidence=[
                        f"Latest value "
                        f"{value}"
                    ]
                )
            )

        return ProcessorResult(

            processor_name=
            "TestProcessor",

            facts=facts
        )