# app/agents/multi_agent_graph.py

import operator
from app.core.config import get_settings
from typing import TypedDict, Annotated, List

from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.messages import (BaseMessage, SystemMessage)

settings = get_settings()

# 1. Define the shared LLM used by all agents (Groq)
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=settings.groq_api_key,
    temperature=0.2,
)


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]


def planner_node(state: AgentState) -> AgentState:

    messages = state["messages"]

    prompt = [
        SystemMessage(
            content=(
                "You are a planning agent. Your job is to look at the user's goal "
                "and outline a short, clear plan (2–5 bullet points) for how an AI should answer.\n"
                "Do NOT give the final answer, only the plan."
            )
        )
    ] + messages

    result = llm.invoke(prompt)
    return {"messages": [result]}


def executor_node(state: AgentState) -> AgentState:
    messages = state["messages"]

    prompt = [
        SystemMessage(
            content=(
                "You are an execution agent. You are given:\n"
                "1. The full conversation so far\n"
                "2. A plan from another agent (in one of the last assistant messages)\n\n"
                "Your job is to produce a helpful, detailed answer that follows the plan. "
                "Do NOT include the word 'plan' in your answer."
            )
        )
    ] + messages

    result = llm.invoke(prompt)
    return {"messages": [result]}


def critic_node(state: AgentState) -> AgentState:
    messages = state["messages"]

    prompt = [
        SystemMessage(
            content=(
                "You are a critic and editor agent. You are given the conversation and "
                "the latest assistant answer. Just review it and if you find any issue then correct or improve its structure. And return the final answer for the user."
                "If the previous assistant message it satisfactory then return it as it is."
                "Improve it if needed:\n"
                "- fix any obvious issues\n"
                "- improve clarity and structure\n"
                "- keep the same meaning and tone\n"
                "Respond with the final improved answer."
            )
        )
    ] + messages

    result = llm.invoke(prompt)
    return {"messages": [result]}


graph = StateGraph(AgentState)

graph.add_node("planner", planner_node)
graph.add_node("executor", executor_node)
graph.add_node("critic", critic_node)

graph.add_edge(START, "planner")
graph.add_edge("planner", "executor")
graph.add_edge("executor", "critic")
graph.add_edge("critic", END)

multi_agent_app = graph.compile()