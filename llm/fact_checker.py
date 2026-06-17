class SynopsisFactChecker:

    @staticmethod
    def validate(
        summary: str,
        context: str
    ):

        summary_lower = summary.lower()
        context_lower = context.lower()

        dangerous_terms = [

            "dialysis",
            "transplant",
            "sepsis",
            "cancer",
            "stroke",
            "myocardial infarction",
            "heart attack",
            "arrhythmia",
            "ventilator",
            "icu",
            "metastatic",
            "end stage",
            "terminal"
        ]

        violations = []

        for term in dangerous_terms:

            if (
                term in summary_lower
                and term not in context_lower
            ):
                violations.append(term)

        if violations:

            raise ValueError(
                f"Hallucinated facts: {violations}"
            )

        return True