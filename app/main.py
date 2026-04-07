"""
FastAPI 애플리케이션 진입점
lifespan 이벤트로 모델 로드/해제 관리
"""
import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import get_settings
from app.core.model import get_model_manager

# ─────────────────────────────────────────────
# 로거 설정
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)
settings = get_settings()


# ─────────────────────────────────────────────
# Lifespan: 앱 시작/종료 이벤트 처리
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    앱 시작 시 ML 모델을 로드하고,
    앱 종료 시 메모리를 해제합니다.
    """
    logger.info("=" * 60)
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} 시작 중...")
    logger.info("=" * 60)

    # 모델 로드 (최초 실행 시 Hugging Face Hub에서 다운로드)
    manager = get_model_manager()
    try:
        manager.load()
        logger.info("✅ 서버 준비 완료 — 요청을 받을 수 있습니다.")
    except Exception as e:
        logger.error(f"❌ 모델 로드 실패: {e}")
        logger.warning("⚠️  서버는 시작되지만 /classify 엔드포인트는 503을 반환합니다.")

    yield  # 서버 실행 구간

    # 종료 처리
    logger.info("🛑 서버 종료 중 — 모델 메모리 해제...")
    manager.unload()
    logger.info("✅ 정상 종료 완료")


# ─────────────────────────────────────────────
# FastAPI 앱 초기화
# ─────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",        # Swagger UI
    redoc_url="/redoc",      # ReDoc UI
    openapi_url="/openapi.json",
)

# ─────────────────────────────────────────────
# 미들웨어 등록
# ─────────────────────────────────────────────

# CORS — 프론트엔드 연동 및 로컬 테스트용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip 압축 — 큰 JSON 응답 압축
app.add_middleware(GZipMiddleware, minimum_size=1000)


# ─────────────────────────────────────────────
# 전역 예외 핸들러
# ─────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"처리되지 않은 예외: {exc} | URL: {request.url}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "서버 내부 오류가 발생했습니다.",
        },
    )


# ─────────────────────────────────────────────
# 라우터 등록
# ─────────────────────────────────────────────
app.include_router(router, prefix="/api/v1")


# ─────────────────────────────────────────────
# 루트 엔드포인트
# ─────────────────────────────────────────────
@app.get("/", tags=["Root"], summary="API 정보")
async def root():
    """API 기본 정보 및 주요 엔드포인트 안내"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "standard": "2026년 한국 분리배출 기준",
        "endpoints": {
            "swagger_ui":   "/docs",
            "redoc":        "/redoc",
            "health":       "/api/v1/health",
            "categories":   "/api/v1/categories",
            "classify":     "POST /api/v1/classify",
            "waste_info":   "/api/v1/info/{category_key}",
        },
    }


# ─────────────────────────────────────────────
# 직접 실행 시 uvicorn 구동
# ─────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
