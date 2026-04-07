"""
앱 전역 설정 관리 (pydantic-settings 사용)
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 앱 기본 정보
    APP_NAME: str = "지능형 분리수거 도우미 API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "2026년 한국 분리배출 기준에 따른 AI 기반 쓰레기 분류 API"

    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # 모델 설정
    # CLIP zero-shot 분류 사용 (별도 fine-tuning 불필요)
    CLIP_MODEL_NAME: str = "openai/clip-vit-base-patch32"
    MODEL_CACHE_DIR: str = "./models"

    # 이미지 업로드 제한
    MAX_IMAGE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: list[str] = ["jpg", "jpeg", "png", "webp", "bmp"]

    # 분류 신뢰도 임계값
    CONFIDENCE_THRESHOLD: float = 0.15

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
