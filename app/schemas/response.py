"""
Pydantic 응답 스키마 정의
FastAPI의 응답 직렬화 및 OpenAPI 문서 자동 생성에 사용
"""
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────
# Enum 정의
# ─────────────────────────────────────────────
class WasteCategoryCode(str, Enum):
    PLASTIC = "PL"
    GLASS = "GL"
    METAL = "MT"
    PAPER = "PA"
    FOOD_WASTE = "FW"
    GENERAL_WASTE = "GW"
    BATTERY = "BT"
    VINYL = "VN"
    STYROFOAM = "SF"
    CLOTHING = "CL"


# ─────────────────────────────────────────────
# 응답 스키마
# ─────────────────────────────────────────────
class DisposalInfo(BaseModel):
    """분리배출 상세 정보"""

    category_code: str = Field(..., description="카테고리 코드 (예: PL, GL, MT)")
    category_name: str = Field(..., description="카테고리 한글명")
    sub_categories: list[str] = Field(..., description="세부 품목 목록")
    disposal_steps: list[str] = Field(..., description="단계별 배출 방법")
    collection_bag: str = Field(..., description="필요한 배출 용기/봉투")
    collection_day_tip: str = Field(..., description="배출 시간/요일 팁")
    fine_if_violated: str = Field(..., description="위반 시 과태료 부과 기준")
    fine_amount_krw: int = Field(..., description="과태료 금액 (원)", ge=0)
    tips: list[str] = Field(..., description="분리배출 꿀팁")
    recyclable: bool = Field(..., description="재활용 가능 여부")
    icons: list[str] = Field(..., description="카테고리 이모지 아이콘")


class ClassificationScore(BaseModel):
    """개별 카테고리 분류 점수"""

    label: str = Field(..., description="CLIP 레이블 (영어)")
    score: float = Field(..., description="softmax 확률 점수", ge=0.0, le=1.0)


class ClassifyResponse(BaseModel):
    """쓰레기 분류 API 메인 응답"""

    success: bool = Field(True, description="요청 처리 성공 여부")
    category_key: str = Field(..., description="내부 카테고리 키 (예: plastic, glass)")
    confidence: float = Field(
        ..., description="최고 신뢰도 점수 (0.0~1.0)", ge=0.0, le=1.0
    )
    disposal_info: DisposalInfo = Field(..., description="2026 한국 분리배출 기준 정보")
    top_predictions: list[ClassificationScore] = Field(
        ..., description="상위 3개 분류 후보 (신뢰도 내림차순)"
    )
    inference_time_ms: float = Field(..., description="모델 추론 소요 시간 (ms)")
    model_name: str = Field(..., description="사용된 ML 모델명")
    standard_year: int = Field(2026, description="적용 분리배출 기준 연도")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "category_key": "plastic",
                "confidence": 0.812,
                "disposal_info": {
                    "category_code": "PL",
                    "category_name": "플라스틱",
                    "sub_categories": ["PET병", "PP", "PE"],
                    "disposal_steps": [
                        "내용물을 깨끗이 비우고 물로 헹군다",
                        "라벨을 제거한다",
                        "찌그러뜨려 부피를 줄인다",
                    ],
                    "collection_bag": "별도 분리수거함",
                    "collection_day_tip": "지자체별 플라스틱 수거일 확인",
                    "fine_if_violated": "혼합 배출 시 과태료 부과",
                    "fine_amount_krw": 100000,
                    "tips": ["내용물이 남아있으면 재활용 불가"],
                    "recyclable": True,
                    "icons": ["♻️", "🧴"],
                },
                "top_predictions": [
                    {"label": "plastic bottle or plastic container", "score": 0.812},
                    {"label": "plastic bag or vinyl bag", "score": 0.051},
                    {"label": "styrofoam packaging", "score": 0.031},
                ],
                "inference_time_ms": 123.4,
                "model_name": "openai/clip-vit-base-patch32",
                "standard_year": 2026,
            }
        }
    }


class CategoryListItem(BaseModel):
    """카테고리 목록 아이템"""

    key: str
    code: str
    name: str
    recyclable: bool
    icons: list[str]


class CategoryListResponse(BaseModel):
    """카테고리 목록 응답"""

    success: bool = True
    total: int
    categories: list[CategoryListItem]


class HealthResponse(BaseModel):
    """헬스체크 응답"""

    status: str = Field(..., description="서버 상태 (healthy / degraded)")
    model_loaded: bool = Field(..., description="ML 모델 로드 여부")
    device: str = Field(..., description="추론 디바이스 (cpu / cuda)")
    version: str = Field(..., description="API 버전")


class ErrorResponse(BaseModel):
    """에러 응답"""

    success: bool = False
    error_code: str = Field(..., description="에러 코드")
    message: str = Field(..., description="에러 메시지")
    detail: Any = Field(None, description="추가 에러 정보")
