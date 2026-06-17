import json
from pathlib import Path

class MedicineNormalizer:
    def __init__(self):
        dictionary_path = (Path.Path(__file__).parent.parent/"knowledge"/"medicine_dictionary.json")

        with open(dictionary_path, "r", encoding="utf-8") as file:
            self.mapping = json.load(file)

    def normalize(self, medicine_name: str) -> str:
        if not medicine_name:
            return "UNKNOWN"
        
        cleaned_name = (medicine_name.strip().upper())
        return self.mapping.get(cleaned_name, cleaned_name)