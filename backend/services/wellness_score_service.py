import numpy as np
from typing import Dict, Any, Optional, List

class WellnessScoreService:
    SLEEP_WEIGHT = 0.30
    ACTIVITY_WEIGHT = 0.25
    HEART_RATE_WEIGHT = 0.25
    STRESS_WEIGHT = 0.20
    
    SLEEP_OPTIMAL = 7.5
    SLEEP_MIN = 5
    STEPS_OPTIMAL = 10000
    STEPS_MIN = 3000
    HEART_RATE_REST_OPTIMAL = 70
    HEART_RATE_REST_MAX = 90
    STRESS_MIN = 3
    STRESS_MAX = 8
    
    @staticmethod
    def calculate_sleep_score(sleep_hours: Optional[float]) -> float:
        if sleep_hours is None:
            return 50.0
        
        if sleep_hours >= WellnessScoreService.SLEEP_OPTIMAL:
            return 100.0
        
        if sleep_hours <= WellnessScoreService.SLEEP_MIN:
            return 20.0
        
        score = 20 + ((sleep_hours - WellnessScoreService.SLEEP_MIN) / 
                     (WellnessScoreService.SLEEP_OPTIMAL - WellnessScoreService.SLEEP_MIN)) * 80
        return max(0, min(100, score))
    
    @staticmethod
    def calculate_activity_score(steps: Optional[int], calories: Optional[float]) -> float:
        score = 0
        steps_contribution = 0
        calories_contribution = 0
        
        if steps is not None:
            if steps >= WellnessScoreService.STEPS_OPTIMAL:
                steps_contribution = 100
            elif steps <= WellnessScoreService.STEPS_MIN:
                steps_contribution = 20
            else:
                steps_contribution = 20 + ((steps - WellnessScoreService.STEPS_MIN) / 
                                          (WellnessScoreService.STEPS_OPTIMAL - WellnessScoreService.STEPS_MIN)) * 80
        
        if calories is not None:
            if calories >= 2000:
                calories_contribution = 100
            elif calories < 500:
                calories_contribution = 20
            else:
                calories_contribution = 20 + ((calories - 500) / 1500) * 80
        
        if steps is not None and calories is not None:
            score = (steps_contribution * 0.6 + calories_contribution * 0.4)
        elif steps is not None:
            score = steps_contribution
        elif calories is not None:
            score = calories_contribution
        else:
            score = 50.0
        
        return max(0, min(100, score))
    
    @staticmethod
    def calculate_heart_rate_score(heart_rate: Optional[int]) -> float:
        if heart_rate is None:
            return 50.0
        
        if heart_rate <= WellnessScoreService.HEART_RATE_REST_OPTIMAL:
            return 100.0
        
        if heart_rate >= WellnessScoreService.HEART_RATE_REST_MAX:
            return 30.0
        
        score = 100 - ((heart_rate - WellnessScoreService.HEART_RATE_REST_OPTIMAL) / 
                      (WellnessScoreService.HEART_RATE_REST_MAX - WellnessScoreService.HEART_RATE_REST_OPTIMAL)) * 70
        return max(0, min(100, score))
    
    @staticmethod
    def calculate_stress_score(stress_level: Optional[int]) -> float:
        if stress_level is None:
            return 50.0
        
        if stress_level <= WellnessScoreService.STRESS_MIN:
            return 100.0
        
        if stress_level >= WellnessScoreService.STRESS_MAX:
            return 20.0
        
        score = 100 - ((stress_level - WellnessScoreService.STRESS_MIN) / 
                      (WellnessScoreService.STRESS_MAX - WellnessScoreService.STRESS_MIN)) * 80
        return max(0, min(100, score))
    
    @classmethod
    def calculate_overall_score(cls, health_data: Dict[str, Any]) -> Dict[str, float]:
        sleep_hours = health_data.get('sleep_hours')
        steps = health_data.get('steps')
        calories = health_data.get('calories')
        heart_rate = health_data.get('heart_rate')
        stress_level = health_data.get('stress_level')
        
        sleep_score = cls.calculate_sleep_score(sleep_hours)
        activity_score = cls.calculate_activity_score(steps, calories)
        heart_rate_score = cls.calculate_heart_rate_score(heart_rate)
        stress_score = cls.calculate_stress_score(stress_level)
        
        overall_score = (
            (sleep_score * cls.SLEEP_WEIGHT) +
            (activity_score * cls.ACTIVITY_WEIGHT) +
            (heart_rate_score * cls.HEART_RATE_WEIGHT) +
            (stress_score * cls.STRESS_WEIGHT)
        )
        
        return {
            "overall_score": round(overall_score, 2),
            "sleep_score": round(sleep_score, 2),
            "activity_score": round(activity_score, 2),
            "heart_rate_score": round(heart_rate_score, 2),
            "stress_score": round(stress_score, 2)
        }
    
    @staticmethod
    def get_score_color(score: float) -> str:
        if score >= 75:
            return "green"
        elif score >= 50:
            return "yellow"
        else:
            return "red"
    
    @staticmethod
    def get_score_label(score: float) -> str:
        if score >= 85:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 60:
            return "Fair"
        elif score >= 50:
            return "Needs Improvement"
        else:
            return "Poor"
