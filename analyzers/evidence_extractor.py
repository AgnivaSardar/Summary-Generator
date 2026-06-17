class EvidenceExtractor:

    @staticmethod
    def extract_numeric_trend(
        test_name: str,
        values: list[float]
    ) -> str:

        trend_string = (
            " → "
            .join(
                map(
                    str,
                    values
                )
            )
        )

        return (
            f"{test_name}: "
            f"{trend_string}"
        )

    @staticmethod
    def latest_result(
        test_name: str,
        value,
        unit=""
    ):

        return (
            f"{test_name}: "
            f"{value} {unit}"
        )