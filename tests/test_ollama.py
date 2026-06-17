# test_ollama.py

import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen3:8b",
        "prompt": "hello",
        "stream": False,
        "think": False
    }
)

print(response.status_code)
print(response.json())