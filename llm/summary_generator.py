import time
import re

from llm.deterministic_serializer import (
    DeterministicSerializer
)

from llm.fact_checker import (
    SynopsisFactChecker
)

from llm.prompt_template import (
    RETRY_PROMPT,
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

    MAX_VALIDATION_RETRIES = 2

    def __init__(self):
        from config.settings import settings
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
            from llm.gemini_client import GeminiClient
            self.ollama = GeminiClient()
        else:
            self.ollama = OllamaClient()

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

        print("\n===== CONTEXT (STRUCTURED KEYS) =====")
        try:
            patient_block = (patient_context.get("patient", {}) or {})
            print(
                "patient_id:",
                patient_block.get("patient_id")
            )
            print(
                "patient_name:",
                patient_block.get("patient_name")
            )
            print(
                "counts => active_problems:",
                len(patient_context.get("active_problems", []) or [])
            )
            print(
                "counts => evidence:",
                len(patient_context.get("evidence", []) or [])
            )
            print(
                "counts => risks:",
                len(patient_context.get("risks", []) or [])
            )
            print(
                "counts => timeline:",
                len(patient_context.get("timeline", []) or [])
            )
        except Exception:
            print("(could not print structured context details)")

        print("\n===== CONTEXT (TEXT SENT TO LLM) =====")
        print(
            "Context preview (first 700 chars): "
            f"{context_text[:700]}"
        )
        if len(context_text) > 700:
            print(
                "Context preview (last 700 chars): "
                f"{context_text[-700:]}"
            )
        print("========================================")

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

        if self._has_no_meaningful_clinical_content(
            patient_context,
            context_text
        ):

            print(
                "No meaningful clinical content detected; "
                "using deterministic serializer"
            )

            return (
                ResponseFormatter()
                .format(
                    DeterministicSerializer.build(
                        context_text
                    )
                )
            )

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
        print(
            "Prompt preview: "
            f"{prompt[:500]}"
        )
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

        print("\nSending to Ollama...")

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

        print("Received Response")

        # -----------------------------
        # Validation
        # -----------------------------

        response = self._validate_or_retry(
            response,
            context_text
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

    def _validate_or_retry(
        self,
        response: str,
        context_text: str
    ) -> str:

        validation_error = ""

        for attempt in range(
            self.MAX_VALIDATION_RETRIES + 1
        ):

            response = (
                ResponseFormatter()
                .format(
                    response
                )
            )

            try:

                if (
                    getattr(
                        self.ollama,
                        "last_done_reason",
                        ""
                    )
                    == "length"
                ):

                    raise ValueError(
                        "Response stopped due to token limit"
                    )

                self._validate_response(
                    response,
                    context_text
                )

                return response

            except Exception as e:

                validation_error = str(e)

                print(
                    "VALIDATION FAILED: "
                    f"{validation_error}"
                )

                if attempt >= self.MAX_VALIDATION_RETRIES:

                    raise ValueError(
                        "Synopsis failed validation after "
                        f"{self.MAX_VALIDATION_RETRIES} retries: "
                        f"{validation_error}"
                    )

                response = self._retry_synopsis(
                    context_text,
                    response,
                    validation_error
                )

        raise ValueError(
            "Synopsis failed validation: "
            f"{validation_error}"
        )

    def _retry_synopsis(
        self,
        context_text: str,
        previous_response: str,
        validation_error: str
    ) -> str:

        print("Retrying with retry prompt...")

        retry_prompt = (
            RETRY_PROMPT
            .replace(
                "{error}",
                validation_error
            )
            .replace(
                "{previous_synopsis}",
                previous_response
            )
            .replace(
                "{context}",
                context_text
            )
        )

        retry_start = time.time()

        retry_response = (
            self.ollama.generate(
                retry_prompt
            )
        )

        retry_time = (
            time.time()
            - retry_start
        )

        print(
            f"Retry Ollama Time: "
            f"{retry_time:.2f}s"
        )

        return retry_response

    def _validate_response(
        self,
        response: str,
        context_text: str
    ) -> None:

        ResponseValidator.validate(
            response,
            context_text
        )

        SynopsisFactChecker.validate(
            response,
            context_text
        )

    def _has_no_meaningful_clinical_content(
        self,
        patient_context,
        context_text: str
    ) -> bool:

        placeholder_count = len(
            re.findall(
                r"\b(?:Condition|Finding|Risk|Event)\s+\d+\b",
                context_text
            )
        )

        if placeholder_count >= 10:
            return True

        # Check if there is any real clinical data
        active_problems = patient_context.get("active_problems", [])
        evidence = patient_context.get("evidence", [])
        risks = patient_context.get("risks", [])
        timeline = patient_context.get("timeline", [])
        medication = patient_context.get("medication", "")
        advice = patient_context.get("advice", "")

        real_timeline = []
        for event in timeline:
            event_stripped = str(event).strip()
            if event_stripped in ["Appointment:", "Admission:", "Test:", "Appointment", "Admission", "Test"]:
                continue
            if event_stripped.startswith("Appointment:") and not event_stripped.replace("Appointment:", "").strip():
                continue
            if event_stripped.startswith("Admission:") and not event_stripped.replace("Admission:", "").strip():
                continue
            if event_stripped.startswith("Test:") and not event_stripped.replace("Test:", "").strip():
                continue
            real_timeline.append(event)

        has_any_data = (
            len(active_problems) > 0 or
            len(evidence) > 0 or
            len(risks) > 0 or
            len(real_timeline) > 0 or
            len(str(medication).strip()) > 0 or
            len(str(advice).strip()) > 0
        )

        return not has_any_data

