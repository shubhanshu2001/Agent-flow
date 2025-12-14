# app/agents/multi_agent_graph.py

import operator
from app.core.config import get_settings
from typing import TypedDict, Annotated, List

from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.messages import (BaseMessage, AIMessage, SystemMessage)
from langchain_core.messages import ToolMessage
from app.tools.registry import TOOLS_REGISTRY

settings = get_settings()

tools = list(TOOLS_REGISTRY.values())

# 1. Define the shared LLM used by all agents (Groq)
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=settings.groq_api_key,
    temperature=0.2,
).bind_tools(tools)


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]


def tool_node(state: AgentState) -> AgentState:

    last_msg = state["messages"][-1]
    tool_calls = getattr(last_msg, "tool_calls", [])

    if not tool_calls:
        return state
    
    tool_call = tool_calls[0]  
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]

    tool_fn = TOOLS_REGISTRY.get(tool_name)
    if tool_fn is None:
        return {"messages": [ToolMessage(
            content=f"Tool '{tool_name}' not found.",
            name=tool_name,
            tool_call_id=tool_call["id"],
        )]}

    result = tool_fn.invoke(tool_args)

    tool_msg = ToolMessage(
        content=str(result),
        name=tool_name,
        tool_call_id=tool_call["id"],
    )

    return {"messages": [tool_msg]}


def planner_node(state: AgentState) -> AgentState:

    messages = state["messages"]

    prompt = [
        SystemMessage(
            content=("""   
                You are the PLANNER agent.

                Your job is:
                1. Understand the user’s query and goal.
                2. Produce a short, 2–6 step plan describing how the EXECUTOR should answer.
                3. Identify exactly which of the allowed tools (if any) might be needed.
                4. NEVER call tools yourself. ONLY describe the plan.

                IMPORTANT:
                - NEVER mention or suggest any tool named "python", "code_interpreter", or any tool not listed below.
                - If a tool is required, reference the correct tool name from this list.

                ALLOWED TOOLS:
                - currency_convert(amount, from_currency, to_currency)
                - get_current_datetime(format: str = "%Y-%m-%d %H:%M:%S"):(format)
                - get_news(query, max_results)
                - translate_language(text, target_lang)
                - get_weather(city)
                - web_search(query, max_results)

                RULES:
                - If no tool is appropriate, note that in the plan.
                - The EXECUTOR will choose the final tool or fallback.
                - Do NOT give the final answer.
                """
            )
        )
    ] + messages

    result = llm.invoke(prompt)
    return {"messages": [result]}


def executor_node(state: AgentState) -> AgentState:
    messages = state["messages"]

    prompt = [
        SystemMessage(
            content=("""                     
                You are the EXECUTOR agent.

                Your responsibilities:
                - Follow the PLANNER’s plan.
                - Decide whether a tool is needed for the user’s request.
                - If the plan suggests a tool, use that tool.
                - If no suitable tool exists, use the 'web_search' tool as a fallback.
                - If no tool is needed, answer directly.

                CRITICAL RULES:
                - You MUST NOT call any tool named "python", "python_exec",
                "code_interpreter", "calculator", or any other undefined tool.
                - ONLY call tools from the following list:

                ALLOWED TOOLS:
                - currency_convert(amount, from_currency, to_currency)
                - get_current_datetime(format: str = "%Y-%m-%d %H:%M:%S"):(format)
                - get_news(query, max_results)
                - translate_language(text, target_lang)
                - get_weather(city)
                - web_search(query, max_results)

                TOOL CALL RULES:
                - You may call EXACTLY ONE tool if needed.
                - The tool call must contain ONLY the tool call.
                - Arguments must match the tool signature exactly.
                - If the plan indicates tool usage but the needed tool does not exist,
                fallback to 'web_search'.

                ANSWER RULES:
                - After receiving tool output, produce a clear, correct final answer.
                - NEVER mention planning, tools, or roles in your final output.
                """
            )
        )
    ] + messages

    result = llm.invoke(prompt)
    return {"messages": [result]}


def critic_node(state: AgentState) -> AgentState:
    messages = state["messages"]

    prompt = [
        SystemMessage(
            content=("""
                You are the CRITIC agent.

                Your role:
                - Review the latest assistant answer from the EXECUTOR.
                - Improve clarity, correctness, factual accuracy, grammar, and structure.
                - Ensure the answer fully satisfies the user's request.
                - Keep the same meaning and tone.
                - DO NOT call tools.
                - DO NOT introduce new facts.
                - If the answer is already good, return it unchanged.

                Note:
                You NEVER call or suggest the "python" tool or any undefined tool.
                """
            )
        )
    ] + messages

    result = llm.invoke(prompt)
    return {"messages": [result]}

def route_from_executor(state: AgentState):

    last = state["messages"][-1]
    tool_calls = getattr(last, "tool_calls", [])

    if tool_calls:
        return "tool_node"
    
    return "critic"


graph = StateGraph(AgentState)

graph.add_node("planner", planner_node)
graph.add_node("executor", executor_node)
graph.add_node("tool_node", tool_node)
graph.add_node("critic", critic_node)

graph.add_edge(START, "planner")
graph.add_edge("planner", "executor")
graph.add_conditional_edges(
    "executor",
    route_from_executor,
    {
        "tool_node": "tool_node",
        "critic": "critic"
    }
)
graph.add_edge("tool_node", "executor")
graph.add_edge("critic", END)

multi_agent_app = graph.compile()