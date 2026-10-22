# 어제의 박스오피스 — KOBIS 일별 박스오피스 API (레드 커튼 극장 테마)
import datetime
import requests
import pandas as pd
import streamlit as st

# 페이지 세팅
st.set_page_config(page_title="시네마 박스오피스", page_icon="🎬", layout="wide")

# ----------------------------------------------------
# 🎭 영화관 레드 커튼 & 시네마 럭셔리 스타일링
# ----------------------------------------------------
st.markdown("""
    <style>
    /* 전체 배경: 깊은 다크 레드 & 클래식 붉은 극장 느낌 */
    .stApp {
        background: radial-gradient(circle at center, #2b080c 0%, #0f0203 100%);
        color: #f8fafc;
    }

    /* 상단 커튼 주름 연출 */
    .cinema-curtain-header {
        background: linear-gradient(180deg, #800a18 0%, #4a020a 70%, transparent 100%);
        border-bottom: 3px solid #d4af37;
        padding: 25px 20px 15px 20px;
        text-align: center;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.8);
        margin-bottom: 25px;
    }

    /* 영화관 타이틀 */
    .cinema-main-title {
        font-family: 'Impact', 'Arial Black', sans-serif;
        font-size: 2.8rem;
        letter-spacing: 4px;
        color: #f59e0b;
        text-shadow: 0 0 12px rgba(245, 158, 11, 0.6), 2px 2px 4px #000000;
        margin: 0;
    }

    /* 곡선 은빛 시네마 스크린 */
    .cinema-screen-box {
        position: relative;
        background: linear-gradient(180deg, #ffffff 0%, #e2e8f0 85%, #cbd5e1 100%);
        border-radius: 16px 16px 80px 80px / 16px 16px 30px 30px;
        padding: 35px 20px 45px 20px;
        color: #0f172a;
        text-align: center;
        box-shadow: 0 0 50px rgba(255, 255, 255, 0.35), inset 0 -8px 20px rgba(0,0,0,0.25);
        border: 4px solid #f1f5f9;
        margin: 20px 0 30px 0;
    }

    .screen-badge {
        display: inline-block;
        background-color: #dc2626;
        color: #ffffff;
        font-weight: 800;
        font-size: 0.85rem;
        padding: 4px 14px;
        border-radius: 20px;
        letter-spacing: 2px;
        margin-bottom: 10px;
    }

    .screen-movie-title {
        font-size: 2.5rem;
        font-weight: 900;
        color: #020617;
        margin-top: 5px;
        word-break: keep-all;
    }

    /* 위젯 카드 스타일 */
    div[data-testid="stMetric"] {
        background: rgba(45, 10, 15, 0.7);
        border: 1px solid #7f1d1d;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }

    div[data-testid="stMetricLabel"] {
        color: #fca5a5 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 800;
    }
    </style>
""", unsafe_allow_html=True)

API_URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
    "boxoffice/searchDailyBoxOfficeList.json"
)

# 서버 시간대와 관계없이 한국 시간(UTC+9) 기준으로 어제를 계산합니다.
KST = datetime.timezone(datetime.timedelta(hours=9))
today_kst = datetime.datetime.now(KST).date()
yesterday = today_kst - datetime.timedelta(days=1)

# 🎭 상단 극장 레드 커튼 헤더
st.markdown("""
    <div class="cinema-curtain-header">
        <h1 class="cinema-main-title">🍿 CINEMA BOX OFFICE 🍿</h1>
        <p style="color: #fef08a; margin-top: 8px; font-weight: 500;">
            어제의 상영작 순위와 관객 수를 확인하세요
        </p>
    </div>
""", unsafe_allow_html=True)

selected_date = st.date_input(
    "📅 상영 날짜 선택 (최대 어제까지 선택 가능)",
    value=yesterday,
    min_value=
