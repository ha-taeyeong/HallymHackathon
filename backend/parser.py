import stanza
import re
import json
import os

# Stanza 한국어 NLP 파이프라인 객체를 전역 저장용 변수로 선언
_nlp = None

def get_nlp():
    """
    Stanza 한국어 NLP 파이프라인 초기화 및 반환 함수.
    최초 호출 시에만 파이프라인을 생성하고 이후에는 재사용하여 성능 최적화.
    프로세서: 토큰화, 품사 태깅, 표제어 추출 포함
    """
    global _nlp
    if _nlp is None:
        _nlp = stanza.Pipeline(lang="ko", processors="tokenize,pos,lemma")
    return _nlp

def load_location_keywords(filepath="locations.json"):
    """
    지정된 JSON 파일에서 위치 키워드 리스트를 로드.
    파일이 존재하고, 내용이 리스트라면 리스트 반환, 아니면 빈 리스트 반환.
    """
    if os.path.exists(filepath):
        with open(filepath, encoding="utf-8") as f:
            lst = json.load(f)
            if isinstance(lst, list):
                return lst
    return []

def load_location_keywords_extended(filepath="locations_extended.json"):
    """
    위치 키워드 확장 리스트를 JSON 파일에서 로드.
    기본 위치 키워드 외에 추가로 관리하기 위한 용도.
    """
    if os.path.exists(filepath):
        with open(filepath, encoding="utf-8") as f:
            lst = json.load(f)
            if isinstance(lst, list):
                return lst
    return []

# 기본 위치 키워드와 확장 위치 키워드를 합친 리스트 생성
location_keywords = load_location_keywords()
location_keywords_extended = location_keywords + load_location_keywords_extended()

def extract_locations(text: str):
    """
    텍스트에서 위치와 관련된 키워드 및 조합된 위치명을 추출하는 함수.
    
    동작 원리:
    1) Stanza NLP로 문장 분석 수행 (현재 결과는 직접 사용하지 않음).
    2) 정규식으로 위치 키워드 기반 후보 명칭 찾기:
       - location_keywords_extended 리스트 내 단어 중 하나로 시작.
       - 뒤따르는 층, 호, 번, 출구 등 위치 상세 정보 허용.
       - 한글 또는 영어 단어(세미나실, Café 등) 추가 가능.
    3) 중복, 숫자만 있는 후보 제외 후 리스트 반환.
    4) 후보를 찾지 못하면, 위치 키워드가 텍스트에 포함됐는지 단순 검사 후 리턴.
    """
    nlp = get_nlp()
    doc = nlp(text)  # 형태소 분석(현재는 결과 직접 사용 안 함)
    entities = []

    # 정규식 패턴 생성: 위치 키워드 + 층/호/번/출구 등의 상세 정보 + 부가 명칭
    pattern = re.compile(
        r'((?:' + '|'.join(map(re.escape, location_keywords_extended)) + r')'  # 위치 키워드 중 하나
        r'(?:[\s\d]{0,7}(?:층|호|번|출구)?)?'                               # 최대 7자리 숫자 + 층/호/번/출구 뒤에 올 수 있음
        r'(?:\s*[가-힣A-Za-z]+)?'                                          # 부가 명칭(한글/영어) 선택적
        r')'
    )

    for match in pattern.finditer(text):
        value = match.group(0).strip()
        # 순수 숫자나 길이 1 이하 문자열, 중복 제거
        if not value.isdigit() and len(value) > 1 and value not in entities:
            entities.append(value)

    # 정규식 패턴으로 후보 못 찾았으면, 텍스트 내 위치 키워드 포함 여부 단순 검사
    if not entities:
        for kw in location_keywords_extended:
            if kw in text and kw not in entities:
                entities.append(kw)

    return entities


def parse_schedule_sentence(text):
    """
    일정 문장에서 시간, 장소, 이벤트를 분리하는 함수.
    
    1) 시간 추출:
       - 날짜 + 시간, 또는 시간 단독 패턴 인식 (예: '8월 3일 오후 3시', '16:00', '오전 10시' 등).
    2) 텍스트에서 시간 부분 제거 후 남은 부분을 대상으로 장소 추출:
       - location_keywords_extended 키워드 기반 동적 정규식 생성.
       - '3호'처럼 숫자 + 호 등의 조합 포함.
    3) 남은 텍스트에서 이벤트명 추출:
       - event_keywords 목록 내 단어 우선 탐색.
       - 후보 없으면 원본 이벤트 텍스트 반환, 기본값은 "일정".
       
    반환값:
      시간 문자열, 장소 문자열, 이벤트 문자열
    """
    # 시간 패턴 정규식
    time_pattern = re.compile(
        r'(\d{1,2}월\s*\d{1,2}일\s*(오전|오후)?\s*\d{1,2}[:시]?\d{0,2}|\d{1,2}[:]\d{2}|오전\s*\d{1,2}시|오후\s*\d{1,2}시)'
    )
    time_match = time_pattern.search(text)
    if time_match:
        time_str = time_match.group(0).strip()
        # 시간 부분 삭제하여 남은 텍스트 추출
        rest = text.replace(time_str, "").strip()
    else:
        time_str = None
        rest = text.strip()

    # 장소 키워드를 동적으로 정규식 패턴에 반영하여 추출
    location_keywords_re = '|'.join(map(re.escape, location_keywords_extended))
    location_pattern = re.compile(rf'(({location_keywords_re})[\s\d]*호?)')
    location_matches = location_pattern.findall(rest)

    if location_matches:
        # 장소 후보들을 합쳐 하나의 문자열로 만듦
        location_str = " ".join(match[0] for match in location_matches)
        # 장소 후보들을 제거한 나머지는 이벤트 후보
        event_str = rest
        for loc in location_matches:
            event_str = event_str.replace(loc[0], "")
        event_str = event_str.strip()
    else:
        location_str = None
        event_str = rest

    # 이벤트 키워드 기반 간단 탐색 함수
    def extract_event(event_text, keywords):
        for kw in keywords:
            if kw in event_text:
                return kw
        return event_text if event_text else "일정"

    from main import event_keywords  # event_keywords는 main.py에서 로드한 글로벌 리스트 (구조에 맞게 import 조절 필요)
    event_str = extract_event(event_str, event_keywords)

    return time_str or "시간 정보 없음", location_str or "위치 정보 없음", event_str or "일정"
