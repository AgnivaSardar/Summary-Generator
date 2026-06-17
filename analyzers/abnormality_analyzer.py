class AbnormalityAnalyzer:
    @staticmethod
    def analyze(value: float, range_min: float, range_max: float) -> str:
        if value < range_min:
            return "LOW"
        elif value > range_max:
            return "HIGH"
        else:
            return "NORMAL"