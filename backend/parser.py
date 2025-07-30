# parser.py
import stanza
import re
import json
import os

# Stanza NLP 파이프라인 객체를 저장할 전역 변수
_nlp = None

def get_nlp():
    """Stanza 한국어 파이프라인을 초기화하고 반환.
    최초 호출 시에만 생성하며 이후에는 재사용."""
    global _nlp
    if _nlp is None:
        # 한국어용 토크나이징, 품사 태깅, 표제어 추출 프로세서 포함
        _nlp = stanza.Pipeline(lang="ko", processors="tokenize,pos,lemma")
    return _nlp

def load_location_keywords(filepath="locations.json"):
    """로컬 JSON 파일에서 위치 키워드 리스트를 불러옴.
    파일이 존재하고 리스트 형태이면 반환, 아니면 빈 리스트 반환."""
    if os.path.exists(filepath):
        with open(filepath, encoding="utf-8") as f:
            lst = json.load(f)
            if isinstance(lst, list):
                return lst
    return []

def load_location_keywords_extended(filepath="locations_extended.json"):
    """확장 위치 키워드 리스트를 JSON 파일에서 로드하는 함수.
    기본 위치 키워드 외 추가 키워드를 관리."""
    if os.path.exists(filepath):
        with open(filepath, encoding="utf-8") as f:
            lst = json.load(f)
            if isinstance(lst, list):
                return lst
    return []

# 기본 위치 키워드 리스트 로드
location_keywords = load_location_keywords()
# 기본 + 확장 위치 키워드를 합친 리스트 생성
location_keywords_extended = location_keywords + load_location_keywords_extended()


def extract_locations(text: str):
    """입력된 텍스트에서 위치 관련 키워드 및 확장 키워드를 기반으로 위치명 추출.

    - Stanza NLP 파이프라인을 통해 문장 분석(현재는 결과 미활용, 추후 확장 가능)
    - 정규식 패턴을 사용해 위치 키워드 및 층·호·번·출구 등 상세 위치 정보 포함된 문자열 추출
    - 중복과 숫자만 있는 값은 제외하여 위치 엔티티 목록 반환"""
    nlp = get_nlp()
    doc = nlp(text)  # 형태소 분석(현 코드에서 분석 결과는 직접 사용하지 않음)
    entities = []    # 추출된 위치명 저장 리스트

    # 정규식 패턴 구성:
    # 1) location_keywords_extended 내 단어 중 하나로 시작
    # 2) 그 뒤에 최대 7자리 숫자 및 층, 호, 번, 출구와 같은 위치 단어가 올 수 있음
    # 3) 마지막으로 한글 또는 영문 단어(세미나실, Café 등)가 올 수 있음
    pattern = re.compile(
        r'((?:' + '|'.join(map(re.escape, location_keywords_extended)) + r')'
        r'(?:[\s\d]{0,7}(?:층|호|번|출구)?)?'  # 예: 3층, 201호
        r'(?:\s*[가-힣A-Za-z]+)?'              # 예: 세미나실, Café
        r')'
    )

    # 텍스트에서 패턴과 일치하는 모든 부분 찾기
    for match in pattern.finditer(text):
        value = match.group(0).strip()
        # 숫자만 있거나 길이가 1 이하면 제외, 중복도 제외
        if not value.isdigit() and len(value) > 1 and value not in entities:
            entities.append(value)

    # 정규식으로 찾지 못했을 경우, 텍스트에 키워드가 포함되어 있는지만 단순 검색
    if not entities:
        for kw in location_keywords_extended:
            if kw in text and kw not in entities:
                entities.append(kw)

    return entities


def safe_parse_datetime(time_obj):
    import datetime
    import re
    from zoneinfo import ZoneInfo
    import dateparser

    now = datetime.datetime.now()

    def replace_relative_dates(text):
        # 상대일 치환 예시 (내일, 모레, 다음주 월요일 등)
        text = re.sub(r'내일', (now + datetime.timedelta(days=1)).strftime("%Y년 %m월 %d일"), text)
        text = re.sub(r'모레', (now + datetime.timedelta(days=2)).strftime("%Y년 %m월 %d일"), text)
        # 다음주 월요일은 좀 더 복잡하게 처리 (생략 가능)
        return text

    def ensure_year_prefix(time_str):
        if re.search(r'\b\d{4}년\b', time_str) or re.search(r'\b\d{4}[-/]', time_str):
            return time_str.strip()
        else:
            return f"{now.year}년 {time_str.strip()}"

    def clean_date_format(time_str):
        time_str = re.sub(r'\s+', ' ', time_str).strip()
        time_str = re.sub(r'(\d{4})년', r'\1-', time_str)
        time_str = re.sub(r'(\d{1,2})월', r'\1-', time_str)
        time_str = re.sub(r'(\d{1,2})일', '', time_str)
        time_str = re.sub(r'-{2,}', '-', time_str)
        time_str = time_str.strip('- ')
        return time_str

    iso_value = None
    if isinstance(time_obj, dict):
        v = time_obj.get("value")
        if isinstance(v, dict):
            iso_value = v.get("value")
        elif isinstance(v, str):
            iso_value = v
    elif isinstance(time_obj, str):
        iso_value = time_obj

    if not iso_value:
        return None

    # 1. 상대일 치환
    iso_value = replace_relative_dates(iso_value)
    # 2. 연도 붙임
    iso_value = ensure_year_prefix(iso_value)
    # 3. 날짜 포맷 정리
    iso_value = clean_date_format(iso_value)

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
