# app/tools/weather.py
import requests
from app.tools.registry import register_tool

@register_tool("get_weather")
def get_weather(city: str):
    """
    Get weather info using Open-Meteo API (free, no key).
    """
    try:
        url = f"https://wttr.in/{city}?format=j1"
        data = requests.get(url).json()

        current = data["current_condition"][0]
        return {
            "temp_C": current["temp_C"],
            "weather_desc": current["weatherDesc"][0]["value"],
            "humidity": current["humidity"],
        }
    except Exception as e:
        return {"error": str(e)}
