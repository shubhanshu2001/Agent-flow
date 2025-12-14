# app/tools/translate.py
import requests
from app.tools.registry import register_tool

@register_tool("translate_language")
def translate_language(text: str, target_lang: str):

    """Translate text from any language to the target language."""
    
    url = "https://api.mymemory.translated.net/get"
    params = {"q": text, "langpair": f"en|{target_lang}"}

    try:
        data = requests.get(url, params=params).json()
        return {"translated": data["responseData"]["translatedText"]}
    except Exception as e:
        return {"error": str(e)}
