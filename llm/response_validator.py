import re


class ResponseValidator:

    FORBIDDEN_PATTERNS = [

        r"\bindicating\b",
        r"\bsuggesting\b",
        r"\blikely\b",
        r"\bpossible\b",
        r"\bconsistent with\b",
        r"\bassociated with\b",
        r"\bevidence of\b",
        r"\bconcerning for\b",
        r"\bdue to\b",
        r"\bsecondary to\b",
    ]

    @classmethod
    def validate(cls, text: str):

        lower = text.lower()

        for pattern in cls.FORBIDDEN_PATTERNS:

            if re.search(pattern, lower):

                raise ValueError(
                    f"Inference detected: {pattern}"
                )

        if len(text.split()) > 120:
            raise ValueError(
                "Summary exceeds 120 words"
            )
        return True