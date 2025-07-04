import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

st.set_page_config(layout="wide", page_title="CM31P 실시간 대시보드 (Cloud)")

def fetch_sheet():
    # 인증 및 시트 연결
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    gc = gspread.authorize(creds)
    sheet = gc.open("cm31p_sensor_log").sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)

st.title("☁️ CM31P 실시간 농도·온도 대시보드 (클라우드)")

interval = st.sidebar.slider("새로고침 주기 (초)", 3, 60, 10)

while True:
    df = fetch_sheet()
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        latest = df.iloc[-1]
        c1, c2 = st.columns(2)
        with c1:
            st.metric("현재 농도 (%)", f"{latest['concentration']:.3f}")
        with c2:
            st.metric("현재 온도 (℃)", f"{latest['temperature']:.2f}")
        st.subheader("📈 농도 변화")
        st.line_chart(df.set_index("timestamp")[["concentration"]])
        st.subheader("🌡️ 온도 변화")
        st.line_chart(df.set_index("timestamp")[["temperature"]])
        st.subheader("📋 최근 로그")
        st.dataframe(df.tail(10), use_container_width=True)
    else:
        st.info("아직 데이터가 없습니다.")
    time.sleep(interval)
    st.rerun()
