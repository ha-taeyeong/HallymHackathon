from fastapi import FastAPI
from pydantic import BaseModel
import requests
from parser import extract_locations  # parser.py에서 함수 임포트

app = FastAPI()

class TextRequest(BaseModel):
    text: str

@app.post("/parse-datetime/")
def parse_datetime(req: TextRequest):
    duckling_url = "http://localhost:8000/parse"
    data = {
        "text": req.text,
        "locale": "ko_KR",
        "dims": '["time"]'
    }
    response = requests.post(duckling_url, data=data)
    return response.json()

@app.post("/extract-location/")
def extract_location(req: TextRequest):
    locations = extract_locations(req.text)
    return {"locations": locations}
