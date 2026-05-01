import json
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from kerykeion import AstrologicalSubject, SynastryAspects, KerykeionChartSVG
import cairosvg
from PIL import Image
import io
import torch
import numpy as np

from date_utils import ParseDateText, DateOffset, CurrentDateFetcher

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

def get_simplified_spanish_phase(phase_name):
    """Returns a simplified Spanish moon phase."""
    if phase_name == "New Moon":
        return "Nueva"
    elif phase_name in ["Waxing Crescent", "First Quarter", "Waxing Gibbous"]:
        return "Creciente"
    elif phase_name == "Full Moon":
        return "Llena"
    elif phase_name in ["Waning Gibbous", "Last Quarter", "Waning Crescent"]:
        return "Menguante"
    return phase_name

class TransitDataCalculator:
    """
    ComfyUI Custom Node to calculate astrological transits for a specific target date.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "target_year": ("INT", {"default": 2024, "min": 1900, "max": 2100}),
                "target_month": ("INT", {"default": 1, "min": 1, "max": 12}),
                "target_day": ("INT", {"default": 1, "min": 1, "max": 31}),
                "target_hour": ("INT", {"default": 12, "min": 0, "max": 23}),
                "target_minute": ("INT", {"default": 0, "min": 0, "max": 59}),
                "reference_city": ("STRING", {"default": "Madrid"}),
            }
        }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("transit_data_json",)
    FUNCTION = "calculate"
    CATEGORY = "ComfyUI-Pitonisa"

    def calculate(self, target_year, target_month, target_day, target_hour, target_minute, reference_city):
        try:
            # 1. Geocoding
            geolocator = Nominatim(user_agent="comfyui-kerykeion-meisoft", timeout=10)
            location = geolocator.geocode(reference_city)

            if not location:
                error_msg = {"error": "Ciudad no encontrada o error de geocodificación"}
                print(f"Warning (TransitDataCalculator): City '{reference_city}' not found.")
                return (json.dumps(error_msg, ensure_ascii=False),)

            lat = location.latitude
            lon = location.longitude

            # 2. Timezone
            tf = TimezoneFinder()
            tz_str = tf.timezone_at(lng=lon, lat=lat)

            if not tz_str:
                error_msg = {"error": "No se pudo determinar la zona horaria para la ubicación"}
                print(f"Warning (TransitDataCalculator): Timezone not found for '{reference_city}'.")
                return (json.dumps(error_msg, ensure_ascii=False),)

            # 3. Calculate Transits (Offline mode)
            subject = AstrologicalSubject(
                name="Transitos",
                year=target_year,
                month=target_month,
                day=target_day,
                hour=target_hour,
                minute=target_minute,
                lat=lat,
                lng=lon,
                tz_str=tz_str,
                city=reference_city,
                online=False
            )

            # 4. Format Output
            data = {
                "fecha_objetivo": f"{target_year:04d}-{target_month:02d}-{target_day:02d}",
                "posiciones_actuales": {
                    "sol": get_spanish_sign(subject.sun.sign),
                    "luna": get_spanish_sign(subject.moon.sign),
                    "mercurio": get_spanish_sign(subject.mercury.sign),
                    "venus": get_spanish_sign(subject.venus.sign),
                    "marte": get_spanish_sign(subject.mars.sign),
                    "jupiter": get_spanish_sign(subject.jupiter.sign),
                    "saturno": get_spanish_sign(subject.saturn.sign),
                    "urano": get_spanish_sign(subject.uranus.sign),
                    "neptuno": get_spanish_sign(subject.neptune.sign),
                    "pluton": get_spanish_sign(subject.pluto.sign)
                },
                "fase_lunar": get_simplified_spanish_phase(subject.lunar_phase.moon_phase_name)
            }

            return (json.dumps(data, ensure_ascii=False, indent=2),)

        except Exception as e:
            error_msg = {"error": f"Error inesperado: {str(e)}"}
            print(f"Error (TransitDataCalculator): {str(e)}")
            return (json.dumps(error_msg, ensure_ascii=False),)

ASPECT_TRANSLATIONS = {
    "conjunction": "Conjunción",
    "opposition": "Oposición",
    "trine": "Trígono",
    "square": "Cuadratura",
    "sextile": "Sextil"
}

PLANET_TRANSLATIONS = {
    "Sun": "Sol", "Moon": "Luna", "Mercury": "Mercurio", "Venus": "Venus", "Mars": "Marte",
    "Jupiter": "Júpiter", "Saturn": "Saturno", "Uranus": "Urano", "Neptune": "Neptuno", "Pluto": "Plutón",
    "True_Node": "Nodo Norte", "True_North_Lunar_Node": "Nodo Norte", "Mean_Node": "Nodo Norte",
    "True_South_Lunar_Node": "Nodo Sur",
    "Ascendant": "Ascendente", "Descendant": "Descendente", "Medium_Coeli": "Medio Cielo", "Imum_Coeli": "Fondo del Cielo",
    "Chiron": "Quirón", "Mean_Lilith": "Lilith"
}

def get_spanish_aspect(aspect_name):
    return ASPECT_TRANSLATIONS.get(aspect_name, aspect_name.capitalize())

def get_spanish_planet(planet_name):
    return PLANET_TRANSLATIONS.get(planet_name, planet_name)

class SynastryCalculator:
    """
    ComfyUI Custom Node to calculate synastry (compatibility) aspects between two people.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "p1_year": ("INT", {"default": 1990, "min": 1900, "max": 2100}),
                "p1_month": ("INT", {"default": 1, "min": 1, "max": 12}),
                "p1_day": ("INT", {"default": 1, "min": 1, "max": 31}),
                "p1_hour": ("INT", {"default": 12, "min": 0, "max": 23}),
                "p1_minute": ("INT", {"default": 0, "min": 0, "max": 59}),
                "p1_city": ("STRING", {"default": "Madrid"}),

                "p2_year": ("INT", {"default": 1995, "min": 1900, "max": 2100}),
                "p2_month": ("INT", {"default": 1, "min": 1, "max": 12}),
                "p2_day": ("INT", {"default": 1, "min": 1, "max": 31}),
                "p2_hour": ("INT", {"default": 12, "min": 0, "max": 23}),
                "p2_minute": ("INT", {"default": 0, "min": 0, "max": 59}),
                "p2_city": ("STRING", {"default": "Barcelona"}),
            }
        }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("synastry_data_json",)
    FUNCTION = "calculate"
    CATEGORY = "ComfyUI-Pitonisa"

    def _get_location_data(self, city_name, geolocator, tf):
        location = geolocator.geocode(city_name)
        if not location:
            return None, None, f"Ciudad no encontrada: {city_name}"
        lat = location.latitude
        lon = location.longitude
        tz_str = tf.timezone_at(lng=lon, lat=lat)
        if not tz_str:
            return None, None, f"Zona horaria no encontrada para: {city_name}"
        return lat, lon, tz_str

    def calculate(self, p1_year, p1_month, p1_day, p1_hour, p1_minute, p1_city,
                  p2_year, p2_month, p2_day, p2_hour, p2_minute, p2_city):
        try:
            geolocator = Nominatim(user_agent="comfyui-kerykeion-meisoft", timeout=10)
            tf = TimezoneFinder()

            lat1, lon1, tz1 = self._get_location_data(p1_city, geolocator, tf)
            if lat1 is None:
                return (json.dumps({"error": tz1}, ensure_ascii=False),)

            lat2, lon2, tz2 = self._get_location_data(p2_city, geolocator, tf)
            if lat2 is None:
                return (json.dumps({"error": tz2}, ensure_ascii=False),)

            s1 = AstrologicalSubject(name="P1", year=p1_year, month=p1_month, day=p1_day, hour=p1_hour, minute=p1_minute, lat=lat1, lng=lon1, tz_str=tz1, city=p1_city, online=False)
            s2 = AstrologicalSubject(name="P2", year=p2_year, month=p2_month, day=p2_day, hour=p2_hour, minute=p2_minute, lat=lat2, lng=lon2, tz_str=tz2, city=p2_city, online=False)

            syn = SynastryAspects(s1, s2)
            aspects = syn.get_relevant_aspects()

            aspectos_relevantes = []
            for aspect in aspects:
                # Filter out minor aspects if desired, though Kerykeion 'relevant_aspects' is usually a good subset
                p1_es = get_spanish_planet(aspect.p1_name)
                p2_es = get_spanish_planet(aspect.p2_name)
                asp_es = get_spanish_aspect(aspect.aspect)

                aspectos_relevantes.append(f"{p1_es} de P1 en {asp_es} con {p2_es} de P2")

            data = {
                "sinastria": aspectos_relevantes
            }
            return (json.dumps(data, ensure_ascii=False, indent=2),)

        except Exception as e:
            return (json.dumps({"error": f"Error inesperado: {str(e)}"}, ensure_ascii=False),)

class NatalChartImageNode:
    """
    ComfyUI Custom Node to generate a visual Natal Chart image.
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
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("natal_chart_image",)
    FUNCTION = "generate_image"
    CATEGORY = "ComfyUI-Pitonisa"

    def generate_image(self, year, month, day, hour, minute, city_name):
        try:
            # 1. Geocoding
            geolocator = Nominatim(user_agent="comfyui-kerykeion-meisoft", timeout=10)
            location = geolocator.geocode(city_name)
            if not location:
                print(f"Error (NatalChartImageNode): Ciudad '{city_name}' no encontrada.")
                # Create a blank fallback image
                blank_img = torch.zeros((1, 512, 512, 3), dtype=torch.float32)
                return (blank_img,)

            lat = location.latitude
            lon = location.longitude

            # 2. Timezone
            tf = TimezoneFinder()
            tz_str = tf.timezone_at(lng=lon, lat=lat)
            if not tz_str:
                print(f"Error (NatalChartImageNode): Zona horaria no encontrada para '{city_name}'.")
                blank_img = torch.zeros((1, 512, 512, 3), dtype=torch.float32)
                return (blank_img,)

            # 3. Calculate Astrological Chart
            subject = AstrologicalSubject(
                name="VisualUser",
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

            # 4. Generate SVG Template
            svg = KerykeionChartSVG(subject)
            svg.makeTemplate()
            svg_string = svg.template

            # 5. Convert SVG to Tensor
            png_data = cairosvg.svg2png(bytestring=svg_string.encode('utf-8'))
            image = Image.open(io.BytesIO(png_data)).convert('RGB')
            tensor = torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)

            return (tensor,)

        except Exception as e:
            print(f"Error inesperado en NatalChartImageNode: {str(e)}")
            blank_img = torch.zeros((1, 512, 512, 3), dtype=torch.float32)
            return (blank_img,)

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
                            "fecha": current_date.strftime("%d/%m/%Y"),
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
                         "fecha": current_date.strftime("%d/%m/%Y"),
                         "evento": f"{phase_esp} en {moon_sign_esp}"
                    })

                previous_subject = current_subject

            end_date = start_date + timedelta(days=duration_days - 1) if duration_days > 0 else start_date
            start_date_str = start_date.strftime("%d/%m/%Y")
            end_date_str = end_date.strftime("%d/%m/%Y")

            data = {
                "periodo": f"Del {start_date_str} al {end_date_str} ({duration_days} días)",
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
    "TransitRangeScanner": TransitRangeScanner,
    "SynastryCalculator": SynastryCalculator,
    "NatalChartImageNode": NatalChartImageNode,
    "AstroParseDate": ParseDateText,
    "AstroDateOffset": DateOffset,
    "AstroCurrentDate": CurrentDateFetcher
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NatalChartCalculator": "Natal Chart Calculator",
    "TransitDataCalculator": "Transit Data Calculator",
    "TransitRangeScanner": "Transit Range Scanner",
    "SynastryCalculator": "Synastry Calculator",
    "NatalChartImageNode": "Natal Chart Image",
    "AstroParseDate": "Astro Parse Date",
    "AstroDateOffset": "Astro Date Offset",
    "AstroCurrentDate": "Astro Current Date"
}
