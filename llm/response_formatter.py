class ResponseFormatter:

    MAX_WORDS = 120

    def format(
        self,
        response: str
    ) -> str:

        response = response.strip()

        words = response.split()

        if len(words) <= self.MAX_WORDS:
            return response

        truncated = " ".join(
            words[:self.MAX_WORDS]
        )

        for symbol in [".", ";"]:

            idx = truncated.rfind(symbol)

            if idx > 0:
                return truncated[:idx + 1]

        return truncated