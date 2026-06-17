import re
from typing import Optional


class TextCleaner:

    @staticmethod
    def clean(text: Optional[str]) -> str:
        """
        Basic text cleaning.

        Removes:
        - extra spaces
        - tabs
        - multiple newlines
        - leading/trailing whitespace
        """

        if not text:
            return ""

        text = str(text)

        # replace tabs with spaces
        text = text.replace("\t", " ")

        # replace newlines with spaces
        text = text.replace("\n", " ")

        # collapse multiple spaces
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    @staticmethod
    def normalize_case(text: Optional[str]) -> str:
        """
        Convert text to uppercase.
        Useful for dictionary matching.
        """

        cleaned = TextCleaner.clean(text)

        return cleaned.upper()

    @staticmethod
    def remove_special_characters(
        text: Optional[str]
    ) -> str:
        """
        Removes unwanted symbols but
        preserves medical punctuation.
        """

        if not text:
            return ""

        text = TextCleaner.clean(text)

        return re.sub(
            r"[^a-zA-Z0-9\s.,:/()\-+]",
            "",
            text
        )

    @staticmethod
    def split_sentences(
        text: Optional[str]
    ) -> list[str]:
        """
        Splits text into sentences.
        """

        if not text:
            return []

        text = TextCleaner.clean(text)

        sentences = re.split(
            r"[.!?]+",
            text
        )

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

    @staticmethod
    def remove_duplicate_lines(
        text: Optional[str]
    ) -> str:
        """
        Removes duplicate lines from
        copied hospital records.
        """

        if not text:
            return ""

        lines = text.splitlines()

        seen = set()

        unique_lines = []

        for line in lines:

            cleaned_line = line.strip()

            if (
                cleaned_line
                and cleaned_line not in seen
            ):

                unique_lines.append(
                    cleaned_line
                )

                seen.add(
                    cleaned_line
                )

        return "\n".join(
            unique_lines
        )

    @staticmethod
    def clean_for_dictionary_matching(
        text: Optional[str]
    ) -> str:
        """
        Aggressive cleaning before
        diagnosis/medicine lookup.
        """

        if not text:
            return ""

        text = TextCleaner.clean(text)

        text = text.upper()

        text = re.sub(
            r"[^A-Z0-9\s]",
            " ",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()