class TrendAnalyzer:

    @staticmethod
    def analyze(
        values: list[float],
        direction: str
    ) -> str:

        if len(values) < 2:

            return "INSUFFICIENT_DATA"

        first = values[0]
        last = values[-1]

        if abs(last - first) < 0.01:

            return "STABLE"

        if direction == "LOWER_BETTER":

            if last < first:
                return "IMPROVING"

            return "WORSENING"

        if direction == "HIGHER_BETTER":

            if last > first:
                return "IMPROVING"

            return "WORSENING"

        if direction == "TARGET_RANGE":

            return (
                TrendAnalyzer
                .target_range_trend(
                    values
                )
            )

        return "UNKNOWN"

    @staticmethod
    def target_range_trend(
        values
    ):

        if len(values) < 2:

            return "UNKNOWN"

        latest = values[-1]

        previous = values[-2]

        if abs(latest - previous) < 0.01:

            return "STABLE"

        if abs(latest) < abs(previous):

            return "IMPROVING"

        return "WORSENING"