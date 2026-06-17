import json
from pathlib import Path


class SeverityAnalyzer:

    def __init__(self):

        rules_path = (
            Path(__file__)
            .parent.parent
            / "knowledge"
            / "custom_severity_rules.json"
        )

        with open(
            rules_path,
            "r",
            encoding="utf-8"
        ) as file:

            self.custom_rules = json.load(file)

    def analyze_range_based(
        self,
        value: float,
        range_min: float,
        range_max: float
    ) -> str:

        width = range_max - range_min

        if width <= 0:
            return "UNKNOWN"

        if range_min <= value <= range_max:
            return "NORMAL"

        if value > range_max:

            ratio = (
                value - range_max
            ) / width

        else:

            ratio = (
                range_min - value
            ) / width

        if ratio < 0.5:
            return "LOW"

        if ratio < 1:
            return "MODERATE"

        if ratio < 2:
            return "HIGH"

        return "CRITICAL"

    def analyze_custom(
        self,
        test_name: str,
        value: float
    ) -> str:

        rules = self.custom_rules.get(
            test_name
        )

        if not rules:
            return "UNKNOWN"

        if (
            "critical_high" in rules
            and value >= rules["critical_high"]
        ):
            return "CRITICAL"

        if (
            "critical_low" in rules
            and value <= rules["critical_low"]
        ):
            return "CRITICAL"

        if (
            "high" in rules
            and value >= rules["high"]
        ):
            return "HIGH"

        if (
            "moderate" in rules
            and value >= rules["moderate"]
        ):
            return "MODERATE"

        return "LOW"