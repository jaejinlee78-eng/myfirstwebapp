# =========================================================
# 2. 스타일
# =========================================================
st.markdown(
    """
    <style>
    /* 전체 배경과 기본 글자 */
    .stApp {
        background-color: #0f1117;
        color: #f9fafb;
    }

    /* 제목 */
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

    /* 메트릭 카드 */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        border: 1px solid rgba(255, 255, 255, 0.10);
        padding: 20px 22px;
        border-radius: 20px;
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.30);
        min-height: 112px;
    }

    /* 메트릭 라벨 */
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

    /* 메트릭 값 */
    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 28px;
        font-weight: 900;
    }

    div[data-testid="stMetricValue"] div {
        color: #ffffff !important;
    }

    /* 안내 박스 */
    div[data-testid="stAlert"] {
        border-radius: 14px;
    }

    /* 구분선 */
    hr {
        border-color: rgba(255, 255, 255, 0.12);
        margin-top: 28px;
        margin-bottom: 28px;
    }

    /* 사이드바 */
    section[data-testid="stSidebar"] {
        background-color: #111827;
    }

    section[data-testid="stSidebar"] * {
        color: #f9fafb;
    }

    /* 데이터프레임 영역 */
    div[data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
    }

    .small-note {
        font-size: 14px;
        color: #94a3b8;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
