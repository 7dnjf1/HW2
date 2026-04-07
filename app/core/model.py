"""
CLIP 모델 싱글턴 로더
앱 시작 시 1회 로드 후 재사용 (메모리 효율)
"""
import logging
import os
from functools import lru_cache

import torch
from transformers import CLIPModel, CLIPProcessor

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ModelManager:
    """
    CLIP 모델 및 프로세서를 싱글턴으로 관리.
    ThreadLocal-safe: FastAPI startup event에서 한 번 초기화.
    """

    def __init__(self):
        self._model: CLIPModel | None = None
        self._processor: CLIPProcessor | None = None
        self._device: str = "cuda" if torch.cuda.is_available() else "cpu"

    def load(self) -> None:
        """Hugging Face Hub에서 CLIP 모델 다운로드 및 로드"""
        if self._model is not None:
            logger.info("모델이 이미 로드되어 있습니다.")
            return

        logger.info(
            f"CLIP 모델 로딩 중: {settings.CLIP_MODEL_NAME} (device={self._device})"
        )

        os.makedirs(settings.MODEL_CACHE_DIR, exist_ok=True)

        self._processor = CLIPProcessor.from_pretrained(
            settings.CLIP_MODEL_NAME,
            cache_dir=settings.MODEL_CACHE_DIR,
        )
        self._model = CLIPModel.from_pretrained(
            settings.CLIP_MODEL_NAME,
            cache_dir=settings.MODEL_CACHE_DIR,
        ).to(self._device)

        self._model.eval()  # 추론 모드
        logger.info("✅ CLIP 모델 로드 완료")

    def unload(self) -> None:
        """메모리 해제 (앱 종료 시 호출)"""
        self._model = None
        self._processor = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("모델 메모리 해제 완료")

    @property
    def model(self) -> CLIPModel:
        if self._model is None:
            raise RuntimeError("모델이 로드되지 않았습니다. load()를 먼저 호출하세요.")
        return self._model

    @property
    def processor(self) -> CLIPProcessor:
        if self._processor is None:
            raise RuntimeError("프로세서가 로드되지 않았습니다.")
        return self._processor

    @property
    def device(self) -> str:
        return self._device

    @property
    def is_loaded(self) -> bool:
        return self._model is not None


# 전역 싱글턴 인스턴스
model_manager = ModelManager()


@lru_cache(maxsize=1)
def get_model_manager() -> ModelManager:
    return model_manager
