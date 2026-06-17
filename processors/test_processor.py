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

            # normalized is expected to be a dict from TestNameNormalizer;
            # guard against unexpected shapes to avoid runtime crashes.
            if isinstance(normalized, dict):
                canonical_name = normalized.get("canonical_name")
                category = normalized.get("category")
            else:
                canonical_name = None
                category = None

            if not canonical_name:
                # fallback: use the raw test name as canonical key
                canonical_name = str(test.testName)

            grouped[canonical_name].append(test)


        for (test_name,records) in grouped.items():

            records_sorted = sorted(records, key=lambda x: x.testDate)
            latest = records_sorted[-1]
            parsed_value = (TestValueParser.parse(latest.testResult))
            parsed_range = (RangeParser.parse(latest.testRange))

            if (parsed_value["type"]!= "numeric"):
                continue

            value = (parsed_value["value"])

            if parsed_range:
                abnormality = (AbnormalityAnalyzer.analyze(value, parsed_range["min"], parsed_range["max"]))
                severity = (
                    self.severity
                    .analyze_range_based(
                        value,
                        parsed_range["min"],
                        parsed_range["max"]
                    )
                )
            else:
                severity = self.severity.analyze_custom(test_name, value)
                if severity == "UNKNOWN":
                    severity = "NORMAL"
                if severity in ["HIGH", "CRITICAL", "MODERATE"]:
                    abnormality = "HIGH"
                else:
                    abnormality = "NORMAL"

            # PriorityAnalyzer expects severity *level* and a category string.
            # SeverityAnalyzer returns a string level (e.g. "LOW", "NORMAL").
            severity_level = severity if isinstance(severity, str) else (
                getattr(severity, "get", lambda *_: None)("level")
                or getattr(severity, "get", lambda *_: None)("severity")
                or getattr(severity, "get", lambda *_: None)("type")
                or severity
            )


            # Derive category from the grouped key where possible.
            # `canonical_name` is not necessarily the same as `category`, so we fall back safely.
            category = None
            if isinstance(test_name, str) and test_name:
                category = test_name

            priority = PriorityAnalyzer.calculate_score(
                str(severity_level).upper(),
                str(category).upper() if category else ""
            )

            # Collect all numeric values chronologically to build a trend or single latest value
            numeric_values = []
            for record in records_sorted:
                parsed_rec = TestValueParser.parse(record.testResult)
                if parsed_rec["type"] == "numeric":
                    numeric_values.append(record.testResult.strip())

            if len(numeric_values) > 1:
                evidence_list = [
                    f"{test_name} trend: " + " → ".join(numeric_values)
                ]
            elif len(numeric_values) == 1:
                evidence_list = [
                    f"{test_name} value: {numeric_values[0]}"
                ]
            else:
                evidence_list = [
                    f"{test_name} value: {value}"
                ]

            facts.append(

                ClinicalFact(

                    id=f"TEST_{test_name}",

                    category=
                    str(category) if category is not None else "",

                    fact=
                    f"{test_name} "
                    f"{abnormality}",

                    severity=severity,

                    priority_score=priority,

                    evidence=evidence_list
                )
            )

        return ProcessorResult(

            processor_name=
            "TestProcessor",

            facts=facts
        )