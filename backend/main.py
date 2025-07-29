from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
import traceback
import os
from dotenv import load_dotenv
import stanza
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 사용자 정의 모듈 (장소 추출 등)
from parser import extract_locations, location_keywords_extended

# --------------------
# NLP 모델 및 환경설정
# --------------------
stanza.download("ko", verbose=False)  # 한 번만 다운로드
nlp = stanza.Pipeline(lang="ko", processors="tokenize,pos,lemma")

# .env 환경 변수 로드 (Google OAuth 관련)
load_dotenv()
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
CLIENT_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8001/auth/callback")

# 사용자 토큰 저장 (간단한 예시, 실제 서비스시 DB 활용 권장)
user_tokens = {}

# FastAPI 앱 생성 및 초기 설정
app = FastAPI()

# 정적 파일 및 템플릿 경로 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 개발용 CORS 설정 (실제 배포시 적절히 수정 권장)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------
# Pydantic 데이터 모델
# --------------------
class ScheduleItem(BaseModel):
    time: dict = None  # 시간 정보 (Duckling 또는 형태소 결과 포함)
    location: Optional[str]  # 장소명
    event: Optional[str]  # 이벤트명

class TextRequest(BaseModel):
    text: str  # 사용자 입력 텍스트

# --------------------
# 일정 파싱 보조 함수
# --------------------
def split_schedule_parts(text: str):
    """
    문장 내 '시'까지는 시간, '시'부터 '에서'까지는 장소, '에서' 이후는 이벤트로 분리.
    '시'가 없으면 시간/장소는 None, 전체를 이벤트로 처리.
    """
    si_pos = text.find('시')
    if si_pos == -1:
        return None, None, text.strip()
    
    eseo_pos = text.find('에서', si_pos)
    time_part = text[:si_pos + 1].strip()
    
    if eseo_pos == -1:
        place_part = text[si_pos + 1:].strip()
        event_part = ""
    else:
        place_part = text[si_pos + 1:eseo_pos].strip()
        event_part = text[eseo_pos + 2:].strip()

    return time_part, place_part, event_part

def pick_valid_location(locations: List[str]) -> str:
    """
    숫자만 있거나 너무 짧은 후보는 제외하고 첫 번째 유효 후보 반환.
    후보가 없으면 '위치 없음' 반환.
    """
    candidates = [loc for loc in locations if not loc.isdigit() and len(loc) > 1]
    return candidates[0] if candidates else "위치 없음"

# --------------------
# FastAPI 엔드포인트
# --------------------
@app.get("/")
def home():
    """홈 페이지 반환"""
    try:
        with open("static/home.html", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except Exception as e:
        return HTMLResponse(f"<h2>홈 페이지 로딩 실패: {e}</h2>")

@app.get("/schedule")
def schedule():
    """일정 등록 페이지 반환"""
    try:
        with open("static/schedule.html", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except Exception as e:
        return HTMLResponse(f"<h2>일정 페이지 로딩 실패: {e}</h2>")

@app.post("/parse-multi-schedule/")
def parse_multi_schedule(req: TextRequest):
    """
    클라이언트가 입력한 여러 일정 문장(콤마 구분)을 
    시간, 장소, 이벤트로 분리하여 반환하는 API.
    """
    if not req.text or not isinstance(req.text, str):
        raise HTTPException(status_code=400, detail="텍스트 입력 필드가 필요합니다.")

    parts = [s.strip() for s in req.text.split(",") if s.strip()]
    schedules = []

    for part in parts:
        # 1. 기본 규칙으로 시간, 장소, 이벤트 분리
        time_part, location_part, event_part = split_schedule_parts(part)

        # 2. 시간 필드 생성
        time = {"value": time_part} if time_part else None

        # 3. 장소 후보 수집 및 선택
        location_candidates = []
        if location_part:
            location_candidates.append(location_part)
        try:
            locs = extract_locations(part)  # parser 모듈 활용, JSON 키워드 기반
            for loc in locs:
                if loc not in location_candidates:
                    location_candidates.append(loc)
        except Exception:
            pass
        location = pick_valid_location(location_candidates)

        # 4. 이벤트 지정 (우선 event_part, 없으면 명사 및 키워드 등 활용)
        event = event_part if event_part else None
        if not event:
            doc = nlp(part)
            nouns = [word.text for sent in doc.sentences for word in sent.words if word.upos == "NOUN"]
            event = next((kw for kw in event_keywords if kw in part), None)
            if not event:
                event = nouns[-1] if nouns else "일정"

        schedules.append({
            "time": time,
            "location": location,
            "event": event,
        })

    return {"schedules": schedules}

# --------------------
# Google Calendar API 인증 및 처리 함수
# --------------------
def get_authenticated_service(user_key: str = "default"):
    """
    저장된 사용자 OAuth 토큰으로 인증 후 Google Calendar API 서비스 객체 반환.
    토큰이 없으면 401 반환, 서비스 생성 실패 시 500 반환.
    """
    tokens = user_tokens.get(user_key)
    if not tokens:
        raise HTTPException(status_code=401, detail="인증된 토큰이 없습니다. 로그인 필요.")

    creds = Credentials(
        token=tokens.get("access_token"),
        refresh_token=tokens.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )
    try:
        service = build("calendar", "v3", credentials=creds)
        return service
    except Exception as e:
        print("Google Calendar 서비스 빌드 실패:", e)
        raise HTTPException(status_code=500, detail="Google 서비스 생성 실패")

@app.post("/check_duplicates/")
def check_duplicates(items: List[ScheduleItem], user_key: str = "default"):
    """
    전달받은 일정 리스트에 대해 Google Calendar 내 겹치는 일정이 있는지 확인.
    """
    import datetime
    from zoneinfo import ZoneInfo

    try:
        service = get_authenticated_service(user_key)
    except HTTPException as e:
        raise e

    duplicates = []

    for schedule in items:
        if schedule.time and schedule.time.get("value"):
            time_obj = schedule.time
            iso_value = None

            if isinstance(time_obj, dict):
                value_obj = time_obj.get("value")
                if isinstance(value_obj, dict):
                    iso_value = value_obj.get("value")
                elif isinstance(value_obj, str):
                    iso_value = value_obj
            elif isinstance(time_obj, str):
                iso_value = time_obj

            if not iso_value:
                continue

            dt = datetime.datetime.fromisoformat(iso_value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=ZoneInfo("Asia/Seoul"))
            else:
                dt = dt.astimezone(ZoneInfo("Asia/Seoul"))

            start_dt = dt
            end_dt = start_dt + datetime.timedelta(hours=1)

            existing_events_result = service.events().list(
                calendarId="primary",
                timeMin=start_dt.isoformat(),
                timeMax=end_dt.isoformat(),
                singleEvents=True,
                orderBy="startTime"
            ).execute()

            existing_events = existing_events_result.get("items", [])
            for ev in existing_events:
                duplicates.append({
                    "schedule": {
                        "summary": schedule.event or "일정",
                        "location": schedule.location or "",
                        "start": start_dt.isoformat(),
                        "end": end_dt.isoformat(),
                    },
                    "existing_event": ev
                })
                break

    return {
        "has_duplicates": len(duplicates) > 0,
        "duplicates": duplicates
    }

@app.post("/register-google-calendar/")
def register_google_calendar(items: List[ScheduleItem], user_key: str = "default"):
    """
    일정 리스트를 받아 Google Calendar에 등록(중복 시 업데이트).
    """
    import datetime
    from zoneinfo import ZoneInfo

    print("[DEBUG] 받은 items:", items)

    created_ids = []

    try:
        service = get_authenticated_service(user_key)
    except HTTPException as e:
        raise e

    for schedule in items:
        if schedule.time and schedule.time.get("value"):
            try:
                time_obj = schedule.time
                iso_value = None

                if isinstance(time_obj, dict):
                    value_obj = time_obj.get("value")
                    if isinstance(value_obj, dict):
                        iso_value = value_obj.get("value")
                    elif isinstance(value_obj, str):
                        iso_value = value_obj

                if not iso_value:
                    continue

                dt = datetime.datetime.fromisoformat(iso_value)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=ZoneInfo("Asia/Seoul"))
                else:
                    dt = dt.astimezone(ZoneInfo("Asia/Seoul"))

                start_dt = dt
                end_dt = start_dt + datetime.timedelta(hours=1)

                existing_events_result = service.events().list(
                    calendarId="primary",
                    timeMin=start_dt.isoformat(),
                    timeMax=end_dt.isoformat(),
                    singleEvents=True,
                    orderBy="startTime"
                ).execute()

                existing_events = existing_events_result.get("items", [])
                duplicate_event_id = None
                for ev in existing_events:
                    duplicate_event_id = ev["id"]
                    break

                event_body = {
                    "summary": schedule.event or "일정",
                    "location": schedule.location or "",
                    "start": {"dateTime": start_dt.isoformat(), "timeZone": "Asia/Seoul"},
                    "end": {"dateTime": end_dt.isoformat(), "timeZone": "Asia/Seoul"},
                }

                if duplicate_event_id:
                    event = service.events().update(
                        calendarId="primary",
                        eventId=duplicate_event_id,
                        body=event_body
                    ).execute()
                else:
                    event = service.events().insert(
                        calendarId="primary",
                        body=event_body
                    ).execute()

                created_ids.append(event.get("id"))
            except Exception:
                traceback.print_exc()
    return {"created_event_ids": created_ids}

# --------------------
# 장소 후보 판단용 헬퍼
# --------------------
def is_place_like(s: str) -> bool:
    """
    텍스트에 장소형 명사 혹은 키워드 포함 여부 확인.
    """
    place_words = ['회의실', '카페', '도서관', '라운지', '세미나실', '출구', '동', '호', '층']
    return any(w in s for w in location_keywords_extended + place_words)

def pick_final_location(candidates: list[str]) -> str:
    """
    후보 장소들을 길이와 장소 키워드 포함 개수 기준으로 정렬 후 최적 후보 선택.
    숫자 또는 1글자인 후보는 우선 제외.
    """
    filtered = [
        c for c in candidates
        if len(c) > 1 and not c.isdigit() and is_place_like(c)
    ]
    if filtered:
        filtered.sort(key=lambda x: (len(x), sum([x.count(w) for w in location_keywords_extended])), reverse=True)
        return filtered[0]

    normal_filtered = [c for c in candidates if len(c) > 1 and not c.isdigit()]
    if normal_filtered:
        normal_filtered.sort(key=len, reverse=True)
        return normal_filtered[0]

    return "위치 정보 없음"
