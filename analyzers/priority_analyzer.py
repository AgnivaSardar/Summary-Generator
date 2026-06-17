class PriorityAnalyzer:

    SEVERITY_SCORE = {

        "NORMAL": 0,

        "LOW": 25,

        "MODERATE": 50,

        "HIGH": 75,

        "CRITICAL": 100
    }

    CATEGORY_BONUS = {

        "ONCOLOGY": 20,

        "CARDIAC": 15,

        "RENAL": 10,

        "HEMATOLOGY": 10,

        "ENDOCRINE": 5
    }

    @staticmethod
    def calculate_score(
        severity: str,
        category: str
    ):

        score = (
            PriorityAnalyzer
            .SEVERITY_SCORE
            .get(
                severity,
                0
            )
        )

        score += (
            PriorityAnalyzer
            .CATEGORY_BONUS
            .get(
                category,
                0
            )
        )

        return min(
            score,
            100
        )