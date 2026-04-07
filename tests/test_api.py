"""
pytest 기반 API 통합 테스트
실제 모델 없이도 동작하도록 Mock 패치 사용
"""
import io
import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

# 모델 로드를 Mock으로 대체하여 테스트 속도 향상
with patch("app.core.model.CLIPModel"), patch("app.core.model.CLIPProcessor"):
    from app.main import app

client = TestClient(app, raise_server_exceptions=False)


# ─────────────────────────────────────────────
# 헬퍼
# ─────────────────────────────────────────────
def make_test_image(color: tuple = (255, 0, 0), fmt: str = "JPEG") -> bytes:
    """테스트용 더미 이미지 바이트 생성"""
    img = Image.new("RGB", (224, 224), color=color)
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf.read()


# ─────────────────────────────────────────────
# 루트 & 헬스체크
# ─────────────────────────────────────────────
class TestRoot:
    def test_root_returns_200(self):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_root_contains_name(self):
        resp = client.get("/")
        data = resp.json()
        assert "name" in data
        assert "endpoints" in data

    def test_health_endpoint(self):
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
        assert "model_loaded" in data
        assert "device" in data


# ─────────────────────────────────────────────
# 카테고리 목록
# ─────────────────────────────────────────────
class TestCategories:
    def test_list_categories_returns_200(self):
        resp = client.get("/api/v1/categories")
        assert resp.status_code == 200

    def test_list_categories_structure(self):
        resp = client.get("/api/v1/categories")
        data = resp.json()
        assert data["success"] is True
        assert data["total"] > 0
        assert isinstance(data["categories"], list)

    def test_list_categories_has_required_fields(self):
        resp = client.get("/api/v1/categories")
        data = resp.json()
        category = data["categories"][0]
        assert "key" in category
        assert "name" in category
        assert "recyclable" in category

    def test_list_categories_count(self):
        resp = client.get("/api/v1/categories")
        data = resp.json()
        # 9개 카테고리 (plastic, glass, metal, paper, food_waste, general_waste,
        #               battery, vinyl, styrofoam, clothing)
        assert data["total"] == 10


# ─────────────────────────────────────────────
# 카테고리 정보 직접 조회
# ─────────────────────────────────────────────
class TestCategoryInfo:
    def test_plastic_info(self):
        resp = client.get("/api/v1/info/plastic")
        assert resp.status_code == 200
        data = resp.json()
        assert data["category_code"] == "PL"
        assert "disposal_steps" in data
        assert data["fine_amount_krw"] > 0

    def test_invalid_category_returns_404(self):
        resp = client.get("/api/v1/info/invalid_category")
        assert resp.status_code == 404

    @pytest.mark.parametrize("key", [
        "plastic", "glass", "metal", "paper",
        "food_waste", "general_waste", "battery",
        "vinyl", "styrofoam", "clothing",
    ])
    def test_all_categories_valid(self, key: str):
        resp = client.get(f"/api/v1/info/{key}")
        assert resp.status_code == 200


# ─────────────────────────────────────────────
# 이미지 분류 (모델 Mock 사용)
# ─────────────────────────────────────────────
class TestClassify:
    def _mock_classify_result(self):
        """Mock 분류 결과 반환"""
        mock_result = MagicMock()
        mock_result.category_key = "plastic"
        mock_result.confidence = 0.85
        mock_result.inference_time_ms = 42.0
        mock_result.all_scores = {
            "plastic bottle or plastic container": 0.85,
            "glass bottle or glass jar": 0.05,
            "aluminum can or metal can": 0.03,
        }
        return mock_result

    def test_classify_no_file_returns_422(self):
        resp = client.post("/api/v1/classify")
        assert resp.status_code == 422

    def test_classify_empty_file_returns_400(self):
        resp = client.post(
            "/api/v1/classify",
            files={"file": ("test.jpg", b"", "image/jpeg")},
        )
        assert resp.status_code == 400

    def test_classify_invalid_extension_returns_400(self):
        resp = client.post(
            "/api/v1/classify",
            files={"file": ("test.txt", b"text content", "text/plain")},
        )
        assert resp.status_code == 400

    def test_classify_with_mock_model(self):
        """모델을 Mock으로 대체하여 전체 파이프라인 테스트"""
        image_bytes = make_test_image()
        mock_result = self._mock_classify_result()

        with patch("app.api.routes.get_model_manager") as mock_manager_fn, \
             patch("app.api.routes.get_classifier") as mock_clf_fn:

            # 모델 로드 상태 = True
            mock_mgr = MagicMock()
            mock_mgr.is_loaded = True
            mock_manager_fn.return_value = mock_mgr

            # classifier.classify() 반환값 설정
            mock_clf = MagicMock()
            mock_clf.classify.return_value = mock_result
            mock_clf_fn.return_value = mock_clf

            resp = client.post(
                "/api/v1/classify",
                files={"file": ("plastic.jpg", image_bytes, "image/jpeg")},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["category_key"] == "plastic"
        assert data["confidence"] == 0.85
        assert "disposal_info" in data
        assert "top_predictions" in data
        assert data["standard_year"] == 2026
        assert data["disposal_info"]["category_code"] == "PL"

    def test_classify_response_has_fine_info(self):
        """응답에 과태료 정보 포함 여부 확인"""
        image_bytes = make_test_image()
        mock_result = self._mock_classify_result()

        with patch("app.api.routes.get_model_manager") as mock_manager_fn, \
             patch("app.api.routes.get_classifier") as mock_clf_fn:
            mock_mgr = MagicMock()
            mock_mgr.is_loaded = True
            mock_manager_fn.return_value = mock_mgr

            mock_clf = MagicMock()
            mock_clf.classify.return_value = mock_result
            mock_clf_fn.return_value = mock_clf

            resp = client.post(
                "/api/v1/classify",
                files={"file": ("test.jpg", image_bytes, "image/jpeg")},
            )

        data = resp.json()
        assert "fine_amount_krw" in data["disposal_info"]
        assert "fine_if_violated" in data["disposal_info"]
        assert data["disposal_info"]["fine_amount_krw"] >= 0

    def test_classify_503_when_model_not_loaded(self):
        """모델 미로드 시 503 반환 확인"""
        image_bytes = make_test_image()

        with patch("app.api.routes.get_model_manager") as mock_manager_fn:
            mock_mgr = MagicMock()
            mock_mgr.is_loaded = False
            mock_manager_fn.return_value = mock_mgr

            resp = client.post(
                "/api/v1/classify",
                files={"file": ("test.jpg", image_bytes, "image/jpeg")},
            )

        assert resp.status_code == 503


# ─────────────────────────────────────────────
# 폐배터리 과태료 검증
# ─────────────────────────────────────────────
class TestBatteryFine:
    def test_battery_has_higher_fine(self):
        """폐배터리는 300,000원으로 다른 품목(100,000원)보다 높은 과태료"""
        battery_resp = client.get("/api/v1/info/battery")
        plastic_resp = client.get("/api/v1/info/plastic")

        assert battery_resp.status_code == 200
        assert plastic_resp.status_code == 200

        battery_fine = battery_resp.json()["fine_amount_krw"]
        plastic_fine = plastic_resp.json()["fine_amount_krw"]

        assert battery_fine > plastic_fine
        assert battery_fine == 300000


# ─────────────────────────────────────────────
# 음식물 쓰레기 재활용 불가 검증
# ─────────────────────────────────────────────
class TestFoodWaste:
    def test_food_waste_not_recyclable(self):
        resp = client.get("/api/v1/info/food_waste")
        assert resp.status_code == 200
        data = resp.json()
        assert data["recyclable"] is False

    def test_general_waste_not_recyclable(self):
        resp = client.get("/api/v1/info/general_waste")
        data = resp.json()
        assert data["recyclable"] is False
