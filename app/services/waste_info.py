"""
2026년 한국 분리배출 기준 데이터베이스
환경부 고시 및 지자체 조례 기반
"""
from typing import TypedDict


class WasteCategory(TypedDict):
    category_code: str
    category_name: str
    sub_categories: list[str]
    disposal_steps: list[str]
    collection_bag: str
    collection_day_tip: str
    fine_if_violated: str
    fine_amount_krw: int
    tips: list[str]
    recyclable: bool
    icons: list[str]


# ─────────────────────────────────────────────
# 2026 한국 분리배출 기준 데이터베이스
# ─────────────────────────────────────────────
WASTE_DATABASE: dict[str, WasteCategory] = {

    "plastic": {
        "category_code": "PL",
        "category_name": "플라스틱",
        "sub_categories": ["PET병", "PP", "PE", "PS", "PVC", "기타 플라스틱"],
        "disposal_steps": [
            "내용물을 깨끗이 비우고 물로 헹군다",
            "라벨(비닐 재질)을 제거한다",
            "찌그러뜨려 부피를 줄인다",
            "플라스틱 전용 분리수거함에 배출한다",
            "이물질(음식물 등)이 심하게 묻은 경우 일반쓰레기로 배출",
        ],
        "collection_bag": "별도 마대 또는 전용 분리수거함 (종량제 봉투 불필요)",
        "collection_day_tip": "지자체별 플라스틱 수거일 확인 (보통 주 1~2회)",
        "fine_if_violated": "혼합 배출, 세척 미이행, 타 항목에 혼입 시 과태료 부과",
        "fine_amount_krw": 100000,
        "tips": [
            "내용물이 남아있으면 재활용 불가 판정",
            "색깔이 진한 PET는 무색 PET와 분리 권장",
            "플라스틱 컵 홀더는 종이·비닐·플라스틱 분리 후 각각 배출",
            "2026년부터 PVC 재질 장난감·파이프는 별도 수거거점 이용",
        ],
        "recyclable": True,
        "icons": ["♻️", "🧴"],
    },

    "glass": {
        "category_code": "GL",
        "category_name": "유리",
        "sub_categories": ["소주병", "맥주병", "와인병", "유리컵", "판유리(소량)"],
        "disposal_steps": [
            "내용물을 완전히 비운다",
            "뚜껑(금속·플라스틱)을 분리하여 각각 배출",
            "깨진 유리는 두꺼운 신문지나 종이박스로 감싸고 '깨진 유리'라고 표기",
            "소주·맥주 공병은 빈용기보증금(공병 보증금) 반환 가능",
            "유리 전용 수거함 또는 거점수거함에 배출",
        ],
        "collection_bag": "별도 유리 전용 수거함 (종량제 봉투 불필요)",
        "collection_day_tip": "무거우므로 지자체 거점 수거함 이용 권장",
        "fine_if_violated": "깨진 유리 미포장 배출, 혼합 배출 시 과태료",
        "fine_amount_krw": 100000,
        "tips": [
            "소주·맥주병은 슈퍼마켓·편의점·마트에서 공병 환불 가능",
            "인테리어용 판유리·거울은 대형 폐기물 신고 후 배출",
            "크리스탈·도자기는 유리류 아님 → 일반쓰레기",
            "형광등·백열전구는 유리 아님 → 전용 수거함 이용",
        ],
        "recyclable": True,
        "icons": ["🍶", "♻️"],
    },

    "metal": {
        "category_code": "MT",
        "category_name": "캔 / 고철",
        "sub_categories": ["알루미늄캔", "철캔", "부탄가스통", "스테인리스"],
        "disposal_steps": [
            "내용물을 완전히 비우고 물로 헹군다",
            "부탄가스·스프레이는 반드시 구멍을 뚫어 잔여가스 완전 제거 후 배출",
            "캔을 찌그러뜨려 부피를 줄인다",
            "고철(냄비·철사 등)은 끈으로 묶거나 박스에 담아 배출",
            "캔류 전용 분리수거함에 배출",
        ],
        "collection_bag": "별도 캔 전용 분리수거함 (종량제 봉투 불필요)",
        "collection_day_tip": "알루미늄캔은 고부가 재활용 품목 — 거점수거함 우선 이용",
        "fine_if_violated": "가스 미제거 배출, 혼합 배출 시 과태료 및 안전사고 책임",
        "fine_amount_krw": 100000,
        "tips": [
            "부탄가스통 구멍 미뚫고 배출 시 화재 위험 및 과태료 100,000원",
            "알루미늄 호일은 캔류 아님 → 일반쓰레기",
            "냄비·프라이팬 등 대형 고철은 고철 전문 수집소 이용",
            "2026년부터 알루미늄캔 보증금 환경부담금 시범 적용 지역 확대",
        ],
        "recyclable": True,
        "icons": ["🥫", "♻️"],
    },

    "paper": {
        "category_code": "PA",
        "category_name": "종이 / 박스",
        "sub_categories": ["신문지", "책·잡지", "골판지박스", "종이팩(우유·주스)"],
        "disposal_steps": [
            "테이프·스테이플러침·비닐창 등 이물질 제거",
            "박스는 접어서 납작하게 만든 뒤 끈으로 묶는다",
            "종이팩(우유·두유 등)은 내부를 헹구고 펼쳐 말린 뒤 종이팩 전용함에 배출 (일반 종이류와 분리!)",
            "신문지·책은 묶어서 종이류 수거함 또는 끈으로 묶어 배출",
            "영수증(감열지)·코팅지·방수지는 일반쓰레기로 배출",
        ],
        "collection_bag": "끈으로 묶어 배출 (종량제 봉투 불필요)",
        "collection_day_tip": "골판지 박스는 비 오는 날 배출 금지 (재활용 불가)",
        "fine_if_violated": "테이프 미제거, 비닐·스티로폼 혼입, 우천 시 배출 시 과태료",
        "fine_amount_krw": 100000,
        "tips": [
            "종이팩은 일반 종이와 반드시 분리 배출 (별도 수거함)",
            "택배박스 스티커·에어캡·비닐봉투는 제거 후 각각 분리",
            "감열지 영수증은 재활용 불가 (BPA 함유) → 종량제 봉투",
            "2026년 종이팩 전용 수거함 전국 주민센터 확대 설치",
        ],
        "recyclable": True,
        "icons": ["📦", "♻️"],
    },

    "food_waste": {
        "category_code": "FW",
        "category_name": "음식물 쓰레기",
        "sub_categories": ["채소류", "과일류", "육류", "어패류", "남은 음식"],
        "disposal_steps": [
            "물기를 최대한 제거한다 (30% 이상 무게 감소 효과)",
            "딱딱한 뼈·패각류·복숭아씨 등 음식물쓰레기 불가 항목 제거",
            "음식물 전용 종량제 봉투 또는 RFID 납부필증 부착 용기에 담아 배출",
            "음식물 전용 수거함에 배출 (일반 쓰레기통 혼입 금지)",
            "배출 시간 준수 (보통 저녁 6시 ~ 익일 새벽 3시)",
        ],
        "collection_bag": "음식물 전용 종량제 봉투 (지자체별 다름) 또는 RFID 전용용기",
        "collection_day_tip": "여름철 악취 방지를 위해 야간에 배출 권장",
        "fine_if_violated": "일반 종량제 봉투에 음식물 배출, 무단투기 시 과태료",
        "fine_amount_krw": 100000,
        "tips": [
            "뼈·조개껍데기·복숭아씨·계란껍데기는 음식물 쓰레기 아님 → 일반쓰레기",
            "물기 제거만 잘해도 음식물 쓰레기 처리비용 크게 감소",
            "2026년 음식물 감량기(분쇄형) 인증 제품은 씽크대 배출 허용 지역 확대",
            "RFID 계량 아파트는 kg당 과금이므로 물기 제거 필수",
        ],
        "recyclable": False,
        "icons": ["🍚", "🗑️"],
    },

    "general_waste": {
        "category_code": "GW",
        "category_name": "일반 쓰레기",
        "sub_categories": ["오염된 포장재", "복합재질 용기", "고무제품", "나무젓가락"],
        "disposal_steps": [
            "분리배출이 불가능한 쓰레기를 확인한다",
            "지자체 규격 종량제 봉투에 담는다",
            "봉투를 꽉 밀봉한다",
            "지정된 장소·시간에 배출한다",
        ],
        "collection_bag": "지자체 규격 종량제 봉투 (크기: 5L / 10L / 20L / 30L / 50L 등)",
        "collection_day_tip": "수거일 전날 밤 또는 당일 아침에 배출",
        "fine_if_violated": "종량제 봉투 미사용 배출, 타인 봉투 도용 시 과태료",
        "fine_amount_krw": 100000,
        "tips": [
            "이물질이 많이 묻어 세척이 불가한 용기는 일반쓰레기로",
            "기저귀·생리대는 일반쓰레기 (개인 위생용품)",
            "도자기·크리스탈·거울 조각은 신문지에 감싸 일반쓰레기",
            "종량제 봉투 미구매 배출 적발 시 100,000원 ~ 300,000원",
        ],
        "recyclable": False,
        "icons": ["🗑️"],
    },

    "battery": {
        "category_code": "BT",
        "category_name": "폐배터리 / 전자제품",
        "sub_categories": ["건전지", "충전지(Li-ion)", "납축전지", "소형가전", "휴대폰"],
        "disposal_steps": [
            "건전지·충전지는 전용 수거함(편의점·마트·주민센터)에 배출",
            "리튬이온 배터리(스마트폰·노트북)는 반드시 방전 후 테이프로 단자 절연",
            "납축전지(자동차)는 자동차 정비소 또는 폐배터리 수집 업체에 인계",
            "소형 가전(믹서기·헤어드라이기)은 소형 폐가전 수거함 이용",
            "절대 일반쓰레기·화재 위험 장소에 배출 금지",
        ],
        "collection_bag": "전용 수거함 배출 (종량제 봉투 사용 불가)",
        "collection_day_tip": "편의점·대형마트·주민센터·지하철역 전용 수거함 상시 운영",
        "fine_if_violated": "일반쓰레기 혼입 배출, 무단 투기 시 과태료 및 환경부담금",
        "fine_amount_krw": 300000,
        "tips": [
            "리튬배터리 무단투기 화재 시 손해배상 및 형사처벌 가능",
            "전기차 배터리는 제조사·딜러에 반납 의무화(2025~)",
            "소형 폐가전 무상방문수거 서비스: 한국전자제품자원순환공제조합",
            "휴대폰 배터리 분리 어려운 경우 통째로 전용 수거함 투입 가능",
        ],
        "recyclable": True,
        "icons": ["🔋", "⚡"],
    },

    "vinyl": {
        "category_code": "VN",
        "category_name": "비닐류",
        "sub_categories": ["비닐봉지", "과자봉지", "랩", "에어캡(뽁뽁이)", "위생봉지"],
        "disposal_steps": [
            "내용물을 비우고 이물질을 제거한다",
            "물로 가볍게 헹궈 오염을 제거한다",
            "비닐류 전용 수거함 또는 투명 비닐봉지에 모아 배출",
            "심하게 오염된 비닐(기름·음식물)은 종량제 봉투로 배출",
        ],
        "collection_bag": "투명 비닐봉지에 모아 배출 (종량제 봉투 불필요)",
        "collection_day_tip": "비닐류는 바람에 날리지 않도록 묶어서 배출",
        "fine_if_violated": "음식물 오염 비닐 혼입, 종량제 봉투에 대량 혼입 시 과태료",
        "fine_amount_krw": 100000,
        "tips": [
            "검정 비닐봉지에 담아 배출하면 내용물 확인 불가로 일반쓰레기 처리",
            "에어캡(뽁뽁이)은 비닐류로 배출 가능",
            "2026년부터 커피숍 1회용 컵 홀더(비닐 라벨) 분리 배출 의무화",
            "생선·육류 포장 비닐은 세척 후 배출",
        ],
        "recyclable": True,
        "icons": ["🛍️", "♻️"],
    },

    "styrofoam": {
        "category_code": "SF",
        "category_name": "스티로폼",
        "sub_categories": ["택배 완충재", "컵라면 용기", "과일 포장재"],
        "disposal_steps": [
            "테이프·비닐·이물질을 완전히 제거한다",
            "이물질 없는 흰색 스티로폼만 전용 수거함에 배출 가능",
            "색깔 인쇄된 스티로폼(과일 포장망 포함)은 전용 수거함 확인",
            "오염·음식물 흔적이 있으면 종량제 봉투로 배출",
        ],
        "collection_bag": "스티로폼 전용 수거함 또는 묶어서 배출",
        "collection_day_tip": "파손 시 작게 잘라 묶어 배출 (부피 줄이기)",
        "fine_if_violated": "이물질 미제거, 혼합 배출 시 과태료",
        "fine_amount_krw": 100000,
        "tips": [
            "컵라면 용기는 깨끗하게 씻어 이물질 제거 후 배출",
            "2026년부터 EPS 재활용 품질 강화로 테이프 잔류 시 반려",
            "검정·유색 스티로폼은 재활용 불가 → 종량제 봉투",
        ],
        "recyclable": True,
        "icons": ["📦", "♻️"],
    },

    "clothing": {
        "category_code": "CL",
        "category_name": "의류 / 섬유",
        "sub_categories": ["헌옷", "신발", "가방", "이불·담요(소형)"],
        "disposal_steps": [
            "세탁 후 깨끗한 상태로 준비",
            "헌옷 수거함(아파트 단지·주민센터·마트 앞)에 배출",
            "심하게 오염·파손된 의류는 종량제 봉투로 배출",
            "이불·담요는 지자체 대형폐기물 신고 또는 헌옷 수거함(대형) 이용",
        ],
        "collection_bag": "헌옷 전용 수거함 (비닐봉지에 넣어 투입)",
        "collection_day_tip": "헌옷 수거함은 비가 새는 경우 있으므로 비닐봉지 포장 권장",
        "fine_if_violated": "혼합 배출, 수거함 주변 무단투기 시 과태료",
        "fine_amount_krw": 100000,
        "tips": [
            "아직 입을 수 있는 옷은 당근마켓·아름다운가게 등 나눔 우선",
            "신발·가방도 헌옷 수거함에 투입 가능 (지자체마다 상이)",
            "이불·베개는 대형 폐기물 신고 필요 (별도 스티커 구매)",
        ],
        "recyclable": True,
        "icons": ["👕", "♻️"],
    },
}


# CLIP 모델용 영어 프롬프트 → 한국 카테고리 매핑
CLIP_LABEL_MAP: dict[str, str] = {
    "plastic bottle or plastic container":      "plastic",
    "glass bottle or glass jar":               "glass",
    "aluminum can or metal can":               "metal",
    "cardboard box or paper":                  "paper",
    "newspaper or magazine":                   "paper",
    "food waste or leftover food":             "food_waste",
    "battery or electronic device":            "battery",
    "plastic bag or vinyl bag":                "vinyl",
    "styrofoam packaging":                     "styrofoam",
    "clothing or fabric or shoes":             "clothing",
    "trash or garbage or non-recyclable waste": "general_waste",
}


def get_waste_info(category_key: str) -> WasteCategory | None:
    """카테고리 키로 배출 정보 조회"""
    return WASTE_DATABASE.get(category_key)


def get_all_categories() -> list[dict]:
    """전체 카테고리 목록 반환"""
    return [
        {
            "key": k,
            "code": v["category_code"],
            "name": v["category_name"],
            "recyclable": v["recyclable"],
            "icons": v["icons"],
        }
        for k, v in WASTE_DATABASE.items()
    ]


def get_clip_labels() -> list[str]:
    """CLIP 모델에 입력할 영어 레이블 반환"""
    return list(CLIP_LABEL_MAP.keys())


def map_clip_label_to_category(clip_label: str) -> str:
    """CLIP 예측 레이블을 내부 카테고리 키로 변환"""
    return CLIP_LABEL_MAP.get(clip_label, "general_waste")
