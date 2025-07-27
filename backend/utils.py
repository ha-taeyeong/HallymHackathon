import datetime
from zoneinfo import ZoneInfo  # Python 3.9 이상
from google.oauth2 import service_account
from googleapiclient.discovery import build
import traceback

SERVICE_ACCOUNT_FILE = 'service_account.json'  # 경로 확인 필수
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
CALENDAR_ID = 'electro0218@gmail.com'  # 본인 캘린더 ID

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build('calendar', 'v3', credentials=credentials)

def create_event(schedule):
    try:
        time_obj = schedule.get("time")
        iso_value = None

        if isinstance(time_obj, dict):
            value_obj = time_obj.get("value")
            if isinstance(value_obj, dict):
                iso_value = value_obj.get("value")
            elif isinstance(value_obj, str):
                iso_value = value_obj

        if not iso_value:
            print("시간 정보 없음")
            return None

        dt = datetime.datetime.fromisoformat(iso_value)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo("Asia/Seoul"))
        else:
            dt = dt.astimezone(ZoneInfo("Asia/Seoul"))

        start_dt = dt
        end_dt = start_dt + datetime.timedelta(hours=1)  # 필요시 가변

        event_body = {
            'summary': schedule.get("event") or "일정",
            'location': schedule.get("location") or "",
            'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Asia/Seoul'},
            'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'Asia/Seoul'}
        }

        print(f"[DEBUG] iso_value: {iso_value}")
        print(f"[DEBUG] start_dt: {start_dt.isoformat()}")
        print(f"[DEBUG] end_dt: {end_dt.isoformat()}")
        print(f"[DEBUG] event_body: {event_body}")

        event = service.events().insert(calendarId=CALENDAR_ID, body=event_body).execute()

        print("Event created:", event.get("htmlLink"))
        return event.get("id")

    except Exception as e:
        print(f"이벤트 생성 실패: {e}")
        traceback.print_exc()
        return None