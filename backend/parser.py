import spacy

try:
    nlp = spacy.load("ko_core_news_lg")
except OSError:
    raise RuntimeError("ko_core_news_lg 모델이 설치되어 있어야 합니다.\n"
                       "python -m spacy download ko_core_news_lg 명령어로 설치하세요.")

def extract_locations(text: str):
    location_labels = ("LOC", "GPE", "FAC", "ORG", "LC")
    doc = nlp(text)
    entities = [ent.text for ent in doc.ents if ent.label_ in location_labels]

    extra_locations = ["본사", "강남역", "회의실", "카페"]
    for loc in extra_locations:
        if loc in text and loc not in entities:
            entities.append(loc)

    return entities