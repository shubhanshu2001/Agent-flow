# app/tools/datetime_tool.py
from datetime import datetime
from app.tools.registry import register_tool

@register_tool("get_current_datetime")
def get_current_datetime(format: str = "%Y-%m-%d %H:%M:%S"):

    """Return the current datetime in the given format."""
    
    return {"datetime": datetime.now().strftime(format)}
