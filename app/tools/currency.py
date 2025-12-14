# app/tools/currency.py
import requests
from app.tools.registry import register_tool

@register_tool("currency_convert")
def currency_convert(amount: float, from_currency: str, to_currency: str):
    """
    Convert currency using exchangerate.host (free).
    """
    url = f"https://api.exchangerate.host/convert?from={from_currency}&to={to_currency}&amount={amount}"

    try:
        result = requests.get(url).json()
        return {"result": result.get("result")}
    except Exception as e:
        return {"error": str(e)}
