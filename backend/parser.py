import spacy

_nlp = None

def get_nlp():
    global _nlp
    if _nlp is None:
        try:
            print("Trying to load spaCy model ko_core_news_lg ...")
            _nlp = spacy.load("ko_core_news_lg")
            print("Model loaded successfully.")
        except Exception as e:
            # 어떤 예외가 발생하는지 출력
            print(f"[ERROR] Failed to load spaCy model: {e}")
            raise RuntimeError(f"런타임 오류: {e}")
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

    entities = list(dict.fromkeys(entities))

    print(f"[DEBUG] extract_locations called with: '{text}', entities: {entities}")

    return entities
