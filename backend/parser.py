import spacy

try:
    # 한국어 모델 'ko_core_news_lg' 로드 시도
    nlp = spacy.load("ko_core_news_lg")
except OSError:
    # 모델이 설치되어 있지 않으면 안내 메시지와 함께 예외 발생
    raise RuntimeError(
        "ko_core_news_lg 모델이 설치되어 있어야 합니다.\n"
        "다음 명령어로 설치하세요:\n"
        "python -m spacy download ko_core_news_lg"
    )


def extract_locations(text: str):
    """
    입력된 텍스트에서 장소 관련 개체명(Named Entities)을 추출합니다.

    spaCy 한국어 모델의 개체명 인식 결과에서 아래 라벨에 해당하는 텍스트 추출:
    - LOC: Location (장소)
    - GPE: Geo-Political Entity (지명, 국가, 도시 등)
    - FAC: Facility (건물, 시설)
    - ORG: Organization (조직 이름)
    - LC: Location Context (특정 지리적 문맥)

    추가로, spaCy가 못 잡는 경우를 대비해
    미리 정의한 장소 키워드(예: "본사", "강남역", "회의실", "카페")를 텍스트에 포함되어 있으면 결과에 추가합니다.

    Args:
        text (str): 장소 추출 대상 텍스트

    Returns:
        List[str]: 추출된 장소 이름 리스트 (중복 제거 불가시 그대로 배열 반환)
    """

    location_labels = ("LOC", "GPE", "FAC", "ORG", "LC")
    doc = nlp(text)  # 텍스트를 spaCy 파이프라인에 통과시켜 객체 생성

    # 텍스트에서 장소 관련 개체명만 추출
    entities = [ent.text for ent in doc.ents if ent.label_ in location_labels]

    # 추가 장소 리스트: spaCy가 못 잡는 보충 명칭들
    extra_locations = ["본사", "강남역", "회의실", "카페"]
    for loc in extra_locations:
        # 텍스트에 있고 아직 결과에 없으면 추가
        if loc in text and loc not in entities:
            entities.append(loc)

    return entities
