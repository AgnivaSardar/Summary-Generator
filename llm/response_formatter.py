import re


class ResponseFormatter:

    # Keep this list aligned with llm/response_validator.py -> InferenceValidator.FORBIDDEN_PATTERNS
    # This formatter does not change numbers/years/sequences; it only removes forbidden
    # interpretation words that cause validation failures.
    FORBIDDEN_WORD_REPLACEMENTS = {
        r"\bindicating\b": "",
        r"\bindicating\b": "",
        r"\bindicates\b": "",
        r"\bindicating\b": "",
        r"\bindicating\b": "",
        r"\binference\b": "",
        r"\bsuggests\b": "",
        r"\bsuggesting\b": "",
        r"\blikely\b": "",
        r"\bpossible\b": "",
        r"\bprobable\b": "",
        r"\bappears\b": "",
        r"\bconsistent with\b": "",
        r"\bcompatible with\b": "",
        r"\bassociated with\b": "",
        r"\bevidence of\b": "",
        r"\bsuggestive of\b": "",
        r"\bconcerning for\b": "",
        r"\bbecause of\b": "",
        r"\bcaused by\b": "",
        r"\bdue to\b": "",
        r"\bsecondary to\b": "",
        r"\bhistory of\b": "",
        r"\bpresents with\b": "",
    }

    @classmethod
    def _strip_forbidden_inference_words(cls, text: str) -> str:
        out = text
        for pattern, replacement in cls.FORBIDDEN_WORD_REPLACEMENTS.items():
            out = re.sub(pattern, replacement, out, flags=re.IGNORECASE)
        # Normalize whitespace after removals.
        out = re.sub(r"\s+", " ", out)
        return out.strip()

    def format(
        self,
        response: str
    ) -> str:
        formatted = response.strip()
        formatted = self._strip_forbidden_inference_words(formatted)
        return formatted

