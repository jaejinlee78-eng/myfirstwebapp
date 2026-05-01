# main.py

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


# =========================================================
# 1. 기본 설정
# =========================================================
st.set_page_config(
    page_title="서울시 상권분석 대시보드",
    page_icon="🏙️",
    layout="wide",
)

DATA_FILE_NAME = "서울시_상권분석서비스_샘플.csv"
DATA_FILE = Path(__file__).parent / DATA_FILE_NAME


# =========================================================
# 2. 스타일
# =========================================================
st.markdown(
    """
    <style>
    .main-title {
        font-size: 34px;
        font-weight: 800;
        margin-bottom: 4px;
    }

    .sub-title {
        font-size: 16px;
        color: #666666;
        margin-bottom: 24px;
    }

    .section-title {
        font-size: 22px;
        font-weight: 700;
        margin-top: 10px;
        margin-bottom: 12px;
    }

    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #eeeeee;
        padding: 18px 20px;
        border-radius: 18px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
    }

    div[data-testid="stMetricLabel"] {
        font-size: 15px;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        font-size: 26px;
        font-weight: 800;
    }

    .small-note {
        font-size: 14px;
        color: #777777;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 3. 데이터 불러오기
# =========================================================
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE, encoding="cp949")

    rename_map = {
        "상권_구분_코드_명": "상권유형",
        "상권_코드": "상권코드",
        "상권_코드_명": "상권이름",
        "서비스_업종_코드_명": "업종",
        "당월_매출_금액": "분기매출액",
        "당월_매출_건수": "분기거래건수",
    }

    df = df.rename(columns=rename_map)

    # 혹시 원본 파일에 오타 컬럼명이 들어간 경우까지 방어
    if "당월_매추_건수" in df.columns and "분기거래건수" not in df.columns:
        df = df.rename(columns={"당월_매추_건수": "분기거래건수"})

    # 필수 숫자열 변환
    for col in ["분기매출액", "분기거래건수"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # 필터용 문자열 처리
    if "기준_년분기_코드" in df.columns:
        df["기준_년분기_코드"] = df["기준_년분기_코드"].astype(str)

    return df


# =========================================================
# 4. 표시용 포맷 함수
# =========================================================
def format_eok(value: float) -> str:
    """원 단위 금액을 억 원 단위로 표기"""
    return f"{value / 100_000_000:,.1f}억 원"


def format_man(value: float) -> str:
    """건수를 만 건 단위로 표기"""
    return f"{value / 10_000:,.1f}만 건"


def format_count(value: int) -> str:
    """개수 표기"""
    return f"{value:,}개"


def make_label(values: list[str], all_label: str = "전체") -> str:
    """선택값을 화면 표시용 문자열로 변환"""
    if not values:
        return "선택 없음"

    if all_label in values:
        return all_label

    if len(values) <= 3:
        return ", ".join(values)

    return f"{', '.join(values[:3])} 외 {len(values) - 3}개"


# =========================================================
# 5. 화면 제목
# =========================================================
st.markdown(
    '<div class="main-title">🏙️ 서울시 상권분석 대시보드</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="sub-title">
    선택한 조건 기준으로 상권 매출, 거래건수, 업종별 매출 TOP 10을 확인합니다.
    엑셀을 열지 않아도 되니 인류 문명은 아주 조금 전진했습니다.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 6. 데이터 로딩 및 검증
# =========================================================
try:
    df = load_data()

except FileNotFoundError:
    st.error(
        f"❌ 데이터 파일을 찾을 수 없습니다.\n\n"
        f"`main.py`와 같은 폴더에 `{DATA_FILE_NAME}` 파일을 넣어주세요."
    )
    st.stop()

except UnicodeDecodeError:
    st.error(
        "❌ 파일 인코딩을 읽는 중 문제가 발생했습니다. "
        "현재 코드는 `cp949` 인코딩 기준입니다."
    )
    st.stop()

required_cols = [
    "기준_년분기_코드",
    "상권유형",
    "분기매출액",
    "분기거래건수",
    "상권이름",
    "업종",
]

missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    st.error(f"❌ 필요한 열이 없습니다: {', '.join(missing_cols)}")
    st.stop()


# =========================================================
# 7. 사이드바 데이터 필터
# =========================================================
st.sidebar.header("🧰 데이터 필터")

# -------------------------
# 필터 1: 분기 선택
# -------------------------
quarters = sorted(
    df["기준_년분기_코드"].dropna().unique(),
    key=lambda x: int(x) if str(x).isdigit() else str(x),
)

quarter_options = ["전체"] + quarters

selected_quarters = st.sidebar.multiselect(
    "📅 분기 선택",
    options=quarter_options,
    default=["전체"],
    help="'전체'를 선택하면 모든 분기가 반영됩니다.",
)

# 전체 선택 또는 아무것도 선택하지 않은 경우 전체 데이터 기준
if not selected_quarters or "전체" in selected_quarters:
    quarter_filtered_df = df.copy()
else:
    quarter_filtered_df = df[
        df["기준_년분기_코드"].isin(selected_quarters)
    ].copy()


# -------------------------
# 필터 2: 상권유형
# -------------------------
market_type_options = sorted(
    quarter_filtered_df["상권유형"].dropna().unique()
)

default_market_types = [
    market_type
    for market_type in ["골목상권", "전통시장"]
    if market_type in market_type_options
]

selected_market_types = st.sidebar.multiselect(
    "🏘️ 상권유형",
    options=market_type_options,
    default=default_market_types,
    help="기본값은 골목상권과 전통시장입니다.",
)

if selected_market_types:
    market_type_filtered_df = quarter_filtered_df[
        quarter_filtered_df["상권유형"].isin(selected_market_types)
    ].copy()
else:
    market_type_filtered_df = quarter_filtered_df.iloc[0:0].copy()


# -------------------------
# 필터 3: 업종
# -------------------------
industry_options = sorted(
    market_type_filtered_df["업종"].dropna().unique()
)

top5_industries = (
    market_type_filtered_df
    .groupby("업종", as_index=False)["분기매출액"]
    .sum()
    .sort_values("분기매출액", ascending=False)
    .head(5)["업종"]
    .tolist()
)

# 앞선 필터가 바뀌면 업종 기본값도 다시 상위 5개로 잡히도록 key 구성
industry_filter_key = (
    "industry_filter_"
    + "_".join(selected_quarters)
    + "_"
    + "_".join(selected_market_types)
)

selected_industries = st.sidebar.multiselect(
    "🛍️ 업종",
    options=industry_options,
    default=top5_industries,
    key=industry_filter_key,
    help="기본값은 선택된 분기와 상권유형 기준 매출 상위 5개 업종입니다.",
)

if selected_industries:
    filtered_df = market_type_filtered_df[
        market_type_filtered_df["업종"].isin(selected_industries)
    ].copy()
else:
    filtered_df = market_type_filtered_df.iloc[0:0].copy()


# -------------------------
# 사이드바 데이터 정보
# -------------------------
st.sidebar.divider()

st.sidebar.markdown("### 📦 선택 현황")
st.sidebar.write(f"분기: **{make_label(selected_quarters)}**")
st.sidebar.write(f"상권유형: **{make_label(selected_market_types)}**")
st.sidebar.write(f"업종: **{make_label(selected_industries)}**")

st.sidebar.divider()

st.sidebar.markdown("### 📊 데이터 건수")
st.sidebar.write(f"전체 데이터: **{len(df):,}건**")
st.sidebar.write(f"필터 적용 데이터: **{len(filtered_df):,}건**")


# =========================================================
# 8. 핵심 메트릭
# =========================================================
total_sales = filtered_df["분기매출액"].sum()
total_transactions = filtered_df["분기거래건수"].sum()
market_count = filtered_df["상권이름"].nunique(dropna=True)
industry_count = filtered_df["업종"].nunique(dropna=True)

st.markdown('<div class="section-title">📌 핵심 지표</div>', unsafe_allow_html=True)

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

st.info(
    f"🔎 현재 필터 기준으로 총 **{len(filtered_df):,}건**의 데이터가 반영되었습니다."
)


# =========================================================
# 9. 업종별 분기 매출 TOP 10
# =========================================================
st.divider()

st.markdown(
    '<div class="section-title">🏆 분기 매출 TOP 10업종</div>',
    unsafe_allow_html=True,
)

top10_industry_sales = (
    filtered_df
    .groupby("업종", as_index=False)["분기매출액"]
    .sum()
    .sort_values("분기매출액", ascending=False)
    .head(10)
)

top10_industry_sales["분기매출액_억원"] = (
    top10_industry_sales["분기매출액"] / 100_000_000
)

top10_industry_sales["매출액표시"] = top10_industry_sales["분기매출액_억원"].apply(
    lambda x: f"{x:,.1f}억"
)

if top10_industry_sales.empty:
    st.warning("⚠️ 선택한 조건에 해당하는 업종 매출 데이터가 없습니다.")

else:
    max_sales_eok = top10_industry_sales["분기매출액_억원"].max()
    x_max = max_sales_eok * 1.18 if max_sales_eok > 0 else 1

    bar = (
        alt.Chart(top10_industry_sales)
        .mark_bar(
            cornerRadiusEnd=6,
            size=24,
        )
        .encode(
            x=alt.X(
                "분기매출액_억원:Q",
                title="매출액(억원)",
                scale=alt.Scale(domain=[0, x_max]),
                axis=alt.Axis(format=",.0f", grid=True),
            ),
            y=alt.Y(
                "업종:N",
                sort="-x",
                title=None,
                axis=alt.Axis(labelLimit=220),
            ),
            tooltip=[
                alt.Tooltip("업종:N", title="업종"),
                alt.Tooltip("분기매출액_억원:Q", title="매출액(억원)", format=",.1f"),
            ],
        )
    )

    text = (
        alt.Chart(top10_industry_sales)
        .mark_text(
            align="left",
            baseline="middle",
            dx=7,
            fontSize=13,
            fontWeight="bold",
        )
        .encode(
            x=alt.X("분기매출액_억원:Q"),
            y=alt.Y("업종:N", sort="-x"),
            text=alt.Text("매출액표시:N"),
        )
    )

    chart = (
        (bar + text)
        .properties(
            height=430,
            title="분기 매출 TOP 10업종",
        )
        .configure_title(
            fontSize=22,
            fontWeight="bold",
            anchor="start",
            offset=12,
        )
        .configure_axis(
            labelFontSize=12,
            titleFontSize=13,
        )
        .configure_view(
            strokeWidth=0,
        )
    )

    st.altair_chart(chart, use_container_width=True)

    with st.expander("📋 TOP 10 업종 데이터 보기"):
        display_top10 = top10_industry_sales.copy()
        display_top10["분기매출액"] = display_top10["분기매출액"].apply(lambda x: f"{x:,.0f}")
        display_top10["분기매출액_억원"] = display_top10["분기매출액_억원"].apply(lambda x: f"{x:,.1f}")

        st.dataframe(
            display_top10[["업종", "분기매출액", "분기매출액_억원"]],
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# 10. 데이터 미리보기
# =========================================================
st.divider()

with st.expander("🧩 필터 적용 데이터 미리보기"):
    st.dataframe(
        filtered_df.head(30),
        use_container_width=True,
        hide_index=True,
    )
