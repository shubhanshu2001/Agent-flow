# app/tools/currency.py
import requests
from app.tools.registry import register_tool
from app.utils.cache import cache_get, cache_set

@register_tool("currency_convert")
def currency_convert(amount: float, from_currency: str, to_currency: str):
    """
    Convert currency using exchangerate.host (free).
    """

    key = f"currency:{amount}:{from_currency}:{to_currency}"
    cached = cache_get(key)
    if cached:
        return cached

    url = f"https://api.exchangerate.host/convert?from={from_currency}&to={to_currency}&amount={amount}"

    try:
        result = requests.get(url).json().get("result")

        cache_set(key, result, ttl=3600)  # 1 hour
        
        return result
    
    except Exception as e:
        return {"error": str(e)}
