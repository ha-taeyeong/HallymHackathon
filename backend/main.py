from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests
import json
from typing import List, Optional
import traceback
import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from parser import extract_locations  # 장소 추출 함수


app = FastAPI()


# 정적파일(HTML/JS 등) 서빙: /static/** 경로로 접근 시 static 폴더 내 파일 제공
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 템플릿 디렉토리 설정
templates = Jinja2Templates(directory="templates")


# CORS 미들웨어 설정 (테스트용, 운영시 도메인 한정 권장)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextRequest(BaseModel):
    text: str


def load_event_keywords(filepath="event_keywords.json") -> List[str]:
    """
    event_keywords.json 로부터 이벤트 키워드 로딩.
    실패 시 기본 리스트 반환.
    """
    DEFAULT_EVENT_KEYWORDS = ["회의", "발표", "미팅", "점심", "저녁", "점검", "워크숍"]
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            keywords = json.load(f)
            return keywords if isinstance(keywords, list) else DEFAULT_EVENT_KEYWORDS
    except Exception as e:
        print(f"Failed to load event keywords: {e}")
        return DEFAULT_EVENT_KEYWORDS


event_keywords = load_event_keywords()


# ----------------------------------------
# 1) 홈 페이지 - 메인 화면
# ----------------------------------------
@app.get("/")
def home():
    """
    '/' 경로: 홈 페이지를 static/home.html 파일에서 읽어 보여줌.
    """
    try:
        with open("static/home.html", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except Exception as e:
        # 파일 없거나 읽기 실패 시 에러 메시지 반환
        return HTMLResponse(f"<h2>홈 페이지 로딩 실패: {e}</h2>")


# ----------------------------------------
# 2) 로그인 페이지 - 구글 OAuth 인증 시작 화면
# ----------------------------------------
@app.get("/login")
def login(request: Request):
    return templates.TemplateResponse("oauth.html", {
        "request": request,
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
    })


# ----------------------------------------
# 3) OAuth 콜백 - 구글 로그인 후 토큰 교환 및 리다이렉션
# ----------------------------------------
@app.get("/auth/callback")
async def auth_callback(request: Request):
    """
    구글 OAuth 인증 완료 후 redirect URI로 리다이렉션 되는 곳.
    - 쿼리스트링으로 받은 code로 토큰 교환 요청
    - token을 user_tokens에 저장
    - 인증 성공 시 /schedule 경로로 리다이렉트
    """
    code = request.query_params.get("code")
    if not code:
        return HTMLResponse("<h2>Authorization code not found</h2><a href='/'>홈으로</a>")

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    try:
        resp = requests.post(token_url, data=data)
        resp.raise_for_status()
        tokens = resp.json()
        # 토큰 임시 저장 (실제 서비스에서는 사용자별 DB 저장 필요)
        user_tokens["default"] = tokens
        # 인증 성공 후 일정 등록 페이지로 리다이렉트
        return RedirectResponse(url="/schedule")
    except requests.HTTPError as e:
        return HTMLResponse(
            f"<h2>토큰 획득 실패</h2>{e.response.text}<br><a href='/'>홈으로</a>"
        )


# ----------------------------------------
# 4) 일정 등록 화면 (정적 HTML)
# ----------------------------------------
@app.get("/schedule")
def schedule():
    """
    '/schedule' 경로: static/schedule.html 반환.
    일정 입력/추출/저장 UI 포함.
    """
    try:
        with open("static/schedule.html", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except Exception as e:
        return HTMLResponse(f"<h2>일정 등록 페이지 로딩 실패: {e}</h2>")


# ----------------------------------------
# 5) API: 날짜-시간 파싱 (Duckling 사용)
# ----------------------------------------
@app.post("/parse-datetime/")
def parse_datetime(req: TextRequest):
    duckling_url = "http://localhost:8000/parse"
    data = {
        "text": req.text,
        "locale": "ko_KR",
        "dims": '["time"]',
        "tz": "Asia/Seoul",
    }
    try:
        response = requests.post(duckling_url, data=data)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Duckling API 호출 실패: {e}")
    return response.json()


# ----------------------------------------
# 6) API: 장소 추출 (spaCy 사용)
# ----------------------------------------
@app.post("/extract-location/")
def extract_location(req: TextRequest):
    locations = extract_locations(req.text)
    return {"locations": locations}


# ----------------------------------------
# 7) API: 복수 일정 파싱 (시간+장소+이벤트)
# ----------------------------------------
@app.post("/parse-multi-schedule/")
def parse_multi_schedule(req: TextRequest):
    if not req.text or not isinstance(req.text, str):
        raise HTTPException(
            status_code=400, detail="text 필드는 반드시 비어있지 않은 문자열이어야 합니다."
        )

    data = {
        "text": req.text,
        "locale": "ko_KR",
        "dims": '["time"]',
        "tz": "Asia/Seoul",
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
            location = (
                locations[i] if i < len(locations) else (locations[0] if locations else None)
            )
            event = events[i] if i < len(events) else (events[0] if events else None)
            schedules.append({"time": time, "location": location, "event": event})
        return schedules

    schedules = smart_match_schedules(times, locations, events)
    return {"schedules": schedules}


# ----------------------------------------
# 8) Google Calendar API 호출 준비 함수
# ----------------------------------------
def get_authenticated_service(user_key: str = "default"):
    """
    저장된 OAuth 토큰 기반으로 인증된 Google Calendar API 서비스 객체 생성 반환
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
        raise HTTPException(status_code=500, detail="Google Calendar 서비스 생성 실패")


# ----------------------------------------
# 9) API: 구글 캘린더에 일정 등록
# ----------------------------------------
@app.post("/register-google-calendar/")
def register_google_calendar(items: List[ScheduleItem], user_key: str = "default"):
    """
    - POST 일정 목록으로 Google Calendar 이벤트 등록
    - OAuth 토큰 저장소에서 인증 체크 후 API 호출
    """
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
                    print("시간 정보 없음")
                    continue

                import datetime
                from zoneinfo import ZoneInfo

                dt = datetime.datetime.fromisoformat(iso_value)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=ZoneInfo("Asia/Seoul"))
                else:
                    dt = dt.astimezone(ZoneInfo("Asia/Seoul"))

                start_dt = dt
                end_dt = start_dt + datetime.timedelta(hours=1)

                event_body = {
                    "summary": schedule.event or "일정",
                    "location": schedule.location or "",
                    "start": {"dateTime": start_dt.isoformat(), "timeZone": "Asia/Seoul"},
                    "end": {"dateTime": end_dt.isoformat(), "timeZone": "Asia/Seoul"},
                }

                # Google Calendar API 호출 (기본 캘린더에 이벤트 등록)
                event = service.events().insert(calendarId="primary", body=event_body).execute()
                print("Event created:", event.get("htmlLink"))
                created_ids.append(event.get("id"))
            except Exception as e:
                print("이벤트 등록 실패:", e)
                traceback.print_exc()

    return {"created_event_ids": created_ids}
