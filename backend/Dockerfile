# 1. Python 3.11 슬림 이미지
FROM python:3.11-slim

# 2. 필수 빌드 도구 설치
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# 3. 작업 폴더 지정
WORKDIR /app

# 4. 의존성 설치 (기존 동일)
COPY backend/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# [수정된 부분] 5. 소스 코드 복사
# backend 폴더 내용을 /app/backend가 아닌 /app에 바로 복사했다면 아래 구조가 맞습니다.
COPY backend/ . 

# [중요] 프론트엔드 빌드 결과물(dist)을 컨테이너 내부로 복사합니다.
# main.py에서 '/frontend/dist/assets'를 찾는다면, 루트(/)에 생성해줘야 합니다.
COPY frontend/dist /frontend/dist

# 6. spaCy 설치 (기존 동일)
RUN python -m spacy download ko_core_news_lg

# 7. 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]