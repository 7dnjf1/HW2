# 🗑️ 지능형 분리수거 도우미 API

> **2026년 한국 분리배출 기준** 기반 AI 쓰레기 분류 FastAPI 서버  
> `openai/clip-vit-base-patch32` zero-shot 분류 모델 사용

---

## 📁 프로젝트 구조

```
HW2/
├── app/
│   ├── main.py                 # FastAPI 앱 진입점 (lifespan, 미들웨어)
│   ├── api/
│   │   └── routes.py           # API 라우터 (4개 엔드포인트)
│   ├── core/
│   │   ├── config.py           # 환경변수 기반 설정 (pydantic-settings)
│   │   └── model.py            # CLIP 모델 싱글턴 매니저
│   ├── services/
│   │   ├── classifier.py       # 이미지 분류 서비스 (CLIP zero-shot)
│   │   └── waste_info.py       # 2026 한국 분리배출 기준 DB
│   └── schemas/
│       └── response.py         # Pydantic 응답 스키마
├── tests/
│   └── test_api.py             # pytest 통합 테스트
├── models/                     # 모델 캐시 (자동 생성, git 제외)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── pytest.ini
├── .env.example
└── .gitignore
```

---

## 🚀 빠른 시작

### 1. 가상환경 생성 및 의존성 설치

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. 환경변수 설정 (선택)

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
```

### 3. 서버 실행

```bash
# 개발 모드 (자동 리로드)
uvicorn app.main:app --reload --port 8000

# 또는
python -m app.main
```

서버 구동 시 **CLIP 모델이 자동 다운로드** (~600MB, 최초 1회)됩니다.

---

## 🐳 Docker로 실행

```bash
# 이미지 빌드 및 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d
```

> ⚠️ 첫 실행 시 모델 다운로드로 2~5분 소요 (`start_period: 120s`)

---

## 📡 API 엔드포인트

| Method | 경로 | 설명 |
|--------|------|------|
| `GET` | `/` | API 기본 정보 |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/api/v1/health` | 서버·모델 상태 확인 |
| `GET` | `/api/v1/categories` | 분류 카테고리 목록 |
| **`POST`** | **`/api/v1/classify`** | **쓰레기 이미지 분류 (핵심)** |
| `GET` | `/api/v1/info/{key}` | 카테고리별 배출 정보 |

---

## 🔬 분류 API 사용 예시

### Request

```bash
curl -X POST http://localhost:8000/api/v1/classify \
  -F "file=@/path/to/plastic_bottle.jpg"
```

### Response

```json
{
  "success": true,
  "category_key": "plastic",
  "confidence": 0.812,
  "disposal_info": {
    "category_code": "PL",
    "category_name": "플라스틱",
    "sub_categories": ["PET병", "PP", "PE", "PS", "PVC", "기타 플라스틱"],
    "disposal_steps": [
      "내용물을 깨끗이 비우고 물로 헹군다",
      "라벨(비닐 재질)을 제거한다",
      "찌그러뜨려 부피를 줄인다",
      "플라스틱 전용 분리수거함에 배출한다"
    ],
    "collection_bag": "별도 마대 또는 전용 분리수거함 (종량제 봉투 불필요)",
    "collection_day_tip": "지자체별 플라스틱 수거일 확인 (보통 주 1~2회)",
    "fine_if_violated": "혼합 배출, 세척 미이행, 타 항목에 혼입 시 과태료 부과",
    "fine_amount_krw": 100000,
    "tips": ["내용물이 남아있으면 재활용 불가 판정"],
    "recyclable": true,
    "icons": ["♻️", "🧴"]
  },
  "top_predictions": [
    {"label": "plastic bottle or plastic container", "score": 0.812},
    {"label": "plastic bag or vinyl bag", "score": 0.051},
    {"label": "styrofoam packaging", "score": 0.031}
  ],
  "inference_time_ms": 123.4,
  "model_name": "openai/clip-vit-base-patch32",
  "standard_year": 2026
}
```

---

## 🗂️ 지원 분류 카테고리 (2026 기준)

| 코드 | 카테고리 | 재활용 | 과태료 |
|------|----------|--------|--------|
| PL | 🧴 플라스틱 | ✅ | 10만원 |
| GL | 🍶 유리 | ✅ | 10만원 |
| MT | 🥫 캔/고철 | ✅ | 10만원 |
| PA | 📦 종이/박스 | ✅ | 10만원 |
| FW | 🍚 음식물 쓰레기 | ❌ | 10만원 |
| GW | 🗑️ 일반 쓰레기 | ❌ | 10만원 |
| BT | 🔋 폐배터리/전자제품 | ✅ | **30만원** |
| VN | 🛍️ 비닐류 | ✅ | 10만원 |
| SF | 📦 스티로폼 | ✅ | 10만원 |
| CL | 👕 의류/섬유 | ✅ | 10만원 |

> 폐배터리는 화재 위험으로 **과태료 30만원** 적용

---

## 🧪 테스트 실행

```bash
pytest tests/ -v
```

---

## 🧠 ML 파이프라인 구조

```
사용자 이미지 업로드
       │
       ▼
  [파일 검증]  ← 확장자·크기·손상 여부
       │
       ▼
  [PIL 변환]   ← RGB 정규화
       │
       ▼
[CLIP 이미지 임베딩]  ← openai/clip-vit-base-patch32
       │
       ▼
[CLIP 텍스트 임베딩]  ← 11개 도메인 프롬프트 (캐시됨)
       │
       ▼
  [코사인 유사도]
       │
       ▼
  [Softmax 확률]
       │
       ▼
[신뢰도 임계값 검사]  ← 0.15 미만 시 → 일반쓰레기
       │
       ▼
[카테고리 → 배출 DB 조회]
       │
       ▼
   JSON 응답 반환
```

---

## ⚙️ 환경변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `HOST` | `0.0.0.0` | 서버 호스트 |
| `PORT` | `8000` | 서버 포트 |
| `DEBUG` | `false` | 개발 모드 (자동 리로드) |
| `CLIP_MODEL_NAME` | `openai/clip-vit-base-patch32` | Hugging Face 모델 ID |
| `MODEL_CACHE_DIR` | `./models` | 모델 캐시 경로 |
| `MAX_IMAGE_SIZE_MB` | `10` | 업로드 최대 크기 |
| `CONFIDENCE_THRESHOLD` | `0.15` | 분류 신뢰도 임계값 |

---

## 📦 GPU 사용 시 (선택)

PyTorch GPU 버전을 별도 설치하면 추론 속도가 크게 향상됩니다:

```bash
# CUDA 12.1 예시
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

GPU가 감지되면 서버 시작 시 자동으로 CUDA를 사용합니다.

---

## 📄 라이선스

MIT License
