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

# Dictionary to translate English lunar phases to Spanish
PHASE_TRANSLATIONS = {
    "New Moon": "Luna Nueva",
    "Waxing Crescent": "Luna Creciente",
    "First Quarter": "Cuarto Creciente",
    "Waxing Gibbous": "Luna Llena (Aproximandose)",
    "Full Moon": "Luna Llena",
    "Waning Gibbous": "Luna Menguante",
    "Last Quarter": "Cuarto Menguante",
    "Waning Crescent": "Luna Balsamica"
}

def get_spanish_phase(phase_name):
    """Translates the moon phase to Spanish."""
    return PHASE_TRANSLATIONS.get(phase_name, phase_name)

class TransitDataCalculator:
    """
    Placeholder node to satisfy the export requirement for TransitDataCalculator.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dummy": ("STRING", {"default": "Dummy"}),
            }
        }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("data",)
    FUNCTION = "calculate"
    CATEGORY = "ComfyUI-Pitonisa"

    def calculate(self, dummy):
        return (json.dumps({"message": "TransitDataCalculator placeholder"}, ensure_ascii=False),)

class TransitRangeScanner:
    """
    ComfyUI Custom Node to scan for astrological transits and moon phases over a given period.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "start_year": ("INT", {"default": 2024, "min": 1900, "max": 2100}),
                "start_month": ("INT", {"default": 1, "min": 1, "max": 12}),
                "start_day": ("INT", {"default": 1, "min": 1, "max": 31}),
                "duration_days": ("INT", {"default": 7, "min": 1, "max": 31}),
                "city_name": ("STRING", {"default": "Madrid"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("transit_data_json",)
    FUNCTION = "scan_transits"
    CATEGORY = "ComfyUI-Pitonisa"

    def scan_transits(self, start_year, start_month, start_day, duration_days, city_name):
        from datetime import datetime, timedelta

        try:
            # 1. Geocoding
            geolocator = Nominatim(user_agent="comfyui-kerykeion-meisoft", timeout=10)
            location = geolocator.geocode(city_name)

            if not location:
                error_msg = {"error": "Ciudad no encontrada o error de geocodificación"}
                print(f"Warning (TransitRangeScanner): City '{city_name}' not found.")
                return (json.dumps(error_msg, ensure_ascii=False),)

            lat = location.latitude
            lon = location.longitude

            # 2. Timezone
            tf = TimezoneFinder()
            tz_str = tf.timezone_at(lng=lon, lat=lat)

            if not tz_str:
                error_msg = {"error": "No se pudo determinar la zona horaria para la ubicación"}
                print(f"Warning (TransitRangeScanner): Timezone not found for '{city_name}'.")
                return (json.dumps(error_msg, ensure_ascii=False),)

            try:
                start_date = datetime(start_year, start_month, start_day, 12, 0)
            except ValueError as e:
                 return (json.dumps({"error": f"Fecha de inicio inválida: {str(e)}"}, ensure_ascii=False),)

            eventos_clave = []

            # Use 'yesterday' to establish baseline for changes on day 1
            previous_date = start_date - timedelta(days=1)
            previous_subject = AstrologicalSubject(
                name="Prev",
                year=previous_date.year,
                month=previous_date.month,
                day=previous_date.day,
                hour=12,
                minute=0,
                lat=lat,
                lng=lon,
                tz_str=tz_str,
                city=city_name,
                online=False
            )

            # Map planet objects for comparison
            planets_map = {
                "Sol": lambda sub: sub.sun,
                "Luna": lambda sub: sub.moon,
                "Mercurio": lambda sub: sub.mercury,
                "Venus": lambda sub: sub.venus,
                "Marte": lambda sub: sub.mars,
                "Jupiter": lambda sub: sub.jupiter,
                "Saturno": lambda sub: sub.saturn,
                "Urano": lambda sub: sub.uranus,
                "Neptuno": lambda sub: sub.neptune,
                "Pluton": lambda sub: sub.pluto
            }

            clima_astral_general = {}
            if duration_days > 0:
                 # Populate initial climate with the start_date's information
                 current_subject = AstrologicalSubject(
                    name="Init",
                    year=start_date.year,
                    month=start_date.month,
                    day=start_date.day,
                    hour=12,
                    minute=0,
                    lat=lat,
                    lng=lon,
                    tz_str=tz_str,
                    city=city_name,
                    online=False
                 )
                 clima_astral_general = {
                     "sol_en": get_spanish_sign(current_subject.sun.sign),
                     "marte_en": get_spanish_sign(current_subject.mars.sign)
                 }

            for day_offset in range(duration_days):
                current_date = start_date + timedelta(days=day_offset)
                current_subject = AstrologicalSubject(
                    name="Day",
                    year=current_date.year,
                    month=current_date.month,
                    day=current_date.day,
                    hour=12,
                    minute=0,
                    lat=lat,
                    lng=lon,
                    tz_str=tz_str,
                    city=city_name,
                    online=False
                )

                # Check for planetary sign changes (Ingresos)
                for planet_name, get_planet in planets_map.items():
                    prev_planet = get_planet(previous_subject)
                    curr_planet = get_planet(current_subject)

                    if prev_planet.sign != curr_planet.sign:
                        signo_esp = get_spanish_sign(curr_planet.sign)
                        eventos_clave.append({
                            "dia": day_offset + 1,
                            "evento": f"Ingreso: {planet_name} entra en {signo_esp}"
                        })

                # Check for major Moon Phases changing
                prev_phase = previous_subject.lunar_phase.moon_phase_name
                curr_phase = current_subject.lunar_phase.moon_phase_name

                major_phases = ["New Moon", "Full Moon", "First Quarter", "Last Quarter"]
                if curr_phase != prev_phase and curr_phase in major_phases:
                    phase_esp = get_spanish_phase(curr_phase)
                    moon_sign_esp = get_spanish_sign(current_subject.moon.sign)
                    eventos_clave.append({
                         "dia": day_offset + 1,
                         "evento": f"{phase_esp} en {moon_sign_esp}"
                    })

                previous_subject = current_subject

            data = {
                "periodo": f"{duration_days} días",
                "eventos_clave": eventos_clave,
                "clima_astral_general": clima_astral_general
            }

            return (json.dumps(data, ensure_ascii=False, indent=2),)

        except Exception as e:
            error_msg = {"error": f"Error inesperado: {str(e)}"}
            print(f"Error (TransitRangeScanner): {str(e)}")
            return (json.dumps(error_msg, ensure_ascii=False),)

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
    "NatalChartCalculator": NatalChartCalculator,
    "TransitDataCalculator": TransitDataCalculator,
    "TransitRangeScanner": TransitRangeScanner
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NatalChartCalculator": "Natal Chart Calculator",
    "TransitDataCalculator": "Transit Data Calculator",
    "TransitRangeScanner": "Transit Range Scanner"
}
