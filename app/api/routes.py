"""
API 라우터 — 쓰레기 분류 관련 엔드포인트 정의
"""
import logging
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.model import get_model_manager
from app.schemas.response import (
    CategoryListResponse,
    ClassificationScore,
    ClassifyResponse,
    DisposalInfo,
    ErrorResponse,
    HealthResponse,
)
from app.services.classifier import get_classifier
from app.services.waste_info import get_all_categories, get_waste_info

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()


# ─────────────────────────────────────────────
# 헬스체크
# ─────────────────────────────────────────────
@router.get(
    "/health",
    response_model=HealthResponse,
    summary="서버 상태 확인",
    tags=["System"],
)
async def health_check():
    """
    서버 및 ML 모델 상태를 확인합니다.
    모니터링 시스템(Prometheus, k8s liveness probe 등)에서 사용 가능.
    """
    manager = get_model_manager()
    return HealthResponse(
        status="healthy" if manager.is_loaded else "degraded",
        model_loaded=manager.is_loaded,
        device=manager.device,
        version=settings.APP_VERSION,
    )


# ─────────────────────────────────────────────
# 카테고리 목록 조회
# ─────────────────────────────────────────────
@router.get(
    "/categories",
    response_model=CategoryListResponse,
    summary="분리배출 카테고리 목록",
    tags=["Waste Info"],
)
async def list_categories():
    """
    지원하는 모든 분리배출 카테고리 목록을 반환합니다.
    (2026년 한국 분리배출 기준)
    """
    categories = get_all_categories()
    return CategoryListResponse(
        total=len(categories),
        categories=categories,
    )


# ─────────────────────────────────────────────
# 쓰레기 이미지 분류 (핵심 엔드포인트)
# ─────────────────────────────────────────────
@router.post(
    "/classify",
    response_model=ClassifyResponse,
    summary="쓰레기 이미지 분류",
    tags=["Classification"],
    responses={
        400: {"model": ErrorResponse, "description": "잘못된 요청 (이미지 형식 오류 등)"},
        422: {"model": ErrorResponse, "description": "파일 업로드 실패"},
        500: {"model": ErrorResponse, "description": "서버 내부 오류"},
        503: {"model": ErrorResponse, "description": "모델 미로드 상태"},
    },
)
async def classify_waste(
    file: Annotated[
        UploadFile,
        File(description="분류할 쓰레기 이미지 (JPG, PNG, WebP, BMP 지원, 최대 10MB)"),
    ],
):
    """
    ## 쓰레기 이미지 분류 API

    이미지를 업로드하면 **2026년 한국 분리배출 기준**에 따라 자동 분류하고,
    구체적인 배출 방법 및 과태료 정보를 반환합니다.

    ### 분류 카테고리
    - 🧴 플라스틱 (PL)
    - 🍶 유리 (GL)
    - 🥫 캔/고철 (MT)
    - 📦 종이/박스 (PA)
    - 🍚 음식물 쓰레기 (FW)
    - 🗑️ 일반 쓰레기 (GW)
    - 🔋 폐배터리/전자제품 (BT)
    - 🛍️ 비닐류 (VN)
    - 📦 스티로폼 (SF)
    - 👕 의류/섬유 (CL)

    ### 사용 모델
    `openai/clip-vit-base-patch32` — zero-shot 이미지-텍스트 분류
    """
    # 1. 파일 확장자 검사
    if file.filename:
        ext = file.filename.rsplit(".", 1)[-1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error_code": "INVALID_FILE_TYPE",
                    "message": f"지원하지 않는 파일 형식: .{ext}",
                    "detail": f"지원 형식: {', '.join(settings.ALLOWED_EXTENSIONS)}",
                },
            )

    # 2. 파일 읽기
    try:
        image_bytes = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "success": False,
                "error_code": "FILE_READ_ERROR",
                "message": f"파일 읽기 실패: {str(e)}",
            },
        )

    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error_code": "EMPTY_FILE",
                "message": "빈 파일이 업로드되었습니다.",
            },
        )

    # 3. 모델 로드 상태 확인
    manager = get_model_manager()
    if not manager.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "success": False,
                "error_code": "MODEL_NOT_LOADED",
                "message": "ML 모델이 아직 로드되지 않았습니다. 잠시 후 재시도 해주세요.",
            },
        )

    # 4. 이미지 분류
    classifier = get_classifier()
    try:
        result = classifier.classify(image_bytes)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error_code": "IMAGE_PROCESS_ERROR",
                "message": str(e),
            },
        )
    except Exception as e:
        logger.exception(f"분류 중 예상치 못한 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error_code": "CLASSIFICATION_ERROR",
                "message": "이미지 분류 중 서버 오류가 발생했습니다.",
            },
        )

    # 5. 분리배출 정보 조회
    waste_info = get_waste_info(result.category_key)
    if waste_info is None:
        waste_info = get_waste_info("general_waste")

    # 6. 상위 3개 예측 결과 정리
    top3 = sorted(result.all_scores.items(), key=lambda x: x[1], reverse=True)[:3]
    top_predictions = [
        ClassificationScore(label=label, score=score) for label, score in top3
    ]

    # 7. 응답 조립
    return ClassifyResponse(
        success=True,
        category_key=result.category_key,
        confidence=result.confidence,
        disposal_info=DisposalInfo(**waste_info),
        top_predictions=top_predictions,
        inference_time_ms=result.inference_time_ms,
        model_name=settings.CLIP_MODEL_NAME,
        standard_year=2026,
    )


# ─────────────────────────────────────────────
# 특정 카테고리 배출 정보 직접 조회
# ─────────────────────────────────────────────
@router.get(
    "/info/{category_key}",
    response_model=DisposalInfo,
    summary="카테고리별 배출 정보 조회",
    tags=["Waste Info"],
    responses={
        404: {"model": ErrorResponse, "description": "해당 카테고리를 찾을 수 없음"},
    },
)
async def get_category_info(category_key: str):
    """
    카테고리 키(예: `plastic`, `glass`)로 배출 정보를 직접 조회합니다.
    이미지 분류 없이 텍스트로 카테고리를 알고 있을 때 사용합니다.
    """
    info = get_waste_info(category_key.lower())
    if info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error_code": "CATEGORY_NOT_FOUND",
                "message": f"카테고리를 찾을 수 없습니다: '{category_key}'",
                "detail": "GET /api/v1/categories 로 유효한 카테고리 목록을 확인하세요.",
            },
        )
    return DisposalInfo(**info)
