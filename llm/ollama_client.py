import time
import requests
import re

from config.settings import settings


class OllamaClient:

    def generate(
        self,
        prompt: str
    ) -> str:

        print("\n===== OLLAMA REQUEST =====")
        print(
            f"Model: "
            f"{settings.OLLAMA_MODEL}"
        )

        print(
            f"Prompt Size: "
            f"{len(prompt)} chars"
        )

        start_time = time.time()

        try:

            response = requests.post(

                f"{settings.OLLAMA_URL}/api/generate",

                json={

                    "model":
                    settings.OLLAMA_MODEL,

                    "prompt":
                    prompt,

                    "stream":
                    False,

                    "think": False,
                    
                    "keep_alive": "30m",

                    "options": {

                        "temperature": 0,

                        "top_p": 0.2,

                        "top_k": 10,

                        "repeat_penalty": 1.05,

                        "num_predict": 1024,

                        "seed": 42
                    }
                }
            )

            response.raise_for_status()

            elapsed = (
                time.time()
                - start_time
            )

            print(
                f"Ollama Response "
                f"Received in "
                f"{elapsed:.2f}s"
            )

            # data = response.json()

            # print(
            #     f"Output Size: "
            #     f"{len(data.get('response', ''))}"
            #     f" chars"
            # )

            # result = data["response"]

            # # result = re.sub(
            # #     r"<think>.*?</think>",
            # #     "",
            # #     result,
            # #     flags=re.DOTALL
            # # ).strip()

            # return result

            data = response.json()

            result = data.get("response", "")

            print(
                "Ollama done_reason: "
                f"{data.get('done_reason', '')}"
            )

            print(
                "Ollama eval_count: "
                f"{data.get('eval_count', '')}"
            )

            print("RAW RESPONSE:")
            print(result)

            self.last_done_reason = (
                data.get("done_reason", "")
            )

            self.last_eval_count = (
                data.get("eval_count", 0)
            )

            return result

        except requests.exceptions.Timeout:

            print(
                "ERROR: Ollama "
                "request timed out."
            )

            raise

        except Exception as e:

            print(
                f"ERROR: {e}"
            )

            raise
