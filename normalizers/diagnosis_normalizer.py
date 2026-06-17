import json
from pathlib import Path

class DiagnosisNormalizer:
    def __init__(self):
        dictionary_path = (Path(__file__).parent.parent/"knowledge"/"diagnosis_dictionary.json")

        with open(dictionary_path, "r", encoding="utf-8") as file:
            self.mapping = json.load(file)

    def normalize(self, diagnosis_name: str) -> str:
        if not diagnosis_name:
            return "UNKNOWN"
        
        cleaned_name = (diagnosis_name.strip().upper())
        return self.mapping.get(cleaned_name, cleaned_name)