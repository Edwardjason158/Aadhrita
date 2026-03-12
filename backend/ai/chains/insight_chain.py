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
    
    def generate_daily_insight(self, health_data: Dict[str, Any], patterns: List[Dict]) -> Dict[str, Any]:
        if not self.llm:
            return self._fallback_insight(health_data, patterns)
        
        prompt = self._build_daily_prompt(health_data, patterns)
        
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
    
    def _build_daily_prompt(self, health_data: Dict, patterns: List[Dict]) -> str:
        sleep = health_data.get("sleep_hours", "N/A")
        steps = health_data.get("steps", "N/A")
        heart_rate = health_data.get("heart_rate", "N/A")
        stress = health_data.get("stress_level", "N/A")
        screen_time = health_data.get("screen_time", "N/A")
        calories = health_data.get("calories", "N/A")
        
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

Format your response as:
Insight: [your 3-4 sentence insight]

Suggestions:
1. [suggestion 1]
2. [suggestion 2]
3. [suggestion 3]
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
            suggestions = [
                "Track your sleep consistently",
                "Aim for 10,000 steps daily",
                "Practice stress management techniques"
            ]
        
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
    
    def _fallback_insight(self, health_data: Dict, patterns: List[Dict]) -> Dict[str, Any]:
        suggestions = []
        insights = []
        
        sleep = health_data.get("sleep_hours")
        steps = health_data.get("steps")
        stress = health_data.get("stress_level")
        heart_rate = health_data.get("heart_rate")
        
        if sleep:
            if sleep < 6:
                insights.append(f"Your sleep ({sleep}h) is below the recommended 7-8 hours, which might affect your energy.")
                suggestions.append("Try to get more sleep - aim for 7-8 hours")
            elif sleep > 9:
                insights.append(f"You got plenty of sleep ({sleep}h) today! Make sure you stay active to balance it out.")
                suggestions.append("Keep active to balance your long rest")
            else:
                insights.append(f"Great job getting {sleep} hours of sleep!")
        
        if steps:
            if steps < 5000:
                insights.append(f"Your activity level is low with {steps} steps.")
                suggestions.append("Increase your daily steps - try a short walk")
            elif steps > 10000:
                insights.append(f"Excellent activity with {steps} steps today!")
                suggestions.append("Keep up the high activity level!")
        
        if stress and stress > 7:
            insights.append("Your stress levels are quite high today.")
            suggestions.append("Consider stress management techniques like meditation")
        
        if heart_rate and heart_rate > 100:
            insights.append(f"Your heart rate is a bit high ({heart_rate} bpm).")
            suggestions.append("Take some time to rest and breathe deeply")
        
        if not insights:
            insight = "Welcome to your wellness dashboard! Start tracking more data to see deeper insights."
        else:
            insight = " ".join(insights[:2]) # Use top 2 insights
            
        if not suggestions:
            suggestions = [
                "Maintain your current healthy habits",
                "Continue tracking your health data",
                "Stay consistent with your routine"
            ]
        
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

def generate_ai_insight(user_id: int, insight_type: str, db) -> Dict[str, Any]:
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
            
            return insight_chain.generate_daily_insight(health_data, pattern_list)
    
    return insight_chain._fallback_insight({}, [])
