import streamlit as st
import pandas as pd
import plotly.express as px

# CSV 불러오기 (상위 폴더)
df = pd.read_csv('../제주특별자치도_서귀포시_제과점현황_20250401.csv', encoding='cp949')

st.title("🥐 제주 서귀포 제과점 현황 (인터랙티브 차트)")
st.write("📆 데이터 기준일:", df["데이터기준일자"].iloc[0])

# 읍/면/동 추출
df["지역"] = df["소재지(도로명)"].str.extract(r"서귀포시\s(.+?)[\s,]")

# 지역 선택
regions = sorted(df["지역"].dropna().unique())
selected = st.selectbox("🔎 지역을 선택하세요", regions)

# 해당 지역 필터링
filtered = df[df["지역"] == selected]

st.write(f"📌 **{selected} 지역 제과점 수: {len(filtered)}개**")
st.dataframe(filtered[["업소명", "소재지(도로명)"]])

# Plotly 바 차트 (무지개 색)
fig = px.bar(
    filtered,
    x="업소명",
    y="위도",  # y값은 의미 없는 값, bar 높이 용
    title=f"🍞 {selected} 지역 제과점 분포",
    text="업소명",
    color="업소명",
    color_discrete_sequence=px.colors.qualitative.Vivid,  # 🌈 무지개 느낌
)

fig.update_layout(xaxis_title="제과점 이름", yaxis_title="", showlegend=False)

st.plotly_chart(fig, use_container_width=True)
