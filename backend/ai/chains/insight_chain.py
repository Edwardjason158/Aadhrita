import os
import sys
import json
from typing import Dict, Any, Optional, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, PRIMARY_MODEL, BACKUP_MODEL

try:
    from langchain_community.llms import OpenRouter
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate
    from langchain.memory import ConversationBufferMemory
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    pass

class InsightChain:
    def __init__(self):
        self.llm = None
        self.memory = {}
        self.primary_model = PRIMARY_MODEL
        self.backup_model = BACKUP_MODEL
        
        if LANGCHAIN_AVAILABLE and OPENROUTER_API_KEY:
            try:
                self.llm = OpenRouter(
                    model=self.primary_model,
                    openrouter_api_key=OPENROUTER_API_KEY,
                    openrouter_base_url=OPENROUTER_BASE_URL,
                    max_tokens=500,
                    temperature=0.7
                )
            except Exception as e:
                print(f"Failed to initialize primary model: {e}")
                try:
                    self.llm = OpenRouter(
                        model=self.backup_model,
                        openrouter_api_key=OPENROUTER_API_KEY,
                        openrouter_base_url=OPENROUTER_BASE_URL,
                        max_tokens=500,
                        temperature=0.7
                    )
                    self.primary_model = self.backup_model
                except Exception as e2:
                    print(f"Failed to initialize backup model: {e2}")
    
    def get_memory(self, user_id: int) -> Optional[Any]:
        if not LANGCHAIN_AVAILABLE:
            return None
        if user_id not in self.memory:
            from langchain.memory import ConversationBufferMemory
            self.memory[user_id] = ConversationBufferMemory(
                memory_key="history",
                input_key="input",
                output_key="output"
            )
        return self.memory[user_id]
    
    def generate_daily_insight(self, health_data: Dict[str, Any], patterns: List[Dict], lang: str = "en") -> Dict[str, Any]:
        if not self.llm:
            return self._fallback_insight(health_data, patterns, lang)
        
        prompt = self._build_daily_prompt(health_data, patterns, lang)
        
        try:
            response = self.llm(prompt)
            return self._parse_insight_response(response)
        except Exception as e:
            print(f"Error generating insight: {e}")
            return self._fallback_insight(health_data, patterns)
    
    def generate_weekly_summary(self, weekly_data: List[Dict], patterns: List[Dict]) -> Dict[str, Any]:
        if not self.llm:
            return self._fallback_weekly_summary(weekly_data)
        
        prompt = self._build_weekly_prompt(weekly_data, patterns)
        
        try:
            response = self.llm(prompt)
            return self._parse_weekly_response(response)
        except Exception as e:
            print(f"Error generating weekly summary: {e}")
            return self._fallback_weekly_summary(weekly_data)
    
    def generate_pattern_insight(self, pattern: Dict, health_context: Dict) -> str:
        if not self.llm:
            return pattern.get("description", "Pattern detected in your health data.")
        
        prompt = self._build_pattern_prompt(pattern, health_context)
        
        try:
            response = self.llm(prompt)
            return response
        except Exception as e:
            print(f"Error generating pattern insight: {e}")
            return pattern.get("description", "Pattern detected in your health data.")
    
    def _build_daily_prompt(self, health_data: Dict, patterns: List[Dict], lang: str = "en") -> str:
        sleep = health_data.get("sleep_hours", "N/A")
        steps = health_data.get("steps", "N/A")
        heart_rate = health_data.get("heart_rate", "N/A")
        stress = health_data.get("stress_level", "N/A")
        screen_time = health_data.get("screen_time", "N/A")
        calories = health_data.get("calories", "N/A")
        
        language_map = {
            "en": "English",
            "hi": "Hindi",
            "te": "Telugu"
        }
        target_lang = language_map.get(lang, "English")
        
        pattern_text = "\n".join([f"- {p.get('pattern_type')}: {p.get('description')}" for p in patterns]) if patterns else "No patterns detected"
        
        prompt = f"""You are a personal wellness coach. Your role is to help users understand their health data and provide actionable insights to improve their wellbeing.

The user's health data for today:
- Sleep: {sleep} hours
- Steps: {steps} steps
- Heart Rate: {heart_rate} bpm
- Stress Level: {stress}/10
- Screen Time: {screen_time} hours
- Calories: {calories} kcal

Detected Patterns:
{pattern_text}

Generate a friendly, caring, and simple insight in 3-4 sentences (under 150 words).
Then provide exactly 3 specific actionable suggestions that the user can implement today.

IMPORTANT: You MUST generate the entire response (Insight and Suggestions) in {target_lang}.

Format your response as:
Insight: [your 3-4 sentence insight in {target_lang}]

Suggestions:
1. [suggestion 1 in {target_lang}]
2. [suggestion 2 in {target_lang}]
3. [suggestion 3 in {target_lang}]
"""
        return prompt
    
    def _build_weekly_prompt(self, weekly_data: List[Dict], patterns: List[Dict]) -> str:
        if not weekly_data:
            return "No data available"
        
        sleep_values = [d.get("sleep_hours", 0) for d in weekly_data if d.get("sleep_hours")]
        steps_values = [d.get("steps", 0) for d in weekly_data if d.get("steps")]
        
        avg_sleep = sum(sleep_values) / len(sleep_values) if sleep_values else 0
        avg_steps = sum(steps_values) / len(steps_values) if steps_values else 0
        
        pattern_text = "\n".join([f"- {p.get('pattern_type')}: {p.get('description')}" for p in patterns]) if patterns else "No patterns detected"
        
        prompt = f"""You are a personal wellness coach. Analyze the user's weekly health data and provide a comprehensive summary.

Weekly Statistics:
- Average Sleep: {avg_sleep:.1f} hours
- Average Steps: {avg_steps:.0f} steps
- Total Days Tracked: {len(weekly_data)}

Detected Patterns:
{pattern_text}

Generate a weekly summary that includes:
1. Key trends and observations
2. What went well this week
3. Areas that need attention
4. 3-5 goals for next week

Keep the tone friendly, supportive, and motivating.
"""
        return prompt
    
    def _build_pattern_prompt(self, pattern: Dict, health_context: Dict) -> str:
        prompt = f"""You are a personal wellness coach. Explain a health pattern that has been detected in the user's data.

Detected Pattern:
- Type: {pattern.get('pattern_type')}
- Description: {pattern.get('description')}
- Severity: {pattern.get('severity')}
- Signals Involved: {pattern.get('signals_involved')}

Provide a simple, human-friendly explanation of:
1. What this pattern means
2. Why it's harmful (or beneficial)
3. How the user can improve or maintain it

Keep the explanation under 100 words. Use a caring, supportive tone.
"""
        return prompt
    
    def _parse_insight_response(self, response: str) -> Dict[str, Any]:
        insight_text = ""
        suggestions = []
        
        lines = response.split("\n")
        in_insight = False
        in_suggestions = False
        
        for line in lines:
            line = line.strip()
            if line.startswith("Insight:"):
                in_insight = True
                insight_text = line.replace("Insight:", "").strip()
            elif line.startswith("Suggestions:"):
                in_insight = False
                in_suggestions = True
            elif in_suggestions and line:
                if line.startswith("1.") or line.startswith("2.") or line.startswith("3."):
                    suggestion = line.lstrip("123. ").strip()
                    suggestions.append(suggestion)
        
        if not insight_text:
            insight_text = response[:200]
        
        if not suggestions:
            default_suggestions = {
                "en": ["Track your sleep consistently", "Aim for 10,000 steps daily", "Practice stress management techniques"],
                "hi": ["अपनी नींद को लगातार ट्रैक करें", "प्रतिदिन 10,000 कदम चलने का लक्ष्य रखें", "तनाव प्रबंधन तकनीकों का अभ्यास करें"],
                "te": ["మీ నిద్రను క్రమం తప్పకుండా ట్రాక్ చేయండి", "రోజుకు 10,000 అడుగులు వేయాలని లక్ష్యంగా పెట్టుకోండి", "ఒత్తిడి నిర్వహణ పద్ధతులను ప్రాక్టీస్ చేయండి"]
            }
            suggestions = default_suggestions.get("en", default_suggestions["en"])
        
        return {
            "insight": insight_text,
            "suggestions": ", ".join(suggestions),
            "model": self.primary_model
        }
    
    def _parse_weekly_response(self, response: str) -> Dict[str, Any]:
        return {
            "insight": response[:500],
            "suggestions": "",
            "model": self.primary_model
        }
    
    def _fallback_insight(self, health_data: Dict, patterns: List[Dict], lang: str = "en") -> Dict[str, Any]:
        suggestions = []
        insights = []
        
        sleep = health_data.get("sleep_hours")
        steps = health_data.get("steps")
        stress = health_data.get("stress_level")
        heart_rate = health_data.get("heart_rate")
        
        # Simple translations for fallback
        msgs = {
            "en": {
                "sleep_low": f"Your sleep ({sleep}h) is below the recommended 7-8 hours.",
                "sleep_high": f"You got plenty of sleep ({sleep}h) today!",
                "sleep_ok": f"Great job getting {sleep} hours of sleep!",
                "steps_low": f"Your activity level is low with {steps} steps.",
                "steps_high": f"Excellent activity with {steps} steps today!",
                "stress_high": "Your stress levels are quite high today.",
                "hr_high": f"Your heart rate is a bit high ({heart_rate} bpm).",
                "welcome": "Welcome to your wellness dashboard!",
                "s1": "Maintain your current healthy habits",
                "s2": "Continue tracking your health data",
                "s3": "Stay consistent with your routine"
            },
            "hi": {
                "sleep_low": f"आज आपकी नींद ({sleep} घंटे) औसत से कम रही।",
                "sleep_high": f"आज आपको भरपूर नींद ({sleep} घंटे) मिली!",
                "sleep_ok": f"अच्छी नींद ({sleep} घंटे) ली!",
                "steps_low": f"आपके कदम ({steps}) कम रहे।",
                "steps_high": f"आज आपने ({steps} कदम) बहुत अच्छा किया!",
                "stress_high": "आज आपका तनाव स्तर काफी अधिक है।",
                "hr_high": f"आपकी हृदय गति थोड़ी अधिक ({heart_rate} bpm) है।",
                "welcome": "आपके वेलनेस डैशबोर्ड में स्वागत है!",
                "s1": "अपनी वर्तमान स्वस्थ आदतों को बनाए रखें",
                "s2": "अपने स्वास्थ्य डेटा को ट्रैक करना जारी रखें",
                "s3": "अपनी दिनचर्या में निरंतर बने रहें"
            },
            "te": {
                "sleep_low": f"మీ నిద్ర ({sleep} గంటలు) తక్కువగా ఉంది.",
                "sleep_high": f"ఈరోజు మీకు తగినంత నిద్ర ({sleep} గంటలు) లభించింది!",
                "sleep_ok": f"చక్కటి నిద్ర ({sleep} గంటలు) పోయారు!",
                "steps_low": f"మీరు తక్కువ అడుగులు ({steps}) వేశారు.",
                "steps_high": f"ఈరోజు మీరు అద్భుతంగా ({steps} అడుగులు) వేశారు!",
                "stress_high": "ఈరోజు మీ ఒత్తిడి స్థాయిలు ఎక్కువగా ఉన్నాయి.",
                "hr_high": f"మీ హృదయ స్పందన రేటు కొంత ఎక్కువగా ({heart_rate} bpm) ఉంది.",
                "welcome": "మీ వెల్‌నెస్ డ్యాష్‌బోర్డ్‌కు స్వాగతం!",
                "s1": "మీ ప్రస్తుత ఆరోగ్యకరమైన అలవాట్లను కొనసాగించండి",
                "s2": "మీ ఆరోగ్య డేటాను ట్రాక్ చేయడం కొనసాగించండి",
                "s3": "మీ దినచర్యలో స్థిరంగా ఉండండి"
            }
        }
        
        m = msgs.get(lang, msgs["en"])
        
        if sleep:
            if sleep < 6: insights.append(m["sleep_low"])
            elif sleep > 9: insights.append(m["sleep_high"])
            else: insights.append(m["sleep_ok"])
        
        if steps:
            if steps < 5000: insights.append(m["steps_low"])
            elif steps > 10000: insights.append(m["steps_high"])
        
        if stress and stress > 7: insights.append(m["stress_high"])
        if heart_rate and heart_rate > 100: insights.append(m["hr_high"])
        
        if not insights:
            insight = m["welcome"]
        else:
            insight = " ".join(insights[:2])
            
        if not suggestions:
            suggestions = [m["s1"], m["s2"], m["s3"]]
        
        return {
            "insight": insight,
            "suggestions": ", ".join(suggestions[:3]),
            "model": "fallback"
        }
    
    def _fallback_weekly_summary(self, weekly_data: List[Dict]) -> Dict[str, Any]:
        return {
            "insight": "Keep tracking your health data to see weekly trends and patterns.",
            "suggestions": "",
            "model": "fallback"
        }


insight_chain = InsightChain()

def generate_ai_insight(user_id: int, insight_type: str, db, lang: str = "en") -> Dict[str, Any]:
    from backend.models.models import HealthRecord, Pattern
    from datetime import datetime, timedelta
    
    if insight_type == "daily":
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        records = db.query(HealthRecord).filter(
            HealthRecord.user_id == user_id,
            HealthRecord.date >= today
        ).all()
        
        patterns = db.query(Pattern).filter(
            Pattern.user_id == user_id,
            Pattern.detected_at >= today - timedelta(days=7)
        ).all()
        
        if records:
            # Aggregate data from all records for today
            health_data = {
                "sleep_hours": None,
                "steps": None,
                "heart_rate": None,
                "stress_level": None,
                "screen_time": None,
                "calories": None
            }
            
            for record in records:
                if record.sleep_hours is not None: health_data["sleep_hours"] = record.sleep_hours
                if record.steps is not None: health_data["steps"] = record.steps
                if record.heart_rate is not None: health_data["heart_rate"] = record.heart_rate
                if record.stress_level is not None: health_data["stress_level"] = record.stress_level
                if record.screen_time is not None: health_data["screen_time"] = record.screen_time
                if record.calories is not None: health_data["calories"] = record.calories
            
            pattern_list = [{"pattern_type": p.pattern_type, "description": p.description} for p in patterns]
            
            return insight_chain.generate_daily_insight(health_data, pattern_list, lang)
    
    return insight_chain._fallback_insight({}, [], lang)
