import json
from pathlib import Path

class TestNameNormalizer:
    def __init__(self):
        dictionary_path = (Path(__file__).parent.parent/"knowledge"/"test_dictionary.json")

        with open(dictionary_path, "r", encoding="utf-8") as file:
            self.mapping = json.load(file)

    def normalize(self, test_name: str) -> str:
        if not test_name:
            return "UNKNOWN"
        
        cleaned_name = (test_name.strip().upper())
        return self.mapping.get(cleaned_name, cleaned_name)
    