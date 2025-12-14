# app/tools/web_search.py
from tavily import TavilyClient
from app.core.config import get_settings
from app.tools.registry import register_tool
from app.utils.cache import cache_get, cache_set

settings = get_settings()
tavily = TavilyClient(api_key=settings.tavily_api_key)

@register_tool("web_search")
def web_search(query: str, max_results: int = 5):
    """
    Returns list of {title, url, snippet}.
    """

    key = f"search:{query}:{max_results}"
    cached = cache_get(key)
    if cached:
        return cached

    try:
        response = tavily.search(
            query=query,
            max_results=max_results,
        )

        # Tavily returns: {"results": [ ... ]}
        clean_results = []

        for item in response.get("results", []):
            clean_results.append({
                "title": item.get("title"),
                "url": item.get("url"),
                "snippet": item.get("content"),
            })

        cache_set(key, clean_results, ttl=3600)

        return clean_results
    
    except Exception as e:
        return [{"title": "Search Error", "href": None, "snippet": str(e)}]
