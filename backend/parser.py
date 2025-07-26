import spacy

nlp = spacy.load("ko_core_news_lg")

def extract_locations(text: str):
    location_labels = ("LOC", "GPE", "FAC", "ORG", "LC")  # 'LC' 추가
    doc = nlp(text)
    return [ent.text for ent in doc.ents if ent.label_ in location_labels]
