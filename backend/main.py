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
from dotenv import load_dotenv
import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from parser import extract_locations  # 장소 추출 함수

load_dotenv()  # .env 파일에서 환경변수 로드

# Google OAuth 설정 (환경 변수 또는 기본값)
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8001/auth/callback")

# 임시 메모리 토큰 저장소
user_tokens = {}


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

# Pydantic 모델 정의
class ScheduleItem(BaseModel):
    time: dict = None
    location: Optional[str] = None
    event: Optional[str] = None

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

    # 1. '일정별'로 문장 분리 (예: 쉼표로 쪼개기 등, 상황 맞게 보완)
    parts = [s.strip() for s in req.text.split(",") if s.strip()]

    schedules = []
    for part in parts:
        # 2. 각 일정 문장별 추출
        # (Duckling으로 시간 추출)
        duckling_url = "http://localhost:8000/parse"
        data = {
            "text": part,
            "locale": "ko_KR",
            "dims": '["time"]',
            "tz": "Asia/Seoul",
        }
        try:
            response = requests.post(duckling_url, data=data)
            response.raise_for_status()
            times = response.json()
            time = times[0] if times else None
        except Exception as e:
            time = None

        # (장소 추출)
        try:
            locations = extract_locations(part)
            location = locations[0] if locations else None
            print(f"[DEBUG] 입력 문장: '{part}' -> 추출된 장소 리스트: {locations}")
        except Exception as e:
            location = None
            print(f"[ERROR] 장소 추출 실패: {e}")

        # (이벤트 추출)
        event = next((kw for kw in event_keywords if kw in part), None)

        schedules.append({
            "time": time,
            "location": location,
            "event": event
        })

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
# 9) 일정 중복 체크 함수
# ----------------------------------------
@app.post("/check-duplicates/")
def check_duplicates(items: List[ScheduleItem], user_key: str = "default"):
    """
    받은 일정들 중 Google Calendar 내 중복 일정 있는지 확인 후 결과를 반환하는 API 함수입니다.

    - items: 클라이언트로부터 받은 일정 리스트
    - user_key: 인증된 유저 토큰 키 (기본값 "default")
    """
    try:
        # 저장된 OAuth 토큰을 활용해 인증된 Google Calendar API 서비스 객체 생성
        service = get_authenticated_service(user_key)
    except HTTPException as e:
        # 인증 실패 시 401 에러 반환
        raise e

    import datetime
    from zoneinfo import ZoneInfo

    duplicates = []  # 중복 일정 정보 저장 리스트

    # 전달받은 각 일정 아이템에 대해 중복 검사 수행
    for schedule in items:
        # 일정의 시간 정보가 있을 때만 처리
        if schedule.time and schedule.time.get("value"):
            time_obj = schedule.time
            iso_value = None

            # 시간 정보의 구조가 dict일 수 있어 중첩 검사
            if isinstance(time_obj, dict):
                value_obj = time_obj.get("value")
                if isinstance(value_obj, dict):
                    # 다시 dict인 경우 내부 'value' 키에서 실제 ISO 시간 문자열 추출
                    iso_value = value_obj.get("value")
                elif isinstance(value_obj, str):
                    iso_value = value_obj

            # 시간 정보가 없으면 해당 일정 스킵
            if not iso_value:
                continue

            # ISO 8601 문자열을 datetime 객체로 변환
            dt = datetime.datetime.fromisoformat(iso_value)
            # 시간대 정보가 없으면 서울 시간대로 설정, 있으면 서울 시간대로 변환
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=ZoneInfo("Asia/Seoul"))
            else:
                dt = dt.astimezone(ZoneInfo("Asia/Seoul"))

            start_dt = dt
            # 기본적으로 일정은 1시간 단위로 설정하여 종료 시간 계산
            end_dt = start_dt + datetime.timedelta(hours=1)

            # Google Calendar API를 이용해 해당 시간 범위 내 기존 이벤트 검색
            existing_events_result = service.events().list(
                calendarId="primary",
                timeMin=start_dt.isoformat(),
                timeMax=end_dt.isoformat(),
                singleEvents=True,
                orderBy="startTime"
            ).execute()
            # 이벤트 리스트 추출 (없으면 빈 리스트)
            existing_events = existing_events_result.get("items", [])

            # 기존 이벤트들 중 시간 범위만 겹치면 중복으로 판단
            for ev in existing_events:
                duplicate_event_id = ev.get("id")
                duplicates.append({
                    "schedule": {
                        "summary": schedule.event or "일정",
                        "location": schedule.location or "",
                        "start": start_dt.isoformat(),
                        "end": end_dt.isoformat(),
                    },
                    "existing_event": ev
                })
                # 한 개라도 중복 찾으면 다음 일정으로 넘어감
                break

    # 중복 여부와 중복 이벤트 상세 목록을 함께 반환
    return {
        "has_duplicates": len(duplicates) > 0,
        "duplicates": duplicates
    }




# ----------------------------------------
# 10) API: 구글 캘린더에 일정 등록
# ----------------------------------------
@app.post("/register-google-calendar/")
def register_google_calendar(items: List[ScheduleItem], user_key: str = "default"):
    """
    POST 요청으로 받은 일정 목록을 Google Calendar에 등록합니다.
    - OAuth 토큰 저장소에서 인증 토큰을 불러와 API 호출
    - 일정 중복 여부를 시작 시간 기준으로 확인 후
      중복일 경우 업데이트, 없으면 새로 등록합니다.
    """
    print("[DEBUG] 받은 items:", items)
    created_ids = []

    # 인증된 Google Calendar API 서비스 객체 얻기
    try:
        service = get_authenticated_service(user_key)
    except HTTPException as e:
        # 인증 실패 시 예외 발생
        raise e

    import datetime
    from zoneinfo import ZoneInfo

    for schedule in items:
        # 각 일정에 시간 정보가 있는지 확인
        if schedule.time and schedule.time.get("value"):
            try:
                time_obj = schedule.time
                iso_value = None

                # 시간 정보 추출 (중첩 dict 또는 문자열 형태 고려)
                if isinstance(time_obj, dict):
                    value_obj = time_obj.get("value")
                    if isinstance(value_obj, dict):
                        iso_value = value_obj.get("value")
                    elif isinstance(value_obj, str):
                        iso_value = value_obj

                # 시간이 없으면 해당 일정 스킵
                if not iso_value:
                    print("시간 정보 없음")
                    continue

                # ISO 형식 문자열을 datetime 객체로 변환 및 시간대 설정
                dt = datetime.datetime.fromisoformat(iso_value)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=ZoneInfo("Asia/Seoul"))
                else:
                    dt = dt.astimezone(ZoneInfo("Asia/Seoul"))

                start_dt = dt
                end_dt = start_dt + datetime.timedelta(hours=1)  # 기본 1시간 일정

                # 해당 시간 범위 내 기존 이벤트 검색 (중복 확인용)
                existing_events_result = service.events().list(
                    calendarId="primary",
                    timeMin=start_dt.isoformat(),
                    timeMax=end_dt.isoformat(),
                    singleEvents=True,
                    orderBy="startTime"
                ).execute()
                existing_events = existing_events_result.get("items", [])

                duplicate_event_id = None

                # 시간 범위 내 이벤트가 있으면 중복으로 판단 (제목/위치 비교 없이)
                for ev in existing_events:
                    duplicate_event_id = ev["id"]
                    break

                # 구글 캘린더에 보낼 이벤트 데이터 구성
                event_body = {
                    "summary": schedule.event or "일정",
                    "location": schedule.location or "",
                    "start": {"dateTime": start_dt.isoformat(), "timeZone": "Asia/Seoul"},
                    "end": {"dateTime": end_dt.isoformat(), "timeZone": "Asia/Seoul"},
                }

                if duplicate_event_id:
                    # 중복 일정이 있으면 업데이트(덮어쓰기)
                    event = service.events().update(
                        calendarId="primary",
                        eventId=duplicate_event_id,
                        body=event_body
                    ).execute()
                    print("Event updated:", event.get("htmlLink"))
                else:
                    # 중복 없으면 새로 등록
                    event = service.events().insert(
                        calendarId="primary",
                        body=event_body
                    ).execute()
                    print("Event created:", event.get("htmlLink"))

                # 생성 또는 업데이트된 이벤트 ID 저장
                created_ids.append(event.get("id"))

            except Exception as e:
                print("이벤트 등록 실패:", e)
                import traceback
                traceback.print_exc()

    # 등록(또는 업데이트)된 이벤트 ID 목록 반환
    return {"created_event_ids": created_ids}
