# app/tools/registry.py
from typing import Any, Dict, Callable
from langchain_core.tools import tool

TOOLS_REGISTRY: Dict[str, Callable[..., Any]] = {}


def register_tool(name: str):
    """
    Decorator to register a tool in the global tool registry.
    """

    def wrapper(func):
        lc_tool = tool(func)
        lc_tool.name = name
        TOOLS_REGISTRY[name] = lc_tool
        return lc_tool
    return wrapper
