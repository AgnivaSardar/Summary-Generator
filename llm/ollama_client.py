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

                        "temperature": 0.1,

                        "top_p": 0.9,

                        "top_k": 20,

                        "repeat_penalty": 1.1,

                        "num_predict": 350,

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

            print("\n===== FULL OLLAMA JSON =====")
            print(data)
            print("===========================\n")

            result = data.get("response", "")

            print("RAW RESPONSE:")
            print(repr(result))

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