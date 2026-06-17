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

    @staticmethod
    def clean_and_translate(medicine_text: str) -> str:
        if not medicine_text:
            return ""

        # First clean up the HTML tags like <div> or <br>
        text = str(medicine_text)
        text = re.sub(r"<[^>]+>", " ", text)

        # Now translate the dosage patterns (e.g., 1-1-2, 1-0-1, etc.)
        def replace_match(match):
            m = int(match.group(1))
            a = int(match.group(2))
            n = int(match.group(3))

            parts = []
            if m > 0:
                unit = "1 tablet" if m == 1 else f"{m} tablets"
                parts.append(f"{unit} in the morning")
            if a > 0:
                unit = "1 tablet" if a == 1 else f"{a} tablets"
                parts.append(f"{unit} in the afternoon")
            if n > 0:
                unit = "1 tablet" if n == 1 else f"{n} tablets"
                parts.append(f"{unit} at night")

            if not parts:
                return "as needed"

            if len(parts) == 1:
                return parts[0]
            elif len(parts) == 2:
                return f"{parts[0]} and {parts[1]}"
            else:
                return f"{parts[0]}, {parts[1]}, and {parts[2]}"

        text = re.sub(r"\b(\d)-(\d)-(\d)\b", replace_match, text)

        # Now do basic text cleaning
        text = text.replace("\t", " ")
        text = text.replace("\n", " ")
        text = re.sub(r"\s+", " ", text)
        return text.strip()