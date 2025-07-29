# parser.py
import re
import spacy

_nlp = None

def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("ko_core_news_lg")
    return _nlp

def extract_locations(text: str):
    nlp = get_nlp()
    doc = nlp(text)
    location_labels = ("LOC", "GPE", "FAC", "ORG", "LC")
    entities = []

    # 1) spaCy 개체명 추출 + 후처리
    for ent in doc.ents:
        if ent.label_ in location_labels:
            base_loc = ent.text
            end_pos = ent.end_char
            following = text[end_pos:end_pos+20]
            pattern = re.compile(r'^\s*(\d{1,3}(층|호|번|출구)?\s*)+')
            match = pattern.match(following)
            full_loc = base_loc + (match.group(0) if match else "")
            full_loc = full_loc.strip()
            if full_loc and full_loc not in entities:
                entities.append(full_loc)

    # 2) 만약 개체명 추출이 없거나 불충분하면, 패턴으로 fallback
    pattern = re.compile(r'(본사(\s?\d{1,3}(층|호)?)?)')
    match = pattern.search(text)
    if match:
        value = match.group(0).strip()
        if value and value not in entities:
            entities.append(value)
    return entities
