# 어제의 박스오피스 — KOBIS 일별 박스오피스 API (영화관 테마 디자인)
import datetime
import requests
import pandas as pd
import streamlit as st

# 페이지 세팅
st.set_page_config(page_title="어제의 박스오피스", page_icon="🎬", layout="wide")

# ----------------------------------------------------
# 🎨 영화관 분위기 CSS 스타일링 (다크 테마 + 스크린 효과)
# ----------------------------------------------------
st.markdown("""
    <style>
    /* 전체 배경을 영사기가 켜진 어두운 영화관 느낌으로 연출 */
    .stApp {
        background-color: #0d0f12;
        color: #e0e0e0;
    }
    
    /* 영화관 스크린 프레임 (상단 곡선 패널) */
    .cinema-screen-container {
        background: linear-gradient(180deg, #ffffff 0%, #d8e2ec 80%, #a0b2c6 100%);
        border-radius: 12px 12px 60px 60px / 12px 12px 25px 25px;
        padding: 30px 20px 40px 20px;
        color: #111111;
        text-align: center;
        box-shadow: 0px 15px 35px rgba(255, 255, 255, 0.25), inset 0px -5px 15px rgba(0,0,0,0.3);
        margin-bottom: 25px;
        border: 2px solid #ffffff;
    }

    /* 스크린 빛 반사 타이틀 */
    .screen-title {
        font-size: 1.2rem;
        font-weight: 700;
        letter-spacing: 3px;
        color: #555555;
        text-transform: uppercase;
        margin-bottom: 5px;
    }

    .screen-movie-name {
        font-size: 2.3rem;
        font-weight: 900;
        color: #0f172a;
        margin-top: 5px;
        text-shadow: 0px 2px 4px rgba(0,0,0,0.15);
    }

    /* 영사기 빔 효과선 */
    .projector-beam {
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent);
        margin: 15px 0 25px 0;
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

st.title("🎬 CINEMA BOX OFFICE")
st.caption("달력에서 날짜를 선택하세요. 가장 늦게 선택할 수 있는 날짜는 한국 시간 기준 어제입니다.")

selected_date = st.date_input(
    "조회 날짜 선택",
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
    with st.spinner("영화관 스크린에 영사 중입니다..."):
        data = fetch_boxoffice(target_dt, str(API_KEY).strip())
except requests.exceptions.Timeout:
    st.error("⏱️ KOBIS 서버 응답 시간이 초과되었습니다.")
    st.info("인터넷 연결을 확인하고 잠시 후 새로고침해 주세요.")
    st.stop()
except requests.exceptions.HTTPError as error:
    st.error("🌐 KOBIS 서버가 HTTP 오류를 반환했습니다.")
    st.write(f"오류 내용: {error}")
    st.info("KOBIS 서비스 상태와 요청 주소를 확인해 주세요.")
    st.stop()
except requests.exceptions.RequestException as error:
    st.error("🌐 KOBIS 서버에 연결하지 못했습니다.")
    st.write(f"오류 내용: {error}")
    st.info("인터넷 연결, 방화벽, KOBIS API 서비스 상태를 확인해 주세요.")
    st.stop()
except ValueError:
    st.error("📦 KOBIS 응답을 JSON으로 읽지 못했습니다.")
    st.info("잠시 후 다시 시도하거나 KOBIS API 상태를 확인해 주세요.")
    st.stop()
except Exception as error:
    st.error("예상하지 못한 문제가 발생했습니다.")
    st.write(f"오류 내용: {error}")
    st.info("앱 설정과 실행 로그를 확인해 주세요.")
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
# 📽️ 1위 영화: 영화관 대형 스크린 전광판 스타일
# ----------------------------------------------------
first = df.iloc[0]

st.markdown('<div class="projector-beam"></div>', unsafe_allow_html=True)
st.markdown(f"""
    <div class="cinema-screen-container">
        <div class="screen-title">NOW SHOWING NO.1 — {display_date}</div>
        <div class="screen-movie-name">🥇 {first['표시 영화명']}</div>
    </div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("오늘 관객수", f"{first['audiCnt']:,} 명")
c2.metric("누적 관객수", f"{first['audiAcc']:,} 명")
c3.metric("스크린수", f"{first['scrnCnt']:,} 개")

st.divider()

# 📊 관객수 상위 5편 차트
st.subheader("📊 관객수 상위 TOP 5")
top5_df = df.head(5).copy()
chart_df = top5_df[["movieNm", "audiCnt"]].rename(
    columns={"movieNm": "영화명", "audiCnt": "일별 관객수"}
).set_index("영화명")

st.bar_chart(chart_df)

st.divider()

# 📋 박스오피스 순위 목록 표
st.subheader("📋 전체 박스오피스 순위")
table = df[["rank", "순위 변동", "표시 영화명", "openDt", "audiCnt", "audiAcc", "scrnCnt"]].copy()
table.columns = ["순위", "전일 대비", "영화명", "개봉일", "관객수", "누적관객", "스크린수"]

def color_rank_change(value):
    if isinstance(value, str) and value.startswith("↑"):
        return "color: #ff5252; font-weight: bold;"
    if isinstance(value, str) and value.startswith("↓"):
        return "color: #448aff; font-weight: bold;"
    return "color: #888888;"

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

st.caption("데이터 출처: 영화관입장권통합전산망(KOBIS) 일별 박스오피스 API")
