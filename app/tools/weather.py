# app/tools/weather.py
import requests
from app.tools.registry import register_tool
from app.utils.cache import cache_get, cache_set

@register_tool("get_weather")
def get_weather(city: str):
    """
    Get weather info using Open-Meteo API (free, no key).
    """

    key = f"weather:{city.lower()}"
    cached = cache_get(key)
    if cached:
        print("\n\nCached hit\n\n")
        return cached

    try:
        url = f"https://wttr.in/{city}?format=j1"
        data = requests.get(url).json()

        current = data["current_condition"][0]

        result = {
            "temp_C": current["temp_C"],
            "weather_desc": current["weatherDesc"][0]["value"],
            "humidity": current["humidity"],
        }

        cache_set(key, result, ttl=900)  # 15 minutes

        return result
    
    except Exception as e:
        return {"error": str(e)}
