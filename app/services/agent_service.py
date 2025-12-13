# app/services/agent_service.py

from typing import List, Dict

from langchain_core.messages import HumanMessage, AIMessage
from app.agents.multi_agent_graph import multi_agent_app


def run_multi_agent(conversation: List[Dict[str, str]]) -> str:

    lc_messages = []
    for msg in conversation:
        role = msg.get("role")
        content = msg.get("content", "")

        if role == "user":
            lc_messages.append(HumanMessage(content=content))
        else:
            lc_messages.append(AIMessage(content=content))

    final_state = multi_agent_app.invoke({
        "messages": lc_messages
    })

    last_msg = final_state["messages"][-1]

    return last_msg.content