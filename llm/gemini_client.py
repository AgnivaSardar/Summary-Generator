import time
import requests
from config.settings import settings

class GeminiClient:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.last_done_reason = ""
        self.last_eval_count = 0

    def generate(self, prompt: str) -> str:
        print("\n===== GEMINI REQUEST =====")
        print("Model: gemini-flash-latest")
        print(f"Prompt Size: {len(prompt)} chars")

        start_time = time.time()
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={self.api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.0,
                    "topP": 0.2,
                    "topK": 10,
                    "maxOutputTokens": 8192
                }
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            elapsed = time.time() - start_time
            print(f"Gemini Response Received in {elapsed:.2f}s")

            data = response.json()
            
            # Extract generated content
            candidates = data.get("candidates", [])
            if not candidates:
                raise ValueError("No candidates returned from Gemini API")
            
            first_candidate = candidates[0]
            content = first_candidate.get("content", {})
            parts = content.get("parts", [])
            if not parts:
                raise ValueError("No parts returned in content from Gemini API")
            
            result = parts[0].get("text", "")

            # Set finish/done reason
            finish_reason = first_candidate.get("finishReason", "")
            print(f"Gemini finishReason: {finish_reason}")
            
            # Map "MAX_TOKENS" to "length" to keep alignment with validator
            if finish_reason == "MAX_TOKENS":
                self.last_done_reason = "length"
            else:
                self.last_done_reason = finish_reason

            self.last_eval_count = 0  # Not directly exposed, set to 0

            print("RAW RESPONSE:")
            print(result)

            return result

        except requests.exceptions.Timeout:
            print("ERROR: Gemini request timed out.")
            raise
        except Exception as e:
            print(f"ERROR: {e}")
            raise
