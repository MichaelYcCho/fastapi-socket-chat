# 베이스 이미지 설정
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# Poetry 설치
RUN pip install poetry

# 필요한 파일 복사
COPY pyproject.toml poetry.lock /app/

# 종속성 설치
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# 애플리케이션 소스 복사
COPY . /app

# 포트 설정
EXPOSE 8000

# 컨테이너 시작 시 실행할 명령어
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]