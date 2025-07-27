from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
from typing import List
from utils import create_event
from parser import extract_locations
import traceback  # 오류 로그용

class ScheduleItem(BaseModel):
    time: dict = None
    location: str = None
    event: str = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextRequest(BaseModel):
    text: str

def load_event_keywords(filepath="event_keywords.json"):
    DEFAULT_EVENT_KEYWORDS = ["회의", "발표", "미팅", "점심", "저녁", "점검", "워크숍"]
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            keywords = json.load(f)
            return keywords if isinstance(keywords, list) else DEFAULT_EVENT_KEYWORDS
    except Exception as e:
        print(f"Failed to load event keywords: {e}")
        return DEFAULT_EVENT_KEYWORDS

event_keywords = load_event_keywords()

@app.post("/parse-datetime/")
def parse_datetime(req: TextRequest):
    duckling_url = "http://localhost:8000/parse"
    data = {
        "text": req.text,
        "locale": "ko_KR",
        "dims": '["time"]',
        "tz": "Asia/Seoul"
    }
    try:
        response = requests.post(duckling_url, data=data)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Duckling API 호출 실패: {e}")
    return response.json()

@app.post("/extract-location/")
def extract_location(req: TextRequest):
    locations = extract_locations(req.text)
    return {"locations": locations}

@app.post("/parse-multi-schedule/")
def parse_multi_schedule(req: TextRequest):
    if not req.text or not isinstance(req.text, str):
        raise HTTPException(status_code=400, detail="text 필드는 반드시 비어있지 않은 문자열이어야 합니다.")

    data = {
        "text": req.text,
        "locale": "ko_KR",
        "dims": '["time"]',
        "tz": "Asia/Seoul"  # ← 반드시 추가
    }
    print("[DEBUG] 보내는 데이터:", data)

    duckling_url = "http://localhost:8000/parse"
    try:
        response = requests.post(duckling_url, data=data)
        response.raise_for_status()
        times = response.json()
        print("[DEBUG] Duckling 파싱 결과 times:", times)
    except requests.RequestException as e:
        print("Duckling 통신 오류:", e)
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"Duckling API 호출 실패: {e}")

    try:
        locations = extract_locations(req.text)
    except Exception as e:
        print("장소 추출 실패:", e)
        traceback.print_exc()
        locations = []

    events = [kw for kw in event_keywords if kw in req.text]

    def smart_match_schedules(times, locations, events):
        schedules = []
        for i, time in enumerate(times):
            location = locations[i] if i < len(locations) else (locations[0] if locations else None)
            event = events[i] if i < len(events) else (events[0] if events else None)
            schedules.append({
                "time": time,
                "location": location,
                "event": event
            })
        return schedules

    schedules = smart_match_schedules(times, locations, events)
    return {"schedules": schedules}


@app.post("/register-google-calendar/")
def register_google_calendar(items: List[ScheduleItem]):
    print("[DEBUG] 받은 items:", items)
    created_ids = []
    for schedule in items:
        if schedule.time and schedule.time.get("value"):
            try:
                event_id = create_event(schedule.dict())
                if event_id:
                    created_ids.append(event_id)
            except Exception as e:
                print("이벤트 등록 실패:", e)
                traceback.print_exc()
    return {"created_event_ids": created_ids}