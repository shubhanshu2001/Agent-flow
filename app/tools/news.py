# app/tools/news.py
import requests
from app.tools.registry import register_tool
from app.utils.cache import cache_get, cache_set

@register_tool("get_news")
def get_news(query: str, max_results: int = 5):
    """
    Fetch simple news using gNews (free).
    """

    key = f"news:{query}:{max_results}"
    cached = cache_get(key)
    if cached:
        return cached

    try:
        url = f"https://gnews.io/api/v4/search?q={query}&lang=en&max={max_results}&token=demo"
        data = requests.get(url).json().get("articles", [])

        articles = [
            {"title": a["title"], "description": a["description"], "url": a["url"]}
            for a in data
        ]

        cache_set(key, articles, ttl=600)  # 10 minutes
        
        return articles
    
    except Exception as e:
        return {"error": str(e)}
