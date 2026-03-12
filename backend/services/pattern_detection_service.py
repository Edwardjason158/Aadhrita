from typing import List, Dict, Any
from datetime import datetime

class PatternDetectionService:
    def __init__(self):
        self.patterns = []
    
    def detect_patterns(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if len(records) < 3:
            return []
        
        patterns = []
        
        patterns.extend(self._detect_sleep_stress_pattern(records))
        patterns.extend(self._detect_screen_sleep_pattern(records))
        patterns.extend(self._detect_activity_heart_rate_pattern(records))
        patterns.extend(self._detect_stress_level_pattern(records))
        patterns.extend(self._detect_low_sleep_pattern(records))
        
        return patterns
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        if len(x) < 2:
            return 0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)
        sum_y2 = sum(yi * yi for yi in y)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = ((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)) ** 0.5
        
        if denominator == 0:
            return 0
        
        return numerator / denominator
    
    def _detect_sleep_stress_pattern(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        patterns = []
        
        sleep_values = [r.get('sleep_hours') for r in records if r.get('sleep_hours') is not None]
        stress_values = [r.get('stress_level') for r in records if r.get('stress_level') is not None]
        
        if len(sleep_values) >= 3 and len(stress_values) >= 3 and len(sleep_values) == len(stress_values):
            corr = self._calculate_correlation(sleep_values, stress_values)
            
            if corr < -0.5:
                high_stress_low_sleep = [r for r in records if r.get('sleep_hours', 0) < 6 and r.get('stress_level', 0) > 7]
                severity = "critical" if len(high_stress_low_sleep) >= 2 else "high"
                
                patterns.append({
                    "pattern_type": "Sleep Stress Connection",
                    "description": "Lower sleep hours are associated with higher stress levels. Your sleep and stress appear to be inversely related.",
                    "signals_involved": "sleep_hours, stress_level",
                    "severity": severity,
                    "correlation": round(corr, 3)
                })
        
        return patterns
    
    def _detect_screen_sleep_pattern(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        patterns = []
        
        screen_values = [r.get('screen_time') for r in records if r.get('screen_time') is not None]
        sleep_values = [r.get('sleep_hours') for r in records if r.get('sleep_hours') is not None]
        
        if len(screen_values) >= 3 and len(sleep_values) >= 3 and len(screen_values) == len(sleep_values):
            corr = self._calculate_correlation(screen_values, sleep_values)
            
            if corr < -0.5:
                avg_screen = sum(screen_values) / len(screen_values)
                avg_sleep = sum(sleep_values) / len(sleep_values)
                
                if avg_screen > 6 and avg_sleep < 6:
                    patterns.append({
                        "pattern_type": "Screen Sleep Disruption",
                        "description": "High screen time (>6 hours) is associated with poor sleep (<6 hours). Digital exposure may be affecting your sleep quality.",
                        "signals_involved": "screen_time, sleep_hours",
                        "severity": "high",
                        "correlation": round(corr, 3)
                    })
        
        return patterns
    
    def _detect_activity_heart_rate_pattern(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        patterns = []
        
        steps_values = [r.get('steps') for r in records if r.get('steps') is not None]
        hr_values = [r.get('heart_rate') for r in records if r.get('heart_rate') is not None]
        
        if len(steps_values) >= 3 and len(hr_values) >= 3 and len(steps_values) == len(hr_values):
            corr = self._calculate_correlation(steps_values, hr_values)
            
            if corr < -0.5:
                avg_steps = sum(steps_values) / len(steps_values)
                avg_hr = sum(hr_values) / len(hr_values)
                
                if avg_steps < 3000 and avg_hr > 90:
                    patterns.append({
                        "pattern_type": "Low Activity High Heart Rate",
                        "description": "Low physical activity combined with elevated heart rate. Your body may be under stress due to inactivity.",
                        "signals_involved": "steps, heart_rate",
                        "severity": "medium",
                        "correlation": round(corr, 3)
                    })
        
        return patterns
    
    def _detect_stress_level_pattern(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        patterns = []
        
        high_stress_days = [r for r in records if r.get('stress_level', 0) >= 8]
        
        if len(high_stress_days) >= 2:
            patterns.append({
                "pattern_type": "Critical Stress Level",
                "description": f"High stress levels (8+) detected on {len(high_stress_days)} days. This could impact your overall health and productivity.",
                "signals_involved": "stress_level",
                "severity": "critical",
                "high_stress_days": len(high_stress_days)
            })
        
        return patterns
    
    def _detect_low_sleep_pattern(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        patterns = []
        
        low_sleep_days = [r for r in records if r.get('sleep_hours', 0) < 6]
        
        if len(low_sleep_days) >= 2:
            patterns.append({
                "pattern_type": "Low Sleep",
                "description": f"Consistently low sleep (<6 hours) detected on {len(low_sleep_days)} days. This can affect cognitive function and overall health.",
                "signals_involved": "sleep_hours",
                "severity": "high" if len(low_sleep_days) >= 3 else "medium",
                "low_sleep_days": len(low_sleep_days)
            })
        
        return patterns
    
    def calculate_correlation_matrix(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {}
    
    def predict_future_trend(self, records: List[Dict[str, Any]], metric: str, days_ahead: int = 7) -> Dict[str, Any]:
        return {"prediction": None, "confidence": 0}
