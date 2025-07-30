# main.py
import os
import stanza
import requests
import traceback
import datetime
import re
from zoneinfo import ZoneInfo
import dateparser

from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from googleapiclient.discovery import build
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from google.oauth2.credentials import Credentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse


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
    
@app.get("/login")
def login():
    # Google OAuth 인증 URL 생성
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": CLIENT_REDIRECT_URI,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/calendar",
        "access_type": "offline",
        "prompt": "consent"
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth"
    req_url = requests.Request('GET', url, params=params).prepare().url
    return RedirectResponse(req_url)


@app.get("/auth/callback")
def auth_callback(code: str):
    # 받은 Authorization code로 Access Token 요청
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": CLIENT_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    response = requests.post(token_url, data=data)
    token_data = response.json()
    if "access_token" in token_data:
        # user_key = 'default' 로 저장
        user_tokens['default'] = token_data
        # 인증 성공 후 /schedule 페이지로 리다이렉트
        return RedirectResponse(url="/schedule")
    else:
        raise HTTPException(status_code=400, detail="토큰 요청 실패")


@app.get("/schedule")
def schedule():
    """일정 등록 페이지 반환"""
    try:
        with open("static/schedule.html", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except Exception as e:
        return HTMLResponse(f"<h2>일정 페이지 로딩 실패: {e}</h2>")


# 이벤트 키워드를 JSON 파일에서 불러와 전역 변수로 저장
def load_event_keywords(filepath="event_keywords.json"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            keywords = json.load(f)
            if isinstance(keywords, list):
                return keywords
    except Exception:
        pass
    return []

event_keywords = load_event_keywords()


@app.post("/parse-multi-schedule/")
def parse_multi_schedule(req: TextRequest):
    """
    클라이언트가 입력한 여러 일정 문장(콤마 구분)을 
    시간, 장소, 이벤트로 분리하여 반환하는 API.
    """
    print("== [입력 데이터] parse-multi-schedule ==\n", req.text)
    if not req.text or not isinstance(req.text, str):
        raise HTTPException(status_code=400, detail="텍스트 입력 필드가 필요합니다.")

    parts = [s.strip() for s in req.text.split(",") if s.strip()]
    schedules = []

    for part in parts:
        # 1. 기본 규칙으로 시간, 장소, 이벤트 분리print("---- [개별 일정 원본] ----", part)
        time_part, location_part, event_part = split_schedule_parts(part)
        print(f"시간: {time_part}, 장소: {location_part}, 이벤트: {event_part}")

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
    print("[DEBUG] check_duplicates items:", items)
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

    for i, schedule in enumerate(items):
        print(f"[{i}] 저장 대상 스케줄:", schedule)
        if schedule.time and schedule.time.get("value"):
            time_obj = schedule.time
            dt = safe_parse_datetime(time_obj)
            if not dt:
                continue  # 잘못된 시간 입력은 건너뜀

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
                break  # 한 건만 확인하고 break
    return {
        "has_duplicates": len(duplicates) > 0,
        "duplicates": duplicates
    }

@app.post("/register-google-calendar/")
def register_google_calendar(items: List[ScheduleItem], user_key: str = "default"):
    import datetime
    from zoneinfo import ZoneInfo
    import traceback

    print("== [저장 요청] 받은 items ==", items)

    created_ids = []
    failed_items = []

    try:
        service = get_authenticated_service(user_key)
    except HTTPException as e:
        raise e

    for i, schedule in enumerate(items):
        print(f"[{i}] 저장 대상 스케줄:", schedule)
        try:
            dt = safe_parse_datetime(schedule.time)
            print(f"  변환된 dt: {dt}")
            if not dt:
                print(f"[{i}] 실패: 시간 파싱 안됨, 일정 건너뜀")
                continue

            start_dt = dt
            end_dt = start_dt + datetime.timedelta(hours=1)

            # 중복 검사 및 event 생성/수정
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
            print(f"[{i}] 일정 저장 완료: {event.get('id')}")
        except Exception as e:
            failed_items.append({"schedule": schedule, "error": str(e)})
            continue

    return {"created_event_ids": created_ids, "failed_items": failed_items}



def safe_parse_datetime(time_obj):

    now = datetime.datetime.now()
    
    # 1. 시간 문자열 추출------------------------------
    iso_value = None
    if isinstance(time_obj, dict):
        val = time_obj.get("value")
        if isinstance(val, dict):
            iso_value = val.get("value")
        elif isinstance(val, str):
            iso_value = val
    elif isinstance(time_obj, str):
        iso_value = time_obj

    if not iso_value:  # 시간 문자열 없으면 None 반환
        return None

    # 2. 전처리 함수 정의 (필요시 함수 밖에 미리 정의해도 무방)
    def replace_relative_dates(text):
        weekdays = {
            "월요일": 0, "화요일": 1, "수요일": 2,
            "목요일": 3, "금요일": 4, "토요일": 5, "일요일": 6,
        }
        text = re.sub(r'오늘', now.strftime("%Y년 %m월 %d일"), text)
        text = re.sub(r'내일', (now + datetime.timedelta(days=1)).strftime("%Y년 %m월 %d일"), text)
        text = re.sub(r'모레', (now + datetime.timedelta(days=2)).strftime("%Y년 %m월 %d일"), text)

        match = re.search(r'다음주\s*(월요일|화요일|수요일|목요일|금요일|토요일|일요일)', text)
        if match:
            target_wd = weekdays[match.group(1)]
            today_wd = now.weekday()
            days_until_target = (target_wd - today_wd) % 7 + 7
            target_date = now + datetime.timedelta(days=days_until_target)
            target_str = target_date.strftime("%Y년 %m월 %d일")
            text = re.sub(r'다음주\s*(월요일|화요일|수요일|목요일|금요일|토요일|일요일)', target_str, text)
        return text

    def ensure_year_prefix(time_str):
        if re.search(r'\b\d{4}년\b', time_str) or re.search(r'\b\d{4}[-/]', time_str):
            return time_str.strip()
        else:
            return f"{now.year}년 {time_str.strip()}"

    def convert_am_pm(time_str):
        def conv(m):
            ampm, hour = m.group(1), int(m.group(2))
            if ampm == "오후" and hour < 12:
                hour += 12
            elif ampm == "오전" and hour == 12:
                hour = 0
            return f"{hour:02d}:00"
        return re.sub(r'(오전|오후)\s*(\d{1,2})시', conv, time_str)

    def clean_date_format(time_str):
        # 1) 여러 공백 → 1개의 공백, 앞뒤 공백 제거
        time_str = re.sub(r'\s+', ' ', time_str).strip()

        # 2) '년', '월' 문자는 하이픈으로 교체
        time_str = re.sub(r'(\d{4})년', r'\1-', time_str)
        time_str = re.sub(r'(\d{1,2})월', r'\1-', time_str)

        # 3) ‘일’ 문자와 주변 공백 제거 (예: '29일' → '29 ' or '29'로 분리)
        time_str = re.sub(r'\s*(\d{1,2})일\s*', r'\1 ', time_str)

        # 4) 중복 하이픈 '--' → '-' 하나로 치환
        time_str = re.sub(r'-{2,}', '-', time_str)

        # 5) 양쪽 끝 불필요한 하이픈 및 공백 제거
        time_str = time_str.strip('- ')

        return time_str


    # 3. 전처리 함수 순서대로 실행
    iso_value = replace_relative_dates(iso_value)
    iso_value = ensure_year_prefix(iso_value)
    iso_value = convert_am_pm(iso_value)
    iso_value = clean_date_format(iso_value)

    # 4. 파싱 시도
    parsed = dateparser.parse(
        iso_value,
        languages=['ko'],
        settings={'RELATIVE_BASE': now, 'PREFER_DATES_FROM': 'future'}
    )

    if not parsed:
        print("[WARN] dateparser 파싱 실패 even after preprocess:", iso_value)
        return None

    dt = parsed
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("Asia/Seoul"))
    else:
        dt = dt.astimezone(ZoneInfo("Asia/Seoul"))
    return dt


# 그리고 이 함수로 기존 코드에서 시간 변환 부분을 대체

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