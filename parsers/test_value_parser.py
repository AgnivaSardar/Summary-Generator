import re
from typing import Any

class TestValueParser:
    @staticmethod
    def parse(value:str) -> dict[str, Any]:
        upper=value.upper()
        if upper is None:
            return{
                "type": "text",
                "value": None
            }
        
        if upper == "":
            return {
                "type": "text",
                "value": ""
            }
        
        if upper == "NIL":
            return {
                "type": "text",
                "value": "NIL"
            }
        
        if upper == "NOT DETECTED" or upper == "NOT PRESENT" or upper == "NEG" or upper == "NO" or upper == "N" or upper == "FALSE" or upper == "F" or upper == "0" or upper == "NEGATIVE":
            return {
                "type": "text",
                "value": "NEGATIVE"
            }
        
        if upper == "DETECTED" or upper == "PRESENT" or upper == "POS" or upper == "YES" or upper == "Y" or upper == "TRUE" or upper == "T" or upper == "1" or upper == "POSITIVE":
            return {
                "type": "text",
                "value": "POSITIVE"
            }
        
        if upper == "HIGH":
            return {
                "type": "text",
                "value": "HIGH"
            }
        
        if upper == "LOW":
            return {
                "type": "text",
                "value": "LOW"
            }
        
        range_pattern = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*$")
        match = range_pattern.match(value)
        if match:
            min_value = float(match.group(1))
            max_value = float(match.group(2))
            return {
                "type": "range",
                "min": min_value,
                "max": max_value
            }
        
        try:
            numeric_value = float(value)
            return {
                "type": "numeric",
                "value": numeric_value
            }
        except ValueError:
            pass

        return {
            "type": "text",
            "value": value
        }