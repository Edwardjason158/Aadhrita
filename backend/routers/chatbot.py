import os
import sys
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Literal, Union
import json
import requests

from backend.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, PRIMARY_MODEL
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, Annotated
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

class ChatRequest(BaseModel):
    user_id: Any
    message: str
    language: str = "en"

# We use ChatOpenAI because OpenRouter is fully compatible with OpenAI structure
llm = ChatOpenAI(
    model=PRIMARY_MODEL,
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base=OPENROUTER_BASE_URL,
    temperature=0.7,
)

@tool
def research_health_topic(query: str) -> str:
    """Useful to search Wikipedia for health topics or general knowledge."""
    try:
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(" ", "_")
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            return resp.json().get("extract", "No additional info found.")
    except Exception:
        pass
    return "No research results found for this query."

tools = [research_health_topic]
try:
    llm_with_tools = llm.bind_tools(tools)
except Exception:
    llm_with_tools = llm

class State(TypedDict):
    messages: Annotated[list, add_messages]
    language: str

def chatbot_node(state: State):
    lang_map = {
        "en": "English",
        "hi": "Hindi",
        "te": "Telugu"
    }
    target_lang = lang_map.get(state.get("language", "en"), "English")
    
    sys_msg = SystemMessage(
        content=f"You are a helpful Wellbeing and Health Assistant for the Wellness Dashboard app. "
        f"You MUST communicate and respond in {target_lang}. "
        f"If the user asks about health topics or recent research, use your search tool. "
        f"Be very concise, empathetic, and informative."
    )
    
    msgs = state["messages"]
    if not msgs or not getattr(msgs[0], "type", "") == "system":
        msgs = [sys_msg] + msgs
        
    response = llm_with_tools.invoke(msgs)
    return {"messages": [response]}

def should_continue(state: State) -> Literal["tools", END]:
    messages = state["messages"]
    last_message = messages[-1]
    # If the LLM makes a tool call, route to tools
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return END

tool_node = ToolNode(tools=[research_health_topic])

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot_node)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", should_continue)
graph_builder.add_edge("tools", "chatbot")

memory = MemorySaver()
app_graph = graph_builder.compile(checkpointer=memory)

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    uid_str = str(request.user_id)
    config = {"configurable": {"thread_id": uid_str}}

    # Dummy check for missing local configuration
    if not OPENROUTER_API_KEY or "your_" in OPENROUTER_API_KEY or OPENROUTER_API_KEY == "test":
        import requests
        
        # Get existing state from LangGraph
        state = app_graph.get_state(config)
        existing_messages = []
        if state and state.values and "messages" in state.values:
            existing_messages = list(state.values["messages"])
        
        user_msg = request.message.lower()
        reply = ""
        
        # Determine dynamic mock response
        if "sleep" in user_msg:
            reply = "I noticed you mentioned sleep! Getting 7-8 hours is essential for recovery. Have you been tracking your sleep schedule? (Mock Mode)"
        elif "stress" in user_msg or "anxious" in user_msg:
            reply = "Stress and anxiety can be tough. Remember to take deep breaths, step away from screens, or do a light walk. (Mock Mode)"
        elif "food" in user_msg or "diet" in user_msg or "water" in user_msg:
            reply = "A balanced diet and proper hydration fuel your body! Make sure to drink plenty of water today. (Mock Mode)"
        elif "history" in user_msg or "remember" in user_msg:
            reply = f"I remember our chat history! We have {len(existing_messages)} previous messages in this session. (Mock Mode)"
        elif "?" in user_msg or "what is" in user_msg:
            words = user_msg.replace("?", "").split()
            topic = [w for w in words if len(w) > 3][-1] if any(len(w)>3 for w in words) else words[-1]
            try:
                # Add proper capitalization and User-Agent 
                topic_capitalized = topic.capitalize()
                url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + topic_capitalized
                headers = {'User-Agent': 'WellnessDashboardBot/1.0'}
                resp = requests.get(url, headers=headers, timeout=3)
                if resp.status_code == 200:
                    data = resp.json().get("extract", "")
                    if data:
                        reply = f"Here is some information about {topic}: {data} (Mock Mode)"
            except:
                pass
                
        if not reply:
            reply = f"I hear you saying: '{request.message}'. As your Wellness Assistant, I'm analyzing that to support you! (Mock Mode)"
            
        print(f"Mocking dynamic response. Missing valid OPENROUTER_API_KEY.")
        
        # Update checkpointer manually so history works
        new_messages = existing_messages + [HumanMessage(content=request.message), AIMessage(content=reply)]
        app_graph.update_state(config, {"messages": new_messages}, as_node="__start__")
        
        return {"reply": reply}

    
    try:
        events = app_graph.invoke(
            {
                "messages": [HumanMessage(content=request.message)],
                "language": request.language
            },
            config=config
        )
        
        last_msg = events["messages"][-1]
        
        # If open router blocks tool calling temporarily, it may fail
        return {
            "reply": last_msg.content
        }
    except Exception as e:
        print(f"Chatbot error: {str(e)}")
        sys_prompt = f"You are a caring Wellness Assistant speaking {request.language}. User says: {request.message}"
        try:
            fallback = llm.invoke([SystemMessage(content=sys_prompt)])
            return {"reply": fallback.content}
        except:
            return {"reply": "I am experiencing temporary technical difficulties."}

@router.get("/history/{user_id}")
async def chat_history(user_id: str):
    config = {"configurable": {"thread_id": user_id}}
    try:
        state = app_graph.get_state(config)
        output = []
        if state and state.values and "messages" in state.values:
            for m in state.values["messages"]:
                if isinstance(m, HumanMessage):
                    output.append({"sender": "user", "text": m.content})
                elif isinstance(m, AIMessage) and m.content:
                    output.append({"sender": "bot", "text": m.content})
        return {"history": output}
    except Exception as e:
        print(f"History error: {e}")
        return {"history": []}

@router.delete("/history/{user_id}")
async def clear_history(user_id: str):
    config = {"configurable": {"thread_id": user_id}}
    try:
        # Reset checkpointer state memory in-memory for this thread
        app_graph.update_state(config, {"messages": []}, as_node="__start__")
        return {"status": "cleared"}
    except:
        return {"status": "failed to clear"}
