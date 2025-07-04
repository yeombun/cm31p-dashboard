import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="CM31P 실시간 농도·온도 대시보드 (클라우드)",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ CM31P 실시간 농도·온도 대시보드 (클라우드)")

# === Google Sheets 연결 ===
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
# Streamlit Cloud에서는 secrets를 사용
SERVICE_ACCOUNT = st.secrets["google_service_account"]

creds = Credentials.from_service_account_info(SERVICE_ACCOUNT, scopes=scope)
gc = gspread.authorize(creds)

SHEET_NAME = "cm31p_sensor_log"   # 구글시트 이름
WORKSHEET = "Sheet1"              # 워크시트 이름

def fetch_sheet():
    worksheet = gc.open(SHEET_NAME).worksheet(WORKSHEET)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    return df

# --- 새로고침 주기 설정 ---
interval = st.sidebar.slider("새로고침 주기 (초)", min_value=3, max_value=60, value=10)

# --- 데이터 불러오기 ---
try:
    df = fetch_sheet()
    st.write("#### 최근 데이터 (마지막 5개)")
    st.dataframe(df.tail(5), use_container_width=True)

    # 컬럼명 확인
    st.write("컬럼명:", df.columns.tolist())
    # 컬럼명 맞추기 (영문-한글 변환)
    if "concentration" in df.columns:
        df = df.rename(columns={"concentration": "농도"})
    if "temperature" in df.columns:
        df = df.rename(columns={"temperature": "온도"})

    # 그래프
    if "농도" in df.columns and "온도" in df.columns:
        st.line_chart(df[["농도", "온도"]])
    else:
        st.warning("데이터에 '농도', '온도' 컬럼이 없습니다. 컬럼명: " + str(df.columns.tolist()))

except Exception as e:
    st.error(f"데이터 수신/표시 오류: {e}")

# --- 주기적 새로고침 ---
st.experimental_rerun()
st_autorefresh(interval * 1000, key="data_refresh")

