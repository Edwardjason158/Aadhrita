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
    
    prompt_text = f"""You are an intelligent AI Wellness Assistant designed to help users understand and improve their health habits.

You support multiple languages:
- English
- Telugu
- Hindi

Always respond in the SAME language used by the user. 
If the language is unclear, reply in English. You must currently respond in: {target_lang}.

Your role is to analyze the user's health-related messages and provide helpful wellness guidance.

The user's message may contain information related to:
- sleep hours
- heart rate (BPM)
- stress level
- screen time
- physical activity or steps
- headaches or other symptoms
- mood or daily habits

You also maintain MEMORY of previous user information to understand patterns over time.

Memory Rules:
- Remember important health data shared by the user (sleep hours, screen time, stress, etc.)
- Use previous information to detect unhealthy patterns
- If the user repeatedly reports unhealthy habits, gently mention the pattern

Example:
"If you mentioned earlier that your screen time is very high, it may be contributing to your headaches."

Analysis Steps:
1. Detect the wellness topic.
2. Determine if the habit or data is healthy or unhealthy.
3. Provide a simple explanation.
4. Suggest practical improvements.

Response Format:

Health Insight:
[Explain what the user's data or symptom means in simple language.]

Suggestion:
[Give helpful advice or actions the user can take.]

Wellness Tips:
Provide 1-3 small healthy habits such as:
- yoga or breathing exercises for stress
- drinking enough water
- reducing screen time
- improving sleep schedule
- stretching or walking
- meditation
- eye relaxation (20-20-20 rule)

Communication Style:
- Be supportive and friendly
- Use simple sentences
- Avoid medical diagnosis
- Do not repeat the user's message
- Provide short and clear answers

If the user reports symptoms like headache, stress, or poor sleep, suggest natural wellness practices such as:
- yoga
- meditation
- deep breathing
- short walks
- proper hydration
- better sleep routine
"""
    sys_msg = SystemMessage(content=prompt_text)
    
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
        # Get existing state from LangGraph
        state = app_graph.get_state(config)
        existing_messages = []
        if state and state.values and "messages" in state.values:
            existing_messages = list(state.values["messages"])
            
        try:
            from g4f.client import AsyncClient as G4FClient
            import asyncio
            client = G4FClient()
            
            lang_map = {"en": "English", "hi": "Hindi", "te": "Telugu"}
            target_lang = lang_map.get(request.language, "English")
            prompt_text = f"""You are an intelligent AI Wellness Assistant designed to help users understand and improve their health habits.

You support multiple languages:
- English
- Telugu
- Hindi

Always respond in the SAME language used by the user. 
If the language is unclear, reply in English. You must currently respond in: {target_lang}.

Your role is to analyze the user's health-related messages and provide helpful wellness guidance.

The user's message may contain information related to:
- sleep hours
- heart rate (BPM)
- stress level
- screen time
- physical activity or steps
- headaches or other symptoms
- mood or daily habits

You also maintain MEMORY of previous user information to understand patterns over time.

Memory Rules:
- Remember important health data shared by the user (sleep hours, screen time, stress, etc.)
- Use previous information to detect unhealthy patterns
- If the user repeatedly reports unhealthy habits, gently mention the pattern

Example:
"If you mentioned earlier that your screen time is very high, it may be contributing to your headaches."

Analysis Steps:
1. Detect the wellness topic.
2. Determine if the habit or data is healthy or unhealthy.
3. Provide a simple explanation.
4. Suggest practical improvements.

Response Format:

Health Insight:
[Explain what the user's data or symptom means in simple language.]

Suggestion:
[Give helpful advice or actions the user can take.]

Wellness Tips:
Provide 1-3 small healthy habits such as:
- yoga or breathing exercises for stress
- drinking enough water
- reducing screen time
- improving sleep schedule
- stretching or walking
- meditation
- eye relaxation (20-20-20 rule)

Communication Style:
- Be supportive and friendly
- Use simple sentences
- Avoid medical diagnosis
- Do not repeat the user's message
- Provide short and clear answers

If the user reports symptoms like headache, stress, or poor sleep, suggest natural wellness practices such as:
- yoga
- meditation
- deep breathing
- short walks
- proper hydration
- better sleep routine
"""
            history = [{"role": "system", "content": prompt_text}]
            
            # append history up to 6 messages
            for em in existing_messages[-6:]:
                role = "user" if isinstance(em, HumanMessage) else "assistant"
                history.append({"role": role, "content": em.content})
                
            history.append({"role": "user", "content": request.message})
            async def fetch_g4f():
                return await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=history
                )
            response = await asyncio.wait_for(fetch_g4f(), timeout=12.0)
            reply_raw = response.choices[0].message.content
            # strip out potential provider ads
            reply = reply_raw.split("http")[0].split("Need proxies")[0].strip()
        except Exception as e:
            print(f"G4F fallback failed: {e}")
            import requests
            user_msg = request.message.lower()
            reply = ""
            if "sleep" in user_msg:
                reply = "I noticed you mentioned sleep. Getting 7-8 hours is essential for recovery. Have you been tracking your sleep schedule?\n\nSuggestion:\nTry to go to bed at the same time every day.\n\nWellness Tips:\n- Avoid screens 1 hour before bed\n- Keep your room cool and dark"
            elif "stress" in user_msg or "anxious" in user_msg or "headache" in user_msg:
                reply = "Stress and headaches can be tough. Remember to take deep breaths, step away from screens, or do a light walk.\n\nSuggestion:\nTake a short break to relax your eyes and mind.\n\nWellness Tips:\n- meditation\n- deep breathing\n- eye relaxation (20-20-20 rule)"
            elif "food" in user_msg or "diet" in user_msg or "water" in user_msg:
                reply = "A balanced diet and proper hydration fuel your body! Make sure to drink plenty of water today.\n\nSuggestion:\nKeep a water bottle nearby.\n\nWellness Tips:\n- proper hydration\n- eating more greens"
            elif "history" in user_msg or "remember" in user_msg:
                reply = f"I remember our chat history! We have {len(existing_messages)} previous messages in this session.\n\nSuggestion:\nYou can always refer back to our advice.\n\nWellness Tips:\n- continue tracking your habits"
            elif "?" in user_msg or "what is" in user_msg:
                words = user_msg.replace("?", "").split()
                topic = [w for w in words if len(w) > 3][-1] if any(len(w)>3 for w in words) else words[-1]
                try:
                    topic_capitalized = topic.capitalize()
                    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + topic_capitalized
                    headers = {'User-Agent': 'WellnessDashboardBot/1.0'}
                    resp = requests.get(url, headers=headers, timeout=3)
                    if resp.status_code == 200:
                        data = resp.json().get("extract", "")
                        if data:
                            reply = f"Here is some information about {topic}: {data}\n\nSuggestion:\nConsider learning more about healthy ways to manage this.\n\nWellness Tips:\n- healthy routines"
                except:
                    pass
            if not reply:
                reply = f"I hear you saying: '{request.message}'. As your Wellness Assistant, I'm here to support you! How does that make you feel?\n\nSuggestion:\nKeep observing your habits.\n\nWellness Tips:\n- write in your journal"
            
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
