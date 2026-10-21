import datetime
import requests
import pandas as pd
import pytz
import streamlit as st

# Streamlit 페이지 세팅 (제목 및 레이아웃 설정)
st.set_page_config(
    page_title="어제 박스오피스 순위",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 어제 일별 박스오피스")

# 1. secrets에서 인증키 불러오기
# Streamlit Cloud의 secrets 설정에 KOBIS_KEY가 저장되어 있는지 확인합니다.
if "KOBIS_KEY" not in st.secrets:
    st.error("🔑 KOBIS API 키가 설정되지 않았습니다.")
    st.info("Streamlit Cloud 설정(Secrets)에서 `KOBIS_KEY = '발급받은_키'` 형태로 추가해 주세요.")
    st.stop()

api_key = st.secrets["KOBIS_KEY"]

# 2. 한국 시간(KST) 기준으로 '어제' 날짜 계산하기
# 배포 서버의 시계(UTC)와 상관없이 한국 표준시(Asia/Seoul) 기준 어제 날짜를 구합니다.
kst_timezone = pytz.timezone("Asia/Seoul")
now_in_kst = datetime.datetime.now(kst_timezone)
yesterday_in_kst = now_in_kst - datetime.timedelta(days=1)
target_date = yesterday_in_kst.strftime("%Y%m%d")  # YYYYMMDD 포맷 문자열로 변환

# 3. KOBIS Open API 요청하기
url = f"https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json?key={api_key}&targetDt={target_date}"

try:
    response = requests.get(url, timeout=10)
    
    # HTTP 상태 코드가 200(성공)이 아닐 경우
    if response.status_code != 200:
        st.error(f"⚠️ API 서버 응답 오류가 발생했습니다. (상태 코드: {response.status_code})")
        st.info("KOBIS API 서버 상태나 네트워크 연결을 확인해 주세요.")
        st.stop()

    data = response.json()

except Exception as error:
    st.error("⚠️ 데이터 요청 중 오류가 발생했습니다.")
    st.caption(f"오류 상세 내용: {error}")
    st.info("인터넷 연결 상태를 확인하거나 잠시 후 다시 시도해 주세요.")
    st.stop()

# 4. 응답 결과 검증 (faultInfo 예외 처리 및 데이터 유효성 검사)
# KOBIS API는 키가 틀려도 200 OK를 반환하며 faultInfo 항목을 포함합니다.
if "faultInfo" in data:
    fault_msg = data["faultInfo"].get("message", "알 수 없는 오류")
    st.error("⚠️ API 호출 오류 (잘못된 인증키 등)")
    st.caption(f"서버 메시지: {fault_msg}")
    st.info("Streamlit Secrets에 입력한 KOBIS_KEY 값이 올바른지 확인해 주세요.")
    st.stop()

# boxOfficeResult 내의 dailyBoxOfficeList 추출
box_office_result = data.get("boxOfficeResult", {})
daily_list = box_office_result.get("dailyBoxOfficeList", [])

# 영화 목록이 비어 있는 경우 처리
if not daily_list:
    st.warning("⚠️ 어제 박스오피스 데이터가 비어 있습니다.")
    st.info("아직 집계가 끝나지 않았거나 KOBIS 점검 시간일 수 있습니다. 잠시 후 다시 시도해 주세요.")
    st.stop()

# 5. 데이터프레임 변환 및 숫자 형변환 (문자열 -> 숫자)
df = pd.DataFrame(daily_list)

# 필요한 컬럼 데이터의 타입을 숫자형으로 변환 (숫자 데이터가 문자열로 오므로 변환 필수)
numeric_columns = ["rank", "audiCnt", "audiAcc", "scrnCnt"]
for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# 날짜 표시용 헤더 (YYYY년 MM월 DD일 형식)
formatted_date = yesterday_in_kst.strftime("%Y년 %m월 %d일")
st.subheader(f"📅 {formatted_date} 기준")

# 6. 1위 영화 지표 카드(Metric) 세 장 표시
top_1 = df.iloc[0]

st.markdown("### 🏆 어제 박스오피스 1위")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="1위 영화명",
        value=top_1["movieNm"]
    )

with col2:
    st.metric(
        label="일별 관객수",
        value=f"{top_1['audiCnt']:,} 명"
    )

with col3:
    st.metric(
        label="누적 관객수",
        value=f"{top_1['audiAcc']:,} 명"
    )

st.divider()

# 7. 관객수 상위 5편 막대그래프 시각화
st.markdown("### 📊 관객수 상위 5편")
top5_df = df.head(5).copy()

# Streamlit 기본 차트에 맞게 컬럼명 재정의 및 인덱스 설정
chart_df = top5_df[["movieNm", "audiCnt"]].rename(
    columns={"movieNm": "영화명", "audiCnt": "일별 관객수"}
)
chart_df = chart_df.set_index("영화명")

st.bar_chart(chart_df)

st.divider()

# 8. 박스오피스 전체 순위 표 표시
st.markdown("### 📋 박스오피스 순위 목록")

# 출력할 컬럼 선택 및 한글 컬럼명으로 변경
display_df = df[["rank", "movieNm", "openDt", "audiCnt", "audiAcc", "scrnCnt"]].copy()
display_df.columns = ["순위", "영화명", "개봉일", "관객수", "누적관객", "스크린수"]

# 표 형태로 출력 (숫자 쉼표 포맷 적용)
st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "관객수": st.column_config.NumberColumn(format="%d명"),
        "누적관객": st.column_config.NumberColumn(format="%d명"),
        "스크린수": st.column_config.NumberColumn(format="%d개"),
    }
)
