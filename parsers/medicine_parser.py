import re

class MedicineParser:

    @staticmethod
    def parse(medicine_text: str):

        if not medicine_text:
            return []
        
        medicines = []

        lines = medicine_text.split("\n")
        for line in lines:
            line = line.strip()
            if line:
                medicines.append(line)
        return medicines