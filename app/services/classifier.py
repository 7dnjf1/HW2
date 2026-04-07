"""
이미지 분류 서비스
CLIP zero-shot classification → 한국 분리배출 카테고리 매핑
"""
import io
import logging
import time
from pathlib import Path

import torch
import torch.nn.functional as F
from PIL import Image, UnidentifiedImageError

from app.core.config import get_settings
from app.core.model import get_model_manager
from app.services.waste_info import (
    get_clip_labels,
    get_waste_info,
    map_clip_label_to_category,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class ClassificationResult:
    """분류 결과를 담는 데이터 클래스"""

    def __init__(
        self,
        category_key: str,
        confidence: float,
        all_scores: dict[str, float],
        inference_time_ms: float,
    ):
        self.category_key = category_key
        self.confidence = confidence
        self.all_scores = all_scores
        self.inference_time_ms = inference_time_ms


class WasteClassifier:
    """
    CLIP 기반 쓰레기 zero-shot 분류기.
    텍스트 임베딩을 캐싱하여 반복 분류 시 속도 향상.
    """

    def __init__(self):
        self._manager = get_model_manager()
        self._text_features: torch.Tensor | None = None
        self._labels: list[str] = get_clip_labels()

    def _ensure_text_features(self) -> None:
        """레이블 텍스트 임베딩 사전 계산 (최초 1회)"""
        if self._text_features is not None:
            return

        logger.info("텍스트 임베딩 사전 계산 중...")
        # 프롬프트 엔지니어링 — 도메인 특화 표현으로 정확도 향상
        prompts = [f"a photo of {label}" for label in self._labels]

        inputs = self._manager.processor(
            text=prompts,
            return_tensors="pt",
            padding=True,
        ).to(self._manager.device)

        with torch.no_grad():
            self._text_features = self._manager.model.get_text_features(**inputs)
            self._text_features = F.normalize(self._text_features, dim=-1)

        logger.info(f"텍스트 임베딩 완료: {len(self._labels)}개 레이블")

    def _load_image(self, image_bytes: bytes) -> Image.Image:
        """바이트 스트림을 PIL Image로 변환 및 유효성 검사"""
        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except UnidentifiedImageError:
            raise ValueError("지원하지 않는 이미지 형식입니다.")
        except Exception as e:
            raise ValueError(f"이미지 로드 실패: {str(e)}")

        # 최대 파일 크기 검사
        size_mb = len(image_bytes) / (1024 * 1024)
        if size_mb > settings.MAX_IMAGE_SIZE_MB:
            raise ValueError(
                f"이미지 크기 초과: {size_mb:.1f}MB (최대 {settings.MAX_IMAGE_SIZE_MB}MB)"
            )

        return img

    @torch.no_grad()
    def classify(self, image_bytes: bytes) -> ClassificationResult:
        """
        이미지 바이트를 받아 쓰레기 카테고리를 분류.

        Returns:
            ClassificationResult 객체
        """
        if not self._manager.is_loaded:
            raise RuntimeError("모델이 초기화되지 않았습니다.")

        start_time = time.perf_counter()

        # 1. 이미지 로드
        image = self._load_image(image_bytes)

        # 2. 텍스트 임베딩 준비
        self._ensure_text_features()

        # 3. 이미지 임베딩 계산
        image_inputs = self._manager.processor(
            images=image,
            return_tensors="pt",
        ).to(self._manager.device)

        image_features = self._manager.model.get_image_features(**image_inputs)
        image_features = F.normalize(image_features, dim=-1)

        # 4. 코사인 유사도 계산 → softmax로 확률 변환
        logits = (image_features @ self._text_features.T) * 100  # temperature scaling
        probs = F.softmax(logits, dim=-1).squeeze().cpu().tolist()

        # 5. 결과 정리
        scores: dict[str, float] = {
            label: round(float(prob), 4)
            for label, prob in zip(self._labels, probs)
        }
        best_label = max(scores, key=scores.__getitem__)
        best_confidence = scores[best_label]

        # 6. 신뢰도 임계값 미달 시 일반쓰레기로 fallback
        category_key = map_clip_label_to_category(best_label)
        if best_confidence < settings.CONFIDENCE_THRESHOLD:
            logger.warning(
                f"신뢰도 임계값 미달 ({best_confidence:.3f} < {settings.CONFIDENCE_THRESHOLD})"
                " → 일반쓰레기로 처리"
            )
            category_key = "general_waste"

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            f"분류 완료: {category_key} (신뢰도={best_confidence:.3f}, "
            f"추론시간={elapsed_ms:.1f}ms)"
        )

        return ClassificationResult(
            category_key=category_key,
            confidence=best_confidence,
            all_scores=scores,
            inference_time_ms=round(elapsed_ms, 2),
        )


# 서비스 싱글턴
_classifier: WasteClassifier | None = None


def get_classifier() -> WasteClassifier:
    global _classifier
    if _classifier is None:
        _classifier = WasteClassifier()
    return _classifier
