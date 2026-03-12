from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

class DataProcessingService:
    @staticmethod
    def clean_health_data(data: Dict[str, Any]) -> Dict[str, Any]:
        cleaned = {}
        
        if 'sleep_hours' in data and data['sleep_hours'] is not None:
            cleaned['sleep_hours'] = max(0, min(24, float(data['sleep_hours'])))
        
        if 'stress_level' in data and data['stress_level'] is not None:
            cleaned['stress_level'] = max(0, min(10, int(data['stress_level'])))
        
        if 'steps' in data and data['steps'] is not None:
            cleaned['steps'] = max(0, int(data['steps']))
        
        if 'screen_time' in data and data['screen_time'] is not None:
            cleaned['screen_time'] = max(0, min(24, float(data['screen_time'])))
        
        if 'heart_rate' in data and data['heart_rate'] is not None:
            cleaned['heart_rate'] = max(30, min(220, int(data['heart_rate'])))
        
        if 'calories' in data and data['calories'] is not None:
            cleaned['calories'] = max(0, float(data['calories']))
        
        return cleaned

    @staticmethod
    def calculate_daily_averages(records: List[Dict[str, Any]]) -> Dict[str, float]:
        if not records:
            return {}
        
        sums = {}
        counts = {}
        
        for record in records:
            for key in ['sleep_hours', 'stress_level', 'steps', 'screen_time', 'heart_rate', 'calories']:
                if key in record and record[key] is not None:
                    sums[key] = sums.get(key, 0) + record[key]
                    counts[key] = counts.get(key, 0) + 1
        
        averages = {}
        for key in sums:
            if counts[key] > 0:
                averages[f'{key}_avg'] = round(sums[key] / counts[key], 2)
        
        return averages

    @staticmethod
    def prepare_for_pattern_analysis(records: List[Dict[str, Any]]) -> List[Dict]:
        return records

    @staticmethod
    def calculate_trends(records: List[Dict[str, Any]], metric: str) -> Dict[str, Any]:
        if not records or metric not in records[0]:
            return {"trend": "neutral", "change": 0}
        
        values = [r.get(metric) for r in records if r.get(metric) is not None]
        
        if len(values) < 2:
            return {"trend": "neutral", "change": 0}
        
        recent = sum(values[-3:]) / min(3, len(values))
        previous = sum(values[:-3]) / max(1, len(values) - 3) if len(values) > 3 else values[0]
        
        if previous == 0:
            return {"trend": "neutral", "change": 0}
        
        change = ((recent - previous) / previous) * 100
        
        if change > 5:
            trend = "improving"
        elif change < -5:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "change": round(change, 2),
            "recent_avg": round(float(recent), 2),
            "previous_avg": round(float(previous), 2)
        }

    @staticmethod
    def get_comparison_to_yesterday(today: Optional[Dict[str, Any]], yesterday: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not today or not yesterday:
            return {}
        
        comparison = {}
        metrics = ['sleep_hours', 'stress_level', 'steps', 'screen_time', 'heart_rate', 'calories']
        
        for metric in metrics:
            if metric in today and metric in yesterday and yesterday.get(metric) is not None:
                today_val = today.get(metric, 0)
                yesterday_val = yesterday.get(metric, 0)
                
                if yesterday_val == 0:
                    comparison[metric] = "N/A"
                else:
                    change = ((today_val - yesterday_val) / yesterday_val) * 100
                    if change > 0:
                        comparison[metric] = f"+{round(change, 1)}%"
                    else:
                        comparison[metric] = f"{round(change, 1)}%"
        
        return comparison
