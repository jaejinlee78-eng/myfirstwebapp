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
    .stApp {
        background-color: #0f1117;
        color: #f9fafb;
    }

    .main-title {
        font-size: 34px;
        font-weight: 800;
        margin-bottom: 6px;
        color: #f9fafb;
        letter-spacing: -0.5px;
    }

    .sub-title {
        font-size: 16px;
        color: #cbd5e1;
        margin-bottom: 28px;
        line-height: 1.6;
    }

    .section-title {
        font-size: 23px;
        font-weight: 800;
        margin-top: 14px;
        margin-bottom: 14px;
        color: #f9fafb;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        border: 1px solid rgba(255, 255, 255, 0.10);
        padding: 20px 22px;
        border-radius: 20px;
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.30);
        min-height: 112px;
    }

    div[data-testid="stMetricLabel"] {
        color: #cbd5e1 !important;
        font-size: 15px;
        font-weight: 700;
    }

    div[data-testid="stMetricLabel"] p {
        color: #cbd5e1 !important;
        font-size: 15px;
        font-weight: 700;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 28px;
        font-weight: 900;
    }

    div[data-testid="stMetricValue"] div {
        color: #ffffff !important;
    }

    hr {
        border-color: rgba(255, 255, 255, 0.12);
        margin-top: 28px;
        margin-bottom: 28px;
    }

    section[data-testid="stSidebar"] {
        background-color: #111827;
    }

    section[data-testid="stSidebar"] * {
        color: #f9fafb;
    }

    .filter-count-box {
        background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
        padding: 14px 16px;
        border-radius: 14px;
        color: #ffffff;
        font-size: 16px;
        font-weight: 800;
        margin-top: 18px;
        margin-bottom: 14px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.25);
    }

    .source-text {
        font-size: 12px;
        color: #94a3b8 !important;
        line-height: 1.5;
        margin-top: 18px;
    }

    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 13px;
        margin-top: 40px;
        padding-top: 18px;
        padding-bottom: 20px;
        border-top: 1px solid rgba(255, 255, 255, 0.12);
    }

    div[data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
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
    data = pd.read_csv(DATA_FILE, encoding="cp949")

    rename_map = {
        "상권_구분_코드_명": "상권유형",
        "상권_코드": "상권코드",
        "상권_코드_명": "상권이름",
        "서비스_업종_코드_명": "업종",
        "당월_매출_금액": "분기매출액",
        "당월_매출_건수": "분기거래건수",
    }

    data = data.rename(columns=rename_map)

    # 혹시 원본 컬럼명에 오타가 있는 경우 방어
    if "당월_매추_건수" in data.columns and "분기거래건수" not in data.columns:
        data = data.rename(columns={"당월_매추_건수": "분기거래건수"})

    numeric_cols = [
        "분기매출액",
        "분기거래건수",
        "남성_매출_금액",
        "여성_매출_금액",
        "연령대_10_매출_금액",
        "연령대_20_매출_금액",
        "연령대_30_매출_금액",
        "연령대_40_매출_금액",
        "연령대_50_매출_금액",
        "연령대_60_이상_매출_금액",
    ]

    for col in numeric_cols:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)

    if "기준_년분기_코드" in data.columns:
        data["기준_년분기_코드"] = data["기준_년분기_코드"].astype(str)

    return data


# =========================================================
# 4. 표시용 함수
# =========================================================
def format_eok(value: float) -> str:
    return f"{value / 100_000_000:,.1f}억 원"


def format_man(value: float) -> str:
    return f"{value / 10_000:,.1f}만 건"


def format_count(value: int) -> str:
    return f"{value:,}개"


def make_label(values: list[str], all_label: str = "전체") -> str:
    if not values:
        return "선택 없음"

    if all_label in values:
        return all_label

    if len(values) <= 3:
        return ", ".join(values)

    return f"{', '.join(values[:3])} 외 {len(values) - 3}개"


# =========================================================
# 5. 제목
# =========================================================
st.markdown(
    '<div class="main-title">🏙️ 서울시 상권분석 대시보드</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="sub-title">
    선택한 분기, 상권유형, 업종 조건을 기준으로 매출 현황과 고객 특성을 확인합니다.
    엑셀 대신 웹앱이라니, 인간 문명도 가끔은 전진합니다.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 6. 데이터 로딩 및 필수 컬럼 검증
# =========================================================
try:
    data = load_data()

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
    "남성_매출_금액",
    "여성_매출_금액",
    "연령대_10_매출_금액",
    "연령대_20_매출_금액",
    "연령대_30_매출_금액",
    "연령대_40_매출_금액",
    "연령대_50_매출_금액",
    "연령대_60_이상_매출_금액",
]

missing_cols = [col for col in required_cols if col not in data.columns]

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
quarter_options = sorted(
    data["기준_년분기_코드"].dropna().unique(),
    key=lambda x: int(x) if str(x).isdigit() else str(x),
)

quarter_select_options = ["전체"] + quarter_options

selected_quarters = st.sidebar.multiselect(
    "📅 분기 선택",
    options=quarter_select_options,
    default=["전체"],
    help="'전체'를 선택하면 모든 분기가 반영됩니다.",
)

# -------------------------
# 필터 2: 상권유형
# -------------------------
market_type_options = sorted(
    data["상권유형"].dropna().unique()
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
)

# -------------------------
# 업종 기본값 계산용 임시 데이터
# 분기 + 상권유형 조건까지만 먼저 반영
# -------------------------
temp_data = data.copy()

if selected_quarters and "전체" not in selected_quarters:
    temp_data = temp_data[
        temp_data["기준_년분기_코드"].isin(selected_quarters)
    ]

if selected_market_types:
    temp_data = temp_data[
        temp_data["상권유형"].isin(selected_market_types)
    ]
else:
    temp_data = temp_data.iloc[0:0]

# -------------------------
# 필터 3: 업종
# -------------------------
industry_options = sorted(
    temp_data["업종"].dropna().unique()
)

default_industries = (
    temp_data
    .groupby("업종", as_index=False)["분기매출액"]
    .sum()
    .sort_values("분기매출액", ascending=False)
    .head(5)["업종"]
    .tolist()
)

industry_filter_key = (
    "industry_filter_"
    + "_".join(selected_quarters if selected_quarters else ["none"])
    + "_"
    + "_".join(selected_market_types if selected_market_types else ["none"])
)

selected_industries = st.sidebar.multiselect(
    "🛍️ 업종",
    options=industry_options,
    default=default_industries,
    key=industry_filter_key,
    help="기본값은 선택된 분기와 상권유형 기준 매출 상위 5개 업종입니다.",
)


# =========================================================
# 8. 최종 필터링 데이터 생성
# =========================================================
filtered_data = data.copy()

if selected_quarters and "전체" not in selected_quarters:
    filtered_data = filtered_data[
        filtered_data["기준_년분기_코드"].isin(selected_quarters)
    ]

if selected_market_types:
    filtered_data = filtered_data[
        filtered_data["상권유형"].isin(selected_market_types)
    ]
else:
    filtered_data = filtered_data.iloc[0:0]

if selected_industries:
    filtered_data = filtered_data[
        filtered_data["업종"].isin(selected_industries)
    ]
else:
    filtered_data = filtered_data.iloc[0:0]


# =========================================================
# 9. 사이드바 선택 현황, 다운로드, 출처
# =========================================================
st.sidebar.divider()

st.sidebar.markdown("### 📌 선택 현황")
st.sidebar.write(f"분기: **{make_label(selected_quarters)}**")
st.sidebar.write(f"상권유형: **{make_label(selected_market_types)}**")
st.sidebar.write(f"업종: **{make_label(selected_industries)}**")

st.sidebar.divider()

st.sidebar.markdown("### 📊 데이터 건수")
st.sidebar.write(f"전체 데이터: **{len(data):,}건**")

st.sidebar.markdown(
    f"""
    <div class="filter-count-box">
    🔎 필터링된 데이터: {len(filtered_data):,}건
    </div>
    """,
    unsafe_allow_html=True,
)

csv_data = filtered_data.to_csv(index=False).encode("cp949", errors="replace")

st.sidebar.download_button(
    label="📥 데이터 다운로드(CSV)",
    data=csv_data,
    file_name="상권분석_필터링데이터.csv",
    mime="text/csv",
    use_container_width=True,
)

st.sidebar.markdown(
    """
    <div class="source-text">
    데이터 출처: 서울 열린데이터광장<br>
    https://data.seoul.go.kr/
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 10. 탭 생성
# =========================================================
sales_tab, customer_tab = st.tabs(["💰 매출 현황", "👥 고객 분석"])


# =========================================================
# 11. 매출 현황 탭
# =========================================================
with sales_tab:
    total_sales = filtered_data["분기매출액"].sum()
    total_transactions = filtered_data["분기거래건수"].sum()
    market_count = filtered_data["상권이름"].nunique(dropna=True)
    industry_count = filtered_data["업종"].nunique(dropna=True)

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
        f"🔎 현재 필터 기준으로 총 **{len(filtered_data):,}건**의 데이터가 반영되었습니다."
    )

    st.divider()

    st.markdown(
        '<div class="section-title">🏆 분기 매출 TOP 10업종</div>',
        unsafe_allow_html=True,
    )

    top10_industry_sales = (
        filtered_data
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
# 12. 고객 분석 탭
# =========================================================
with customer_tab:
    st.markdown('<div class="section-title">👥 고객 분석</div>', unsafe_allow_html=True)

    gender_col, age_col = st.columns([1, 1.35])

    # -------------------------
    # 성별 도넛 차트
    # -------------------------
    with gender_col:
        st.markdown("### 🚻 성별 매출 비중")

        male_sales = filtered_data["남성_매출_금액"].sum()
        female_sales = filtered_data["여성_매출_금액"].sum()
        gender_total_sales = male_sales + female_sales

        gender_data = pd.DataFrame(
            {
                "성별": ["남성", "여성"],
                "매출액": [male_sales, female_sales],
            }
        )

        gender_data["매출액_억원"] = gender_data["매출액"] / 100_000_000

        if gender_total_sales > 0:
            gender_data["비율"] = gender_data["매출액"] / gender_total_sales * 100
        else:
            gender_data["비율"] = 0

        gender_data["비율표시"] = gender_data["비율"].apply(lambda x: f"{x:.1f}%")
        gender_data["라벨"] = gender_data.apply(
            lambda row: f"{row['성별']} {row['비율표시']}",
            axis=1,
        )

        if gender_total_sales <= 0:
            st.warning("⚠️ 선택한 조건에 해당하는 성별 매출 데이터가 없습니다.")

        else:
            donut = (
                alt.Chart(gender_data)
                .mark_arc(
                    innerRadius=70,
                    outerRadius=120,
                )
                .encode(
                    theta=alt.Theta("매출액:Q"),
                    color=alt.Color(
                        "성별:N",
                        legend=alt.Legend(title="성별"),
                    ),
                    tooltip=[
                        alt.Tooltip("성별:N", title="성별"),
                        alt.Tooltip("매출액_억원:Q", title="매출액(억원)", format=",.1f"),
                        alt.Tooltip("비율:Q", title="비율", format=".1f"),
                    ],
                )
            )

            donut_text = (
                alt.Chart(gender_data)
                .mark_text(
                    radius=145,
                    fontSize=14,
                    fontWeight="bold",
                )
                .encode(
                    theta=alt.Theta("매출액:Q"),
                    text=alt.Text("라벨:N"),
                )
            )

            donut_chart = (
                (donut + donut_text)
                .properties(
                    height=360,
                    title="성별 매출 비중",
                )
                .configure_title(
                    fontSize=20,
                    fontWeight="bold",
                    anchor="start",
                )
                .configure_view(
                    strokeWidth=0,
                )
            )

            st.altair_chart(donut_chart, use_container_width=True)

            st.caption(
                f"💡 남성 {male_sales / 100_000_000:,.1f}억 원, "
                f"여성 {female_sales / 100_000_000:,.1f}억 원 기준입니다."
            )

    # -------------------------
    # 연령대 막대 차트
    # -------------------------
    with age_col:
        st.markdown("### 🎂 연령대별 매출")

        age_columns = {
            "10대": "연령대_10_매출_금액",
            "20대": "연령대_20_매출_금액",
            "30대": "연령대_30_매출_금액",
            "40대": "연령대_40_매출_금액",
            "50대": "연령대_50_매출_금액",
            "60대 이상": "연령대_60_이상_매출_금액",
        }

        age_data = pd.DataFrame(
            {
                "연령대": list(age_columns.keys()),
                "매출액": [
                    filtered_data[col].sum()
                    for col in age_columns.values()
                ],
            }
        )

        age_data["매출액_억원"] = age_data["매출액"] / 100_000_000
        age_data["매출액표시"] = age_data["매출액_억원"].apply(lambda x: f"{x:,.1f}억")

        if age_data["매출액"].sum() <= 0:
            st.warning("⚠️ 선택한 조건에 해당하는 연령대 매출 데이터가 없습니다.")

        else:
            age_max_sales = age_data["매출액_억원"].max()
            age_y_max = age_max_sales * 1.18 if age_max_sales > 0 else 1

            age_bar = (
                alt.Chart(age_data)
                .mark_bar(
                    cornerRadiusTopLeft=6,
                    cornerRadiusTopRight=6,
                    size=42,
                )
                .encode(
                    x=alt.X(
                        "연령대:N",
                        sort=list(age_columns.keys()),
                        title=None,
                        axis=alt.Axis(labelAngle=0),
                    ),
                    y=alt.Y(
                        "매출액_억원:Q",
                        title="매출액(억원)",
                        scale=alt.Scale(domain=[0, age_y_max]),
                        axis=alt.Axis(format=",.0f", grid=True),
                    ),
                    tooltip=[
                        alt.Tooltip("연령대:N", title="연령대"),
                        alt.Tooltip("매출액_억원:Q", title="매출액(억원)", format=",.1f"),
                    ],
                )
            )

            age_text = (
                alt.Chart(age_data)
                .mark_text(
                    align="center",
                    baseline="bottom",
                    dy=-5,
                    fontSize=13,
                    fontWeight="bold",
                )
                .encode(
                    x=alt.X("연령대:N", sort=list(age_columns.keys())),
                    y=alt.Y("매출액_억원:Q"),
                    text=alt.Text("매출액표시:N"),
                )
            )

            age_chart = (
                (age_bar + age_text)
                .properties(
                    height=360,
                    title="연령대별 매출액",
                )
                .configure_title(
                    fontSize=20,
                    fontWeight="bold",
                    anchor="start",
                )
                .configure_axis(
                    labelFontSize=12,
                    titleFontSize=13,
                )
                .configure_view(
                    strokeWidth=0,
                )
            )

            st.altair_chart(age_chart, use_container_width=True)

            with st.expander("📋 연령대별 매출 데이터 보기"):
                display_age_data = age_data.copy()
                display_age_data["매출액"] = display_age_data["매출액"].apply(lambda x: f"{x:,.0f}")
                display_age_data["매출액_억원"] = display_age_data["매출액_억원"].apply(lambda x: f"{x:,.1f}")

                st.dataframe(
                    display_age_data[["연령대", "매출액", "매출액_억원"]],
                    use_container_width=True,
                    hide_index=True,
                )


# =========================================================
# 13. 필터 적용 데이터 미리보기
# =========================================================
st.divider()

with st.expander("🧩 필터 적용 데이터 미리보기"):
    st.dataframe(
        filtered_data.head(30),
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 14. 푸터
# =========================================================
st.markdown(
    """
    <div class="footer">
    made by 재진's
    </div>
    """,
    unsafe_allow_html=True,
)
