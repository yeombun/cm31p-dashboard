import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from streamlit_autorefresh import st_autorefresh

# --- 페이지 설정 ---
st.set_page_config(
    page_title="CM31P 실시간 농도·온도 대시보드 (클라우드)",
    page_icon="🌡️",
    layout="wide"
)
st.title("🌡️ CM31P 실시간 농도·온도 대시보드 (클라우드)")

# --- 구글시트 연결 정보 ---
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
SERVICE_ACCOUNT = st.secrets["google_service_account"]
creds = Credentials.from_service_account_info(SERVICE_ACCOUNT, scopes=scope)
gc = gspread.authorize(creds)

SHEET_NAME = "cm31p_sensor_log"  # 구글 시트 이름
WORKSHEET = "시트1"             # 워크시트명 (Sheet1)

# --- 시트 데이터 불러오기 함수 ---
def fetch_sheet():
    worksheet = gc.open(SHEET_NAME).worksheet(WORKSHEET)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    return df

# --- 새로고침 주기 (sidebar) ---
interval = st.sidebar.slider("새로고침 주기 (초)", min_value=3, max_value=60, value=10)
st_autorefresh(interval * 1000, key="refresh")

# --- 데이터 표시 ---
try:
    df = fetch_sheet()
    st.success("데이터 수신 성공 (최근 5개 데이터)")
    st.dataframe(df.tail(5), use_container_width=True)
    # 컬럼명 한글화
    if "concentration" in df.columns:
        df = df.rename(columns={"concentration": "농도"})
    if "temperature" in df.columns:
        df = df.rename(columns={"temperature": "온도"})

    # 온도·농도 두 그래프 나란히 표시
    if "농도" in df.columns and "온도" in df.columns:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("농도(%) 변화 그래프")
            st.line_chart(df[["농도"]])
        with col2:
            st.subheader("온도(℃) 변화 그래프")
            st.line_chart(df[["온도"]])
    else:
        st.warning(f"데이터에 '농도', '온도' 컬럼이 없습니다: {df.columns.tolist()}")
except Exception as e:
    st.error(f"데이터 수신/표시 오류: {e}")
