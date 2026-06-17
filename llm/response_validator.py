import re


class WordValidator:

    TARGET_WORDS = 300

    @classmethod
    def validate(cls, text: str, context: str = ""):

        return True


class InferenceValidator:

    FORBIDDEN_PATTERNS = [

        r"\bindicates\b",
        r"\bindicating\b",
        r"\bsuggests\b",
        r"\bsuggesting\b",
        r"\blikely\b",
        r"\bpossible\b",
        r"\bprobable\b",
        r"\bappears\b",
        r"\bconsistent with\b",
        r"\bcompatible with\b",
        r"\bassociated with\b",
        r"\bevidence of\b",
        r"\bsuggestive of\b",
        r"\bconcerning for\b",
        r"\bbecause of\b",
        r"\bcaused by\b",
        r"\bdue to\b",
        r"\bsecondary to\b",
        r"\bhistory of\b",
        r"\bpresents with\b",
    ]

    @classmethod
    def validate(cls, text: str, context: str = ""):

        lower = text.lower()
        context_lower = context.lower()

        for pattern in cls.FORBIDDEN_PATTERNS:

            match = re.search(pattern, lower)

            if (
                match
                and match.group(0) not in context_lower
            ):

                raise ValueError(
                    f"Inference detected: {pattern}"
                )


class SequenceValidator:

    FORBIDDEN_PATTERNS = [

        r"\bincreased\b.*\bfrom\b",
        r"\bdecreased\b.*\bfrom\b",
        r"\brose\b.*\bfrom\b",
        r"\bfell\b.*\bfrom\b",
        r"\bimproved\b.*\bfrom\b",
        r"\bworsened\b.*\bfrom\b",
        r"\bprogressed\b.*\bfrom\b",
        r"\bdeclined\b.*\bfrom\b",
    ]

    SEQUENCE_PATTERN = re.compile(
        r"\d+(?:\.\d+)?"
        r"(?:\s*(?:->|→|to)\s*\d+(?:\.\d+)?)+"
        r"(?:\s*(?:%|mg/g|mg/dL|mL/min|mmol/L|mIU/L|pg/mL|mmHg))?",
        re.IGNORECASE
    )

    NUMBER_PATTERN = re.compile(
        r"\d+(?:\.\d+)?"
    )

    @classmethod
    def validate(cls, text: str, context: str):

        lower = text.lower()

        for pattern in cls.FORBIDDEN_PATTERNS:

            if re.search(pattern, lower):

                raise ValueError(
                    f"Forbidden sequence rewrite: {pattern}"
                )

        for sequence_match in cls.SEQUENCE_PATTERN.finditer(
            context
        ):

            sequence = sequence_match.group(0).strip()
            sequence_numbers = cls.NUMBER_PATTERN.findall(
                sequence
            )

            if not sequence_numbers:
                continue

            summary_numbers = [
                number
                for number in sequence_numbers
                if re.search(
                    rf"(?<![\d.]){re.escape(number)}(?![\d.])",
                    text
                )
            ]

            if (
                summary_numbers
                and sequence not in text
            ):

                raise ValueError(
                    "Numeric sequence changed or shortened"
                )


class NumericValidator:

    NUMBER_PATTERN = re.compile(
        r"""
        (?<![\w.])
        (?:\d+/\d+|\d+(?:\.\d+)?)
        \s*
        (?:%|mg/g|mg/dL|mL/min|mmol/L|mIU/L|pg/mL|mmHg)?
        (?![\w])
        """,
        re.IGNORECASE | re.VERBOSE
    )

    @classmethod
    def validate(cls, text: str, context: str):

        context_values = cls._extract_values(context)

        violations = []

        # Extract numeric tokens from summary. The model may restate years
        # as part of timeline items, and timeline evidence strings may omit
        # raw years depending on upstream extraction.
        #
        # To avoid hard-failing for benign year mentions, ignore plain 4-digit
        # years that are not present in context.
        for match in cls.NUMBER_PATTERN.finditer(
            cls._strip_sequence_spans(text)
        ):

            raw = match.group(0).strip()

            # Ignore 4-digit years if not explicitly present in context.
            if re.fullmatch(r"\d{4}", raw):
                continue

            value = cls._normalize(raw)

            if value not in context_values:
                violations.append(raw)

        if violations:

            raise ValueError(
                f"Numeric values not in context: {violations}"
            )


    @staticmethod
    def _normalize(value: str) -> str:

        return re.sub(
            r"\s+",
            "",
            value.lower().strip()
        )

    @classmethod
    def _extract_values(cls, text: str) -> set[str]:

        values = {
            cls._normalize(match.group(0))
            for match in cls.NUMBER_PATTERN.finditer(text)
        }

        values.update(
            cls._expand_sequence_values(text)
        )

        return values

    @classmethod
    def _expand_sequence_values(cls, text: str) -> set[str]:

        values = set()

        unit_pattern = (
            r"(?:%|mg/g|mg/dL|mL/min|mmol/L|mIU/L|pg/mL|mmHg)"
        )

        sequence_pattern = re.compile(
            r"(?P<body>\d+(?:\.\d+)?"
            r"(?:\s*(?:->|→|to)\s*\d+(?:\.\d+)?)+)"
            rf"\s*(?P<unit>{unit_pattern})?",
            re.IGNORECASE
        )

        number_pattern = re.compile(
            r"\d+(?:\.\d+)?"
        )

        for match in sequence_pattern.finditer(text):

            unit = match.group("unit") or ""

            for number in number_pattern.findall(
                match.group("body")
            ):

                values.add(
                    cls._normalize(
                        f"{number} {unit}"
                    )
                )

                values.add(
                    cls._normalize(number)
                )

        return values

    @classmethod
    def _strip_sequence_spans(cls, text: str) -> str:

        return re.sub(
            r"\d+(?:\.\d+)?"
            r"(?:\s*(?:->|→|to)\s*\d+(?:\.\d+)?)+"
            r"\s*(?:%|mg/g|mg/dL|mL/min|mmol/L|mIU/L|pg/mL|mmHg)?",
            " ",
            text,
            flags=re.IGNORECASE
        )


class TimelineValidator:

    YEAR_PATTERN = re.compile(
        r"\b(?:19|20)\d{2}\b"
    )

    @classmethod
    def validate(cls, text: str, context: str):

        context_years = set(
            cls.YEAR_PATTERN.findall(context)
        )

        summary_years = set(
            cls.YEAR_PATTERN.findall(text)
        )

        extra_years = sorted(
            summary_years - context_years
        )

        if extra_years:

            raise ValueError(
                f"Timeline years not in context: {extra_years}"
            )


class DuplicateValidator:

    @classmethod
    def validate(cls, text: str, context: str = ""):

        sentences = [
            sentence.strip().lower()
            for sentence in re.split(r"[.;]", text)
            if sentence.strip()
        ]

        duplicates = {
            sentence
            for sentence in sentences
            if sentences.count(sentence) > 1
        }

        if duplicates:

            raise ValueError(
                "Duplicate summary statements detected"
            )


class ResponseValidator:

    VALIDATORS = [
        InferenceValidator,
        SequenceValidator,
        NumericValidator,
        TimelineValidator,
    ]

    @classmethod
    def validate(
        cls,
        text: str,
        context: str = ""
    ):

        for validator in cls.VALIDATORS:

            validator.validate(
                text,
                context
            )

        return True
