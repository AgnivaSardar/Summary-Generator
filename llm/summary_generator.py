import time

from llm.deterministic_serializer import (
    DeterministicSerializer
)

from llm.fact_checker import (
    SynopsisFactChecker
)

from llm.prompt_template import (
    SYNOPSIS_PROMPT
)

from llm.ollama_client import (
    OllamaClient
)

from llm.response_validator import (
    ResponseValidator
)

from llm.response_formatter import (
    ResponseFormatter
)

from context_builder.synopsis_context_builder import (
    SynopsisContextBuilder
)


class SummaryGenerator:

    def __init__(self):

        self.ollama = (
            OllamaClient()
        )

    def generate(
        self,
        patient_context
    ) -> str:

        total_start = time.time()

        print(
            "\n===== SUMMARY "
            "GENERATION STARTED ====="
        )

        # -----------------------------
        # Build Context
        # -----------------------------

        context_start = time.time()

        context_text = (

            SynopsisContextBuilder()
            .build(
                patient_context
            )
        )

        print("\n===== CONTEXT =====")
        print(context_text)
        print("===================")

        context_time = (
            time.time()
            - context_start
        )

        print(
            f"Context Builder: "
            f"{context_time:.2f}s"
        )

        print(
            f"Context Length: "
            f"{len(context_text)} chars"
        )

        placeholder_count = (
            context_text.count("Condition")
            + context_text.count("Finding")
        )

        if placeholder_count >= 5:

            print(
                "Placeholder mode activated"
            )

            return context_text

        # -----------------------------
        # Build Prompt
        # -----------------------------

        prompt_start = time.time()

        prompt = (
            SYNOPSIS_PROMPT
            .replace(
                "{context}",
                context_text
            )
        )

        print("\n===== PROMPT =====")
        print(prompt)
        print("==================")

        prompt_time = (
            time.time()
            - prompt_start
        )

        print(
            f"Prompt Build: "
            f"{prompt_time:.2f}s"
        )

        print(
            f"Prompt Length: "
            f"{len(prompt)} chars"
        )

        # -----------------------------
        # Ollama
        # -----------------------------

        print(
            "\nSending to Ollama..."
        )

        ollama_start = time.time()

        response = (
            self.ollama.generate(
                prompt
            )
        )

        ollama_time = (
            time.time()
            - ollama_start
        )

        print(
            f"Ollama Time: "
            f"{ollama_time:.2f}s"
        )

        print(
            "Received Response"
        )

        # -----------------------------
        # Validation
        # -----------------------------

        try:

            ResponseValidator.validate(
                response
            )

            SynopsisFactChecker.validate(
                response,
                context_text
            )

        except Exception as e:

            print(
                f"VALIDATION FAILED: {e}"
            )

            print(
                "USING DETERMINISTIC SERIALIZER"
            )

            response = (
                DeterministicSerializer.build(
                    context_text
                )
            )

        # -----------------------------
        # Formatting
        # -----------------------------

        formatted_response = (

            ResponseFormatter()
            .format(
                response
            )
        )

        total_time = (
            time.time()
            - total_start
        )

        print(
            "\n===== SUMMARY "
            "GENERATION COMPLETE ====="
        )

        print(
            f"Total Time: "
            f"{total_time:.2f}s"
        )

        return formatted_response