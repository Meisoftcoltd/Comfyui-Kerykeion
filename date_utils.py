from datetime import datetime, timedelta

class ParseDateText:
    """
    ComfyUI Custom Node: Parse a date string into year, month, day.
    Supports YYYY-MM-DD and DD/MM/YYYY formats.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "date_string": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("INT", "INT", "INT")
    RETURN_NAMES = ("year", "month", "day")
    FUNCTION = "parse_date"
    CATEGORY = "ComfyUI-Pitonisa/Time Utils"

    def parse_date(self, date_string):
        date_string = date_string.strip()
        try:
            if "-" in date_string:
                # Assume YYYY-MM-DD
                parts = date_string.split("-")
                if len(parts) == 3:
                    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                    return (year, month, day)
                else:
                    raise ValueError("Formato incorrecto con guiones")
            elif "/" in date_string:
                # Assume DD/MM/YYYY
                parts = date_string.split("/")
                if len(parts) == 3:
                    day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                    return (year, month, day)
                else:
                    raise ValueError("Formato incorrecto con barras")
            else:
                raise ValueError("No se encontraron separadores / o -")
        except Exception as e:
            print(f"Warning: Formato de fecha incorrecto '{date_string}', usando fecha actual. Error: {e}")
            now = datetime.now()
            return (now.year, now.month, now.day)


class DateOffset:
    """
    ComfyUI Custom Node: Add or subtract days from a given date.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "year": ("INT", {"default": 2024}),
                "month": ("INT", {"default": 1}),
                "day": ("INT", {"default": 1}),
                "days_offset": ("INT", {"default": 0}),
            }
        }

    RETURN_TYPES = ("INT", "INT", "INT", "STRING")
    RETURN_NAMES = ("new_year", "new_month", "new_day", "new_date_string")
    FUNCTION = "calculate_offset"
    CATEGORY = "ComfyUI-Pitonisa/Time Utils"

    def calculate_offset(self, year, month, day, days_offset):
        try:
            current_date = datetime(year, month, day)
            new_date = current_date + timedelta(days=days_offset)
            new_date_string = new_date.strftime("%d/%m/%Y")
            return (new_date.year, new_date.month, new_date.day, new_date_string)
        except Exception as e:
            print(f"Warning: Error en DateOffset con fecha {year}-{month}-{day}. Usando fecha actual. Error: {e}")
            now = datetime.now()
            new_date_string = now.strftime("%d/%m/%Y")
            return (now.year, now.month, now.day, new_date_string)


class CurrentDateFetcher:
    """
    ComfyUI Custom Node: Get the current system date and time.
    Bypasses cache to ensure it's always up to date.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {}
        }

    RETURN_TYPES = ("INT", "INT", "INT", "INT", "INT", "STRING")
    RETURN_NAMES = ("year", "month", "day", "hour", "minute", "date_string")
    FUNCTION = "fetch_current_date"
    CATEGORY = "ComfyUI-Pitonisa/Time Utils"

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

    def fetch_current_date(self):
        now = datetime.now()
        date_string = now.strftime("%d/%m/%Y")
        return (now.year, now.month, now.day, now.hour, now.minute, date_string)
