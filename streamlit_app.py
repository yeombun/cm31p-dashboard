import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from streamlit_autorefresh import st_autorefresh
import plotly.express as px

# --- 페이지 설정 ---
st.set_page_config(
    page_title="실시간 염도 모니터링 시스템",
    page_icon="🌡️",
    layout="wide"
)
st.title("🌡 실시간 염도 모니터링 시스템")

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

def fetch_sheet():
    worksheet = gc.open(SHEET_NAME).worksheet(WORKSHEET)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    return df

# --- 새로고침 주기 (sidebar) ---
interval = st.sidebar.slider("새로고침 주기 (초)", min_value=3, max_value=60, value=10)
st_autorefresh(interval * 1000, key="refresh")

try:
    df = fetch_sheet()
    st.success("데이터 수신 성공 (최근 5개 데이터)")
    st.dataframe(df.tail(5), use_container_width=True)
    # 컬럼명 한글화
    if "concentration" in df.columns:
        df = df.rename(columns={"concentration": "염도"})
    if "temperature" in df.columns:
        df = df.rename(columns={"temperature": "온도"})

    # 최신 100개만 표시 (그래프 가독성)
    df_plot = df.tail(100).reset_index(drop=True)
    x_vals = df_plot.index  # 혹시 시간 컬럼이 있다면 df_plot["timestamp"] 등으로 바꿔도 좋음

    if "염도" in df_plot.columns and "온도" in df_plot.columns:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("염도(%)")
            fig_c = px.line(
                df_plot, x=x_vals, y="염도",
                markers=True, title=None,
                labels={"x": "Index", "염도": "염도(%)"}
            )
            fig_c.update_layout(yaxis_title="농도(%)", margin=dict(l=30, r=10, t=30, b=30))
            st.plotly_chart(fig_c, use_container_width=True)
        with col2:
            st.subheader("온도(℃)")
            fig_t = px.line(
                df_plot, x=x_vals, y="온도",
                markers=True, title=None,
                labels={"x": "Index", "온도": "온도(℃)"}
            )
            fig_t.update_layout(yaxis_title="온도(℃)", margin=dict(l=30, r=10, t=30, b=30))
            st.plotly_chart(fig_t, use_container_width=True)
    else:
        st.warning(f"데이터에 '염도', '온도' 컬럼이 없습니다: {df.columns.tolist()}")
except Exception as e:
    st.error(f"데이터 수신/표시 오류: {e}")
