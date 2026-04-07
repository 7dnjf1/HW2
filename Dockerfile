# ─────────────────────────────────────────────
# 지능형 분리수거 도우미 API — Dockerfile
# Multi-stage build로 이미지 크기 최소화
# ─────────────────────────────────────────────

# ── Stage 1: 의존성 설치 (빌더) ───────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# 빌드 도구 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# pip 최신화 및 의존성 설치
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: 런타임 이미지 ───────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# 런타임 라이브러리만 복사
COPY --from=builder /install /usr/local

# 소스코드 복사
COPY app/ ./app/

# Hugging Face 모델 캐시 디렉토리 생성
RUN mkdir -p /app/models

# 비루트 사용자 생성 (보안 강화)
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# 환경 변수
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MODEL_CACHE_DIR=/app/models \
    HOST=0.0.0.0 \
    PORT=8000

EXPOSE 8000

# 헬스체크
HEALTHCHECK --interval=30s --timeout=30s --start-period=120s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

# 서버 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
