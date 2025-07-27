import spacy

_nlp = None

def get_nlp():
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("ko_core_news_lg")
        except OSError:
            raise RuntimeError(
                "ko_core_news_lg 모델이 설치되어 있어야 합니다.\n"
                "다음 명령어로 설치하세요:\n"
                "python -m spacy download ko_core_news_lg"
            )
    return _nlp


def extract_locations(text: str):
    nlp = get_nlp()
    location_labels = ("LOC", "GPE", "FAC", "ORG", "LC")
    doc = nlp(text)

    entities = [ent.text for ent in doc.ents if ent.label_ in location_labels]

    extra_locations = ["본사", "강남역", "회의실", "카페"]
    for loc in extra_locations:
        if loc in text and loc not in entities:
            entities.append(loc)

    # 필요하면 중복 제거
    entities = list(dict.fromkeys(entities))

    return entities
