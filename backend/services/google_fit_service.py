import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_SCOPES

class GoogleFitService:
    BASE_URL = "https://www.googleapis.com/fitness/v1"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    
    def __init__(self, access_token: str, refresh_token: Optional[str] = None):
        self.access_token = access_token
        self.refresh_token = refresh_token
    
    def refresh_access_token(self) -> bool:
        if not self.refresh_token:
            return False
        
        try:
            response = requests.post(self.TOKEN_URL, data={
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "refresh_token": self.refresh_token,
                "grant_type": "refresh_token"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                return True
        except Exception:
            pass
        
        return False
    
    def get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def get_steps(self, start_time: datetime, end_time: datetime) -> Optional[int]:
        try:
            start_millis = int(start_time.timestamp() * 1000)
            end_millis = int(end_time.timestamp() * 1000)
            
            body = {
                "aggregateBy": [{
                    "dataTypeName": "com.google.step_count.delta",
                    "dataSourceId": "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
                }],
                "bucketByTime": {"durationMillis": 86400000},
                "startTimeMillis": start_millis,
                "endTimeMillis": end_millis
            }
            
            response = requests.post(
                f"{self.BASE_URL}/users/me/dataset:aggregate",
                headers=self.get_headers(),
                json=body
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            total_steps = 0
            
            for bucket in data.get("bucket", []):
                for dataset in bucket.get("dataset", []):
                    for point in dataset.get("point", []):
                        for value in point.get("value", []):
                            total_steps += value.get("intVal", 0)
            
            return total_steps
        except Exception:
            return None
    
    def get_heart_rate(self, start_time: datetime, end_time: datetime) -> Optional[float]:
        try:
            start_millis = int(start_time.timestamp() * 1000)
            end_millis = int(end_time.timestamp() * 1000)
            
            body = {
                "aggregateBy": [{
                    "dataTypeName": "com.google.heart_rate.bpm",
                    "dataSourceId": "derived:com.google.heart_rate.bpm:com.google.android.gms:heart_rate_bpm"
                }],
                "bucketByTime": {"durationMillis": 86400000},
                "startTimeMillis": start_millis,
                "endTimeMillis": end_millis
            }
            
            response = requests.post(
                f"{self.BASE_URL}/users/me/dataset:aggregate",
                headers=self.get_headers(),
                json=body
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            heart_rates = []
            
            for bucket in data.get("bucket", []):
                for dataset in bucket.get("dataset", []):
                    for point in dataset.get("point", []):
                        for value in point.get("value", []):
                            heart_rates.append(value.get("fpVal", 0))
            
            if heart_rates:
                return sum(heart_rates) / len(heart_rates)
            
            return None
        except Exception:
            return None
    
    def get_sleep(self, start_time: datetime, end_time: datetime) -> Optional[float]:
        try:
            start_millis = int(start_time.timestamp() * 1000)
            end_millis = int(end_time.timestamp() * 1000)
            
            body = {
                "aggregateBy": [{
                    "dataTypeName": "com.google.sleep.segment"
                }],
                "bucketByTime": {"durationMillis": 86400000},
                "startTimeMillis": start_millis,
                "endTimeMillis": end_millis
            }
            
            response = requests.post(
                f"{self.BASE_URL}/users/me/dataset:aggregate",
                headers=self.get_headers(),
                json=body
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            total_sleep_minutes = 0
            
            for bucket in data.get("bucket", []):
                for dataset in bucket.get("dataset", []):
                    for point in dataset.get("point", []):
                        for value in point.get("value", []):
                            sleep_segment = value.get("mapVal", [])
                            for segment in sleep_segment:
                                if segment.get("key") == "sleep_binary_version":
                                    continue
                                if segment.get("intVal") == 2:
                                    duration = point.get("endTimeNanos", 0) - point.get("startTimeNanos", 0)
                                    total_sleep_minutes += duration / 60000000000
            
            if total_sleep_minutes > 0:
                return total_sleep_minutes / 60
            
            return None
        except Exception:
            return None
    
    def get_calories(self, start_time: datetime, end_time: datetime) -> Optional[float]:
        try:
            start_millis = int(start_time.timestamp() * 1000)
            end_millis = int(end_time.timestamp() * 1000)
            
            body = {
                "aggregateBy": [{
                    "dataTypeName": "com.google.calories.expended",
                    "dataSourceId": "derived:com.google.calories.expended:com.google.android.gms:calories_burned"
                }],
                "bucketByTime": {"durationMillis": 86400000},
                "startTimeMillis": start_millis,
                "endTimeMillis": end_millis
            }
            
            response = requests.post(
                f"{self.BASE_URL}/users/me/dataset:aggregate",
                headers=self.get_headers(),
                json=body
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            total_calories = 0
            
            for bucket in data.get("bucket", []):
                for dataset in bucket.get("dataset", []):
                    for point in dataset.get("point", []):
                        for value in point.get("value", []):
                            total_calories += value.get("fpVal", 0)
            
            return total_calories if total_calories > 0 else None
        except Exception:
            return None
    
    def sync_health_data(self, date: datetime = None) -> Dict[str, Any]:
        if date is None:
            date = datetime.now()
        
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        steps = self.get_steps(start_of_day, end_of_day)
        heart_rate = self.get_heart_rate(start_of_day, end_of_day)
        sleep_hours = self.get_sleep(start_of_day - timedelta(days=1), end_of_day)
        calories = self.get_calories(start_of_day, end_of_day)
        
        return {
            "date": date.isoformat(),
            "steps": steps,
            "heart_rate": round(heart_rate, 1) if heart_rate else None,
            "sleep_hours": round(sleep_hours, 1) if sleep_hours else None,
            "calories": round(calories, 1) if calories else None,
            "data_source": "google_fit"
        }
    
    @staticmethod
    def get_authorization_url(state: str, redirect_uri: str) -> str:
        scopes_str = "%20".join(GOOGLE_SCOPES)
        return (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={GOOGLE_CLIENT_ID}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope={scopes_str}&"
            f"state={state}&"
            f"access_type=offline&"
            f"prompt=consent"
        )
    
    @staticmethod
    def exchange_code_for_tokens(code: str, redirect_uri: str) -> Optional[Dict[str, str]]:
        try:
            response = requests.post(GoogleFitService.TOKEN_URL, data={
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri
            })
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "access_token": data.get("access_token"),
                    "refresh_token": data.get("refresh_token"),
                    "expires_in": data.get("expires_in")
                }
        except Exception:
            pass
        
        return None
