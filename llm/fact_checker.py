import re


class SynopsisFactChecker:

    CKD_PATTERN = re.compile(
        r"\b(?:ckd|chronic kidney disease)\s+stage\s+\d+\b",
        re.IGNORECASE
    )

    RISK_PATTERN = re.compile(
        r"\b([a-z][a-z\s-]+?)\s+risk\b",
        re.IGNORECASE
    )

    NON_RISK_SECTION_PATTERN = re.compile(
        r"^(PROBLEMS|IMPORTANT FINDINGS|TIMELINE):\s*(.*)$",
        re.IGNORECASE | re.MULTILINE
    )

    SECTION_PATTERN = re.compile(
        r"^(PROBLEMS|IMPORTANT FINDINGS|RISKS|TIMELINE):\s*(.*)$",
        re.IGNORECASE | re.MULTILINE
    )

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

        violations.extend(
            SynopsisFactChecker._validate_ckd_stage(
                summary_lower,
                context_lower
            )
        )

        violations.extend(
            SynopsisFactChecker._validate_risk_phrasing(
                summary_lower,
                context_lower
            )
        )

        violations.extend(
            SynopsisFactChecker._validate_known_phrases(
                summary_lower,
                context_lower,
                context
            )
        )

        if violations:

            raise ValueError(
                f"Hallucinated facts: {violations}"
            )

        return True

    @classmethod
    def _validate_ckd_stage(
        cls,
        summary_lower: str,
        context_lower: str
    ) -> list[str]:

        violations = []

        context_stages = {
            cls._normalize_ckd_stage(
                match.group(0)
            )
            for match in cls.CKD_PATTERN.finditer(context_lower)
        }

        summary_stages = {
            cls._normalize_ckd_stage(
                match.group(0)
            )
            for match in cls.CKD_PATTERN.finditer(summary_lower)
        }

        if context_stages:

            mentions_ckd = (
                "ckd" in summary_lower
                or "chronic kidney disease" in summary_lower
            )

            if (
                mentions_ckd
                and not summary_stages
            ):
                violations.append(
                    "CKD stage omitted"
                )

        for stage in summary_stages:

            if stage not in context_stages:
                violations.append(stage)

        return violations

    @staticmethod
    def _normalize_ckd_stage(
        text: str
    ) -> str:

        match = re.search(
            r"stage\s+(\d+)",
            text,
            re.IGNORECASE
        )

        if not match:
            return text.lower()

        return f"ckd stage {match.group(1)}"

    @classmethod
    def _validate_risk_phrasing(
        cls,
        summary_lower: str,
        context_lower: str
    ) -> list[str]:

        violations = []
        non_risk_context = " ".join(
            match.group(2)
            for match in cls.NON_RISK_SECTION_PATTERN.finditer(
                context_lower
            )
        )

        risk_context = " ".join(
            match.group(2)
            for match in cls.SECTION_PATTERN.finditer(
                context_lower
            )
            if match.group(1).lower() == "risks"
        )

        for match in cls.RISK_PATTERN.finditer(
            risk_context
        ):

            full_risk = match.group(0).strip()
            risk_without_suffix = match.group(1).strip()

            if (
                risk_without_suffix in summary_lower
                and full_risk not in summary_lower
                and risk_without_suffix not in non_risk_context
            ):
                violations.append(
                    f"Risk converted to finding: {full_risk}"
                )

        return violations

    @classmethod
    def _validate_known_phrases(
        cls,
        summary_lower: str,
        context_lower: str,
        context: str
    ) -> list[str]:

        violations = []

        phrases = cls._extract_context_phrases(context)

        for phrase in phrases:

            phrase_lower = phrase.lower()

            if (
                len(phrase_lower.split()) < 2
                or phrase_lower not in summary_lower
            ):
                continue

            if phrase_lower not in context_lower:
                violations.append(phrase)

        return violations

    @classmethod
    def _extract_context_phrases(
        cls,
        context: str
    ) -> list[str]:

        phrases = []

        for match in cls.SECTION_PATTERN.finditer(context):

            section_text = match.group(2)

            phrases.extend(
                item.strip()
                for item in section_text.split(";")
                if item.strip()
            )

        return phrases
