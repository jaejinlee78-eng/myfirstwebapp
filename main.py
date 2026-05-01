# main.py

from pathlib import Path

import pandas as pd
import streamlit as st


# =========================
# 기본 설정
# =========================
st.set_page_config(
    page_title="서울시 상권분석 대시보드",
    page_icon="🏙️",
    layout="wide",
)

DATA_FILE = Path(__file__).parent / "서울시_상권분석서비스_샘플.csv"


# =========================
# 데이터 불러오기
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE, encoding="cp949")

    # 열 이름 변경
    rename_map = {
        "상권_구분_코드_명": "상권유형",
        "상권_코드": "상권코드",
        "상권_코드_명": "상권이름",
        "서비스_업종_코드_명": "업종",
        "당월_매출_금액": "분기매출액",
        "당월_매출_건수": "분기거래건수",
    }

    df = df.rename(columns=rename_map)

    # 숫자형 변환
    numeric_cols = ["분기매출액", "분기거래건수"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 분기 코드는 필터용으로 문자열 처리
    if "기준_년분기_코드" in df.columns:
        df["기준_년분기_코드"] = df["기준_년분기_코드"].astype(str)

    return df


# =========================
# 유틸 함수
# =========================
def format_eok(value):
    """원 단위 금액을 억 원 단위로 변환"""
    return f"{value / 100_000_000:,.1f}억 원"


def format_man(value):
    """건수를 만 건 단위로 변환"""
    return f"{value / 10_000:,.1f}만 건"


def format_count(value):
    """개수 표기"""
    return f"{value:,}개"


# =========================
# 앱 본문
# =========================
st.title("🏙️ 서울시 상권분석 대시보드")
st.caption("분기별 상권 매출과 거래 규모를 한눈에 보는 화면입니다. 숫자는 알아서 쉼표를 넣었습니다. 인간이 보기 편하라고요.")

try:
    df = load_data()

except FileNotFoundError:
    st.error(
        f"❌ 데이터 파일을 찾을 수 없습니다.\n\n"
        f"`main.py`와 같은 폴더에 `{DATA_FILE.name}` 파일이 있는지 확인해주세요."
    )
    st.stop()

except UnicodeDecodeError:
    st.error(
        "❌ 파일 인코딩을 읽는 중 문제가 발생했습니다. "
        "현재 코드는 `cp949` 인코딩 기준입니다."
    )
    st.stop()


# =========================
# 필수 컬럼 확인
# =========================
required_cols = [
    "기준_년분기_코드",
    "분기매출액",
    "분기거래건수",
    "상권이름",
    "업종",
]

missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    st.error(f"❌ 필요한 열이 없습니다: {', '.join(missing_cols)}")
    st.stop()


# =========================
# 분기 필터
# =========================
st.sidebar.header("🔎 필터")

quarters = sorted(
    df["기준_년분기_코드"].dropna().unique(),
    key=lambda x: int(x) if str(x).isdigit() else str(x),
)

quarter_options = ["전체"] + quarters

selected_quarter = st.sidebar.selectbox(
    "분기 선택",
    quarter_options,
    index=0,
)

if selected_quarter == "전체":
    filtered_df = df.copy()
else:
    filtered_df = df[df["기준_년분기_코드"] == selected_quarter].copy()


# =========================
# 메트릭 계산
# =========================
total_sales = filtered_df["분기매출액"].sum()
total_transactions = filtered_df["분기거래건수"].sum()
market_count = filtered_df["상권이름"].nunique(dropna=True)
industry_count = filtered_df["업종"].nunique(dropna=True)


# =========================
# 메트릭 표시
# =========================
st.subheader("📌 핵심 지표")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="💰 총분기 매출액",
        value=format_eok(total_sales),
    )

with col2:
    st.metric(
        label="🧾 총분기 거래건수",
        value=format_man(total_transactions),
    )

with col3:
    st.metric(
        label="📍 분석상권수",
        value=format_count(market_count),
    )

with col4:
    st.metric(
        label="🛍️ 업종 종류",
        value=format_count(industry_count),
    )


# =========================
# 선택 정보 표시
# =========================
st.divider()

if selected_quarter == "전체":
    st.info(f"🌐 현재 전체 분기 기준으로 분석 중입니다. 총 {len(filtered_df):,}건의 데이터가 반영되었습니다.")
else:
    st.info(f"📅 현재 `{selected_quarter}` 분기 기준으로 분석 중입니다. 총 {len(filtered_df):,}건의 데이터가 반영되었습니다.")


# =========================
# 데이터 미리보기
# =========================
with st.expander("🧩 데이터 미리보기"):
    st.dataframe(filtered_df.head(20), use_container_width=True)
