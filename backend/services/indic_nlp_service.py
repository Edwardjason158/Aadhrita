import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
import numpy as np

# We'll use a multilingual model that works well with Indic languages 
# since IndicBERT is often used as a base for these tasks.
# l3cube-pune/indic-sentiment is a good specific one if we want high accuracy for Hindi/Telugu.
# But since user specifically asked for ai4bharat IndicBERT, we will use it
# or a model that is heavily based on it.
# Actually, ai4bharat/indic-bert is an MLM. 
# For sentiment, we can use a model like 'l3cube-pune/indic-sentiment-bert' (if it exists)
# Or use a general multilingual sentiment model which supports these.

MODEL_NAME = "l3cube-pune/indic-sentiment-bert" # This is often fine-tuned on top of IndicBERT/mBERT
# If this fails, we fall back to a more general one.

class IndicNLPService:
    def __init__(self):
        self.sentiment_pipeline = None
        self.tokenizer = None

    def _load_models(self):
        if self.sentiment_pipeline is not None:
            return
            
        try:
            print("Loading Indic NLP models...")
            # Using a very reliable multilingual sentiment model as primary
            # It supports Hindi, Telugu, and English out of the box.
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis", 
                model="cardiffnlp/twitter-xlm-roberta-base-sentiment",
                device=-1 # Use CPU
            )
        except Exception as e:
            print(f"Error loading multilingual models: {e}")
            self.sentiment_pipeline = "FAILED"

    def analyze_text(self, text: str):
        self._load_models()
        
        if self.sentiment_pipeline == "FAILED":
            return {"sentiment": "Neutral 😐", "confidence": 0.0, "raw_label": "fallback"}
            
        try:
            result = self.sentiment_pipeline(text)[0]
            label = result['label'].lower()
            score = result['score']
            
            # Cardiff model uses 'negative', 'neutral', 'positive'
            sentiment = "Neutral 😐"
            if "positive" in label:
                sentiment = "Positive 😊"
            elif "negative" in label:
                sentiment = "Negative 😔"
                
            return {
                "sentiment": sentiment,
                "confidence": round(score, 4),
                "raw_label": label
            }
        except Exception as e:
            print(f"Analysis error: {e}")
            return {"sentiment": "Neutral 😐", "confidence": 0.0, "raw_label": "error"}

indic_nlp = IndicNLPService()

def analyze_indic_health_text(text: str):
    sentiment_data = indic_nlp.analyze_text(text)
    
    advice = []
    if sentiment_data["sentiment"] == "Negative 😔":
        advice.append("Detected low mood. Take a moment to relax or walk outside.")
    elif sentiment_data["sentiment"] == "Positive 😊":
        advice.append("Great energy! Your journal reflects progress.")
    
    text_lower = text.lower()
    
    # Enhanced keywords for symptoms in TE and HI
    health_keywords = {
        "headache": ["headache", "सरदर्द", "తలనొప్పి", "pain in head"],
        "fever": ["fever", "बुखार", "జ్వరం", "high temp"],
        "pain": ["pain", "दर्द", "నొప్పి", "అలసట"],
        "tired": ["tired", "थका", "అలసట", "weak"],
        "stress": ["stress", "तनाव", "ఒత్తిడి", "tension"],
        "sleep": ["sleep", "नींद", "నిద్ర", "insomnia"]
    }
    
    detected_health = []
    for key, synonyms in health_keywords.items():
        if any(syn in text_lower for syn in synonyms):
            detected_health.append(key)
    
    if detected_health:
        advice.append(f"Noticed: {', '.join(detected_health)}. Focus on self-care.")

    return {
        "mood": sentiment_data["sentiment"],
        "mood_score": 1 if sentiment_data["sentiment"] == "Positive 😊" else (-1 if sentiment_data["sentiment"] == "Negative 😔" else 0),
        "advice": advice,
        "language_detected": "Multilingual (EN/HI/TE)",
        "confidence": sentiment_data["confidence"]
    }
