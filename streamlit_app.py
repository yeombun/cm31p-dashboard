import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# 구글 시트 연동
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    dict(st.secrets["google_service_account"]), scope)
gc = gspread.authorize(creds)
sheet = gc.open("cm31p_sensor_log").sheet1   # 구글시트 이름

# 시트에서 데이터 읽어오기
records = sheet.get_all_records()
df = pd.DataFrame(records)

st.title("🌡️ CM31P 실시간 농도·온도 대시보드 (클라우드)")

if not df.empty:
    st.dataframe(df)
    st.line_chart(df[['농도', '온도']])
else:
    st.info("아직 데이터가 없습니다.")
