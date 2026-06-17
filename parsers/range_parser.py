import re

class RangeParser:
    @staticmethod
    def parse(value):
        range_pattern = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*$")
        match = range_pattern.match(value)
        if match:
            min_value = float(match.group(1))
            max_value = float(match.group(2))
            return {
                "type": "range",
                "min": min_value,
                "max": max_value,
                "value": (min_value, max_value)
            }
        else:
            return None
