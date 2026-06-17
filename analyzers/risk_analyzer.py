import json
from pathlib import Path


class RiskAnalyzer:

    def __init__(self):

        rules_path = (
            Path(__file__)
            .parent.parent
            / "knowledge"
            / "risk_rules.json"
        )

        with open(
            rules_path,
            "r",
            encoding="utf-8"
        ) as file:

            self.rules = json.load(file)

    def detect_risks(
        self,
        findings: list[str]
    ):

        detected = []

        findings_set = set(
            findings
        )

        for risk_name, rule in (
            self.rules.items()
        ):

            required = set(
                rule["conditions"]
            )

            if required.issubset(
                findings_set
            ):

                detected.append(
                    risk_name
                )

        return detected