import os
import sys
import json
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, PRIMARY_MODEL

class IndicNLPService:
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.base_url = OPENROUTER_BASE_URL
        self.model = PRIMARY_MODEL

    def analyze_text(self, text: str):
        if not self.api_key:
            return self._fallback_analyze(text)
            
        system_prompt = """You are an AI wellness journal analyzer. Analyze the user's journal entry.
The entry could be in English, Hindi, or Telugu.

Respond ONLY with a valid JSON in the exact structure below, no markdown, no other text:
{
  "sentiment": "Positive 😊" | "Negative 😔" | "Neutral 😐",
  "confidence": 0.95
}
"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                "response_format": {"type": "json_object"}
            }
            response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                data = json.loads(content)
                
                return {
                    "sentiment": data.get("sentiment", "Neutral 😐"),
                    "confidence": float(data.get("confidence", 0.8)),
                    "raw_label": data.get("sentiment", "Neutral")
                }
        except Exception as e:
            print(f"OpenRouter analysis error: {e}")
            
        return self._fallback_analyze(text)

    def _fallback_analyze(self, text: str):
        # Basic rule-based fallback if API fails
        text_lower = text.lower()
        positive_words = ['happy', 'good', 'great', 'excellent', 'खुश', 'अच्छा', 'సంతోషం', 'మంచి']
        negative_words = ['sad', 'bad', 'terrible', 'depressed', 'दुखी', 'खराब', 'బాధ', 'చెడ్డ']
        
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        
        if pos_count > neg_count:
            return {"sentiment": "Positive 😊", "confidence": 0.8, "raw_label": "positive"}
        elif neg_count > pos_count:
            return {"sentiment": "Negative 😔", "confidence": 0.8, "raw_label": "negative"}
        
        return {"sentiment": "Neutral 😐", "confidence": 0.5, "raw_label": "neutral"}


indic_nlp = IndicNLPService()

def analyze_indic_health_text(text: str):
    sentiment_data = indic_nlp.analyze_text(text)
    
    advice = []
    if "Negative" in sentiment_data["sentiment"]:
        advice.append("Detected low mood. Take a moment to relax or walk outside.")
    elif "Positive" in sentiment_data["sentiment"]:
        advice.append("Great energy! Your journal reflects progress.")
    else:
        advice.append("A balanced day. Keep maintaining your routines.")
    
    text_lower = text.lower()
    
    # Enhanced keywords for symptoms in TE, HI, EN
    health_keywords = {
        "headache": ["headache", "सरदर्द", "तలనొప్పి", "pain in head"],
        "fever": ["fever", "बुखार", "జ్వరం", "high temp"],
        "pain": ["pain", "दर्द", "నొప్పి", "అలసట"],
        "tired": ["tired", "थका", "అలసట", "weak", "exhausted"],
        "stress": ["stress", "तनाव", "ఒత్తిడి", "tension", "anxious"],
        "sleep": ["sleep", "नींद", "నిద్ర", "insomnia", "awake"]
    }
    
    detected_health = []
    for key, synonyms in health_keywords.items():
        if any(syn in text_lower for syn in synonyms):
            detected_health.append(key)
    
    if detected_health:
        advice.append(f"Noticed: {', '.join(detected_health)}. Focus on self-care.")

    score = 0
    if "Positive" in sentiment_data["sentiment"]: score = 1
    elif "Negative" in sentiment_data["sentiment"]: score = -1

    return {
        "mood": sentiment_data["sentiment"],
        "mood_score": score,
        "advice": advice,
        "language_detected": "Multilingual (EN/HI/TE)",
        "confidence": sentiment_data["confidence"]
    }
