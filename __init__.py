import json
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from kerykeion import AstrologicalSubject

# Dictionary to translate English sign names or abbreviations to Spanish full names
SIGN_TRANSLATIONS = {
    "Aries": "Aries", "Ari": "Aries",
    "Taurus": "Tauro", "Tau": "Tauro",
    "Gemini": "Geminis", "Gem": "Geminis",
    "Cancer": "Cancer", "Can": "Cancer",
    "Leo": "Leo",
    "Virgo": "Virgo", "Vir": "Virgo",
    "Libra": "Libra", "Lib": "Libra",
    "Scorpio": "Escorpio", "Sco": "Escorpio",
    "Sagittarius": "Sagitario", "Sag": "Sagitario",
    "Capricorn": "Capricornio", "Cap": "Capricornio",
    "Aquarius": "Acuario", "Aqu": "Acuario",
    "Pisces": "Piscis", "Pis": "Piscis"
}

def get_spanish_sign(sign_name):
    """Translates the sign name or abbreviation to Spanish."""
    return SIGN_TRANSLATIONS.get(sign_name, sign_name)

class NatalChartCalculator:
    """
    ComfyUI Custom Node to calculate Natal Chart data using Kerykeion.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "year": ("INT", {"default": 2000, "min": 1900, "max": 2100}),
                "month": ("INT", {"default": 1, "min": 1, "max": 12}),
                "day": ("INT", {"default": 1, "min": 1, "max": 31}),
                "hour": ("INT", {"default": 12, "min": 0, "max": 23}),
                "minute": ("INT", {"default": 0, "min": 0, "max": 59}),
                "city_name": ("STRING", {"default": "Madrid"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("astral_data_json",)
    FUNCTION = "calculate_chart"
    CATEGORY = "ComfyUI-Pitonisa"

    def calculate_chart(self, year, month, day, hour, minute, city_name):
        try:
            # 1. Geocoding: Get lat, lon from city_name
            geolocator = Nominatim(user_agent="comfyui-kerykeion-meisoft", timeout=10)
            location = geolocator.geocode(city_name)

            if not location:
                error_msg = {"error": "Ciudad no encontrada o error de geocodificación"}
                print(f"Warning (NatalChartCalculator): City '{city_name}' not found.")
                return (json.dumps(error_msg, ensure_ascii=False),)

            lat = location.latitude
            lon = location.longitude

            # 2. Find Timezone
            tf = TimezoneFinder()
            tz_str = tf.timezone_at(lng=lon, lat=lat)

            if not tz_str:
                error_msg = {"error": "No se pudo determinar la zona horaria para la ubicación"}
                print(f"Warning (NatalChartCalculator): Timezone not found for '{city_name}' (lat: {lat}, lon: {lon}).")
                return (json.dumps(error_msg, ensure_ascii=False),)

            # 3. Calculate Astrological Chart (Offline mode)
            subject = AstrologicalSubject(
                name="User",
                year=year,
                month=month,
                day=day,
                hour=hour,
                minute=minute,
                lat=lat,
                lng=lon,
                tz_str=tz_str,
                city=city_name,
                online=False
            )

            # 4. Extract data and translate to Spanish
            data = {
                "sol": get_spanish_sign(subject.sun.sign),
                "luna": get_spanish_sign(subject.moon.sign),
                "ascendente": get_spanish_sign(subject.first_house.sign),
                "planetas": {
                    "mercurio": get_spanish_sign(subject.mercury.sign),
                    "venus": get_spanish_sign(subject.venus.sign),
                    "marte": get_spanish_sign(subject.mars.sign),
                    "jupiter": get_spanish_sign(subject.jupiter.sign),
                    "saturno": get_spanish_sign(subject.saturn.sign),
                    "urano": get_spanish_sign(subject.uranus.sign),
                    "neptuno": get_spanish_sign(subject.neptune.sign),
                    "pluton": get_spanish_sign(subject.pluto.sign)
                },
                "casas": {
                    "casa_1": get_spanish_sign(subject.first_house.sign),
                    "casa_2": get_spanish_sign(subject.second_house.sign),
                    "casa_3": get_spanish_sign(subject.third_house.sign),
                    "casa_4": get_spanish_sign(subject.fourth_house.sign),
                    "casa_5": get_spanish_sign(subject.fifth_house.sign),
                    "casa_6": get_spanish_sign(subject.sixth_house.sign),
                    "casa_7": get_spanish_sign(subject.seventh_house.sign),
                    "casa_8": get_spanish_sign(subject.eighth_house.sign),
                    "casa_9": get_spanish_sign(subject.ninth_house.sign),
                    "casa_10": get_spanish_sign(subject.tenth_house.sign),
                    "casa_11": get_spanish_sign(subject.eleventh_house.sign),
                    "casa_12": get_spanish_sign(subject.twelfth_house.sign)
                }
            }

            return (json.dumps(data, ensure_ascii=False, indent=2),)

        except Exception as e:
            error_msg = {"error": f"Error inesperado: {str(e)}"}
            print(f"Error (NatalChartCalculator): {str(e)}")
            return (json.dumps(error_msg, ensure_ascii=False),)

# Node registration for ComfyUI
NODE_CLASS_MAPPINGS = {
    "NatalChartCalculator": NatalChartCalculator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NatalChartCalculator": "Natal Chart Calculator"
}
