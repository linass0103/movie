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
st.markdown(
    """
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
    """,
    unsafe_allow_html=True
)

API_URL = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
    "boxoffice/searchDailyBoxOfficeList.json"
)

# 서버 시간대와 관계없이 한국 시간(UTC+9) 기준으로 어제를 계산합니다.
KST = datetime.timezone(datetime.timedelta(hours=9))
today_kst = datetime.datetime.now(KST).date()
yesterday = today_kst - datetime.timedelta(days=1)

# 🎭 상단 극장 레드 커튼 헤더
st.markdown(
    """
    <div class="cinema-curtain-header">
        <h1 class="cinema-main-title">🍿 CINEMA BOX OFFICE 🍿</h1>
        <p style="color: #fef08a; margin-top: 8px; font-weight: 500;">
            어제의 상영작 순위와 관객 수를 확인하세요
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

selected_date = st.date_input(
    "📅 상영 날짜 선택 (최대 어제까지 선택 가능)",
    value=yesterday,
    min_value=datetime.date(2004, 1, 1),
    max_value=yesterday,
    format="YYYY/MM/DD"
)
target_dt = selected_date.strftime("%Y%m%d")
display_date = selected_date.strftime("%Y년 %m월 %d일")

# Secrets 인증키 불러오기
try:
    API_KEY = st.secrets["KOBIS_KEY"]
except Exception:
    st.error("🔐 KOBIS 인증키를 찾을 수 없습니다.")
    st.markdown("Streamlit Cloud의 **Settings → Secrets**에 `KOBIS_KEY`가 등록되어 있는지 확인하세요.")
    st.code('KOBIS_KEY = "발급받은_인증키"', language="toml")
    st.stop()


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_boxoffice(date_text, api_key):
    """KOBIS API를 호출해 JSON 응답을 가져옵니다."""
    response = requests.get(
        API_URL,
        params={"key": api_key, "targetDt": date_text},
        timeout=20
    )
    response.raise_for_status()
    return response.json()


# API 데이터 요청
try:
    with st.spinner("📽️ 영사기 작동 중... 영화 데이터를 불러옵니다"):
        data = fetch_boxoffice(target_dt, str(API_KEY).strip())
except requests.exceptions.Timeout:
    st.error("⏱️ KOBIS 서버 응답 시간이 초과되었습니다.")
    st.info("인터넷 연결을 확인하고 잠시 후 새로고침해 주세요.")
    st.stop()
except requests.exceptions.HTTPError as error:
    st.error("🌐 KOBIS 서버가 HTTP 오류를 반환했습니다.")
    st.write(f"오류 내용: {error}")
    st.stop()
except requests.exceptions.RequestException as error:
    st.error("🌐 KOBIS 서버에 연결하지 못했습니다.")
    st.write(f"오류 내용: {error}")
    st.stop()
except ValueError:
    st.error("📦 KOBIS 응답을 JSON으로 읽지 못했습니다.")
    st.stop()
except Exception as error:
    st.error("예상하지 못한 문제가 발생했습니다.")
    st.write(f"오류 내용: {error}")
    st.stop()

if not isinstance(data, dict):
    st.error("KOBIS에서 예상한 형식의 데이터를 받지 못했습니다.")
    st.stop()

if "faultInfo" in data:
    fault = data.get("faultInfo") or {}
    code = fault.get("errorCode", "정보 없음") if isinstance(fault, dict) else "정보 없음"
    message = fault.get("message", "오류 메시지가 없습니다.") if isinstance(fault, dict) else str(fault)
    st.error("🚨 KOBIS API가 오류 정보를 반환했습니다.")
    st.write(f"오류 코드: {code} / 메시지: {message}")
    st.stop()

boxoffice_result = data.get("boxOfficeResult", {})
movies = boxoffice_result.get("dailyBoxOfficeList", []) if isinstance(boxoffice_result, dict) else []

if not movies:
    st.warning("📭 선택하신 날짜의 박스오피스 데이터가 아직 집계 전입니다.")
    st.info("KOBIS 집계 시간을 확인하시거나 다른 날짜를 선택해 주세요.")
    st.stop()

df = pd.DataFrame(movies)

# 데이터 전처리
for column in ["rank", "rankInten", "audiCnt", "audiAcc", "scrnCnt"]:
    df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0).astype(int)

df["movieNm"] = df["movieNm"].fillna("영화명 없음").astype(str)
df["openDt"] = df["openDt"].fillna("-").replace("", "-").astype(str)

df["표시 영화명"] = df.apply(
    lambda row: f"{row['movieNm']} 🏆" if row["audiAcc"] > 1_000_000 else row["movieNm"],
    axis=1
)

def format_rank_change(value):
    if value > 0:
        return f"↑ {value}"
    if value < 0:
        return f"↓ {abs(value)}"
    return "— 0"

df["순위 변동"] = df["rankInten"].map(format_rank_change)
df = df.sort_values("rank").reset_index(drop=True)

# ----------------------------------------------------
# 🎥 1위 영화: 대형 은빛 곡선 스크린 연출
# ----------------------------------------------------
first = df.iloc[0]

st.markdown(
    f"""
    <div class="cinema-screen-box">
        <span class="screen-badge">SCREEN NO.1 — {display_date}</span>
        <div class="screen-movie-title">🥇 {first['표시 영화명']}</div>
    </div>
    """,
    unsafe_allow_html=True
)

c1, c2, c3 = st.columns(3)
c1.metric("오늘 관객수", f"{first['audiCnt']:,} 명")
c2.metric("누적 관객수", f"{first['audiAcc']:,} 명")
c3.metric("스크린수", f"{first['scrnCnt']:,} 개")

st.markdown("---")

# 📊 관객수 상위 5편 차트
st.subheader("📊 흥행 상위 TOP 5")
top5_df = df.head(5).copy()
chart_df = top5_df[["movieNm", "audiCnt"]].rename(
    columns={"movieNm": "영화명", "audiCnt": "일별 관객수"}
).set_index("영화명")

st.bar_chart(chart_df)

st.markdown("---")

# 📋 박스오피스 순위 목록 표
st.subheader("📋 박스오피스 전체 순위")
table = df[["rank", "순위 변동", "표시 영화명", "openDt", "audiCnt", "audiAcc", "scrnCnt"]].copy()
table.columns = ["순위", "전일 대비", "영화명", "개봉일", "관객수", "누적관객", "스크린수"]

def color_rank_change(value):
    if isinstance(value, str) and value.startswith("↑"):
        return "color: #ff4d4d; font-weight: bold;"
    if isinstance(value, str) and value.startswith("↓"):
        return "color: #60a5fa; font-weight: bold;"
    return "color: #94a3b8;"

st.dataframe(
    table.style.map(color_rank_change, subset=["전일 대비"]),
    hide_index=True,
    use_container_width=True,
    column_config={
        "관객수": st.column_config.NumberColumn(format="%d명"),
        "누적관객": st.column_config.NumberColumn(format="%d명"),
        "스크린수": st.column_config.NumberColumn(format="%d개"),
    }
)

st.caption("🎬 데이터 출처: 영화관입장권통합전산망(KOBIS) 일별 박스오피스 API")
