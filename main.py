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

    /* 상단 레오파드/레드 커튼 주름 연출 */
    .cinema-curtain-header {
        background: linear-gradient(180deg, #800a18 0%, #4a020a 70%, transparent 100%);
        border-bottom: 3px solid #d4af37;
        padding: 25px 20px 15px 20px;
        text-align: center;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.8);
        margin-bottom: 25px;
    }

    /* 영화관 타이틀 (골드 네온 서체) */
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
