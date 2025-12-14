# app/tools/news.py
import requests
from app.tools.registry import register_tool

@register_tool("get_news")
def get_news(query: str, max_results: int = 5):
    """
    Fetch simple news using gNews (free).
    """
    url = f"https://gnews.io/api/v4/search?q={query}&lang=en&max={max_results}&token=demo"  # replace token later

    try:
        data = requests.get(url).json()
        articles = data.get("articles", [])
        return [
            {"title": a["title"], "description": a["description"], "url": a["url"]}
            for a in articles
        ]
    except Exception as e:
        return {"error": str(e)}
