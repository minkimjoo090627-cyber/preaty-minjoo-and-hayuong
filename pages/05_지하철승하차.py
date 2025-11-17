# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

st.set_page_config(page_title="지하철 상위 10개 역", layout="wide")

st.title("📊 지하철 상위 10개 역 — (승차+하차) 기준")
st.markdown("2025년 10월 중 선택한 날짜와 호선의 상위 10개 역을 Plotly로 시각화합니다.")

@st.cache_data
def load_data_from_file(path):
    """로컬 CSV 파일을 cp949 → utf-8 순으로 시도하여 읽음."""
    for enc in ("cp949", "utf-8", "euc-kr"):
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception:
            pass
    st.error("CSV 파일을 불러올 수 없습니다. 인코딩 문제일 수 있습니다.")
    return None


# --------------------------
# 🔥 CSV 파일 로딩 (오류 해결 부분)
# --------------------------

DEFAULT_PATH = "subway.csv"

uploaded_file = None
df_raw = None

# 1) 먼저 로컬 파일 존재 여부 확인
if os.path.exists(DEFAULT_PATH):
    df_raw = load_data_from_file(DEFAULT_PATH)

# 2) 없으면 업로드 옵션 제공
if df_raw is None:
    st.warning("로컬에서 subway.csv 파일을 찾을 수 없습니다. CSV 파일을 업로드하세요.")
    uploaded_file = st.file_uploader("CSV 파일 업로드", type=["csv"])

    if uploaded_file:
        df_raw = pd.read_csv(uploaded_file, encoding="cp949")


# 3) 여전히 없다면 종료
if df_raw is None:
    st.stop()


# --------------------------
# 🔧 데이터 전처리
# --------------------------

def preprocess(df):
    df = df.rename(columns=lambda c: c.strip())

    df["사용일자_str"] = df["사용일자"].astype(str)
    df["사용일자_dt"] = pd.to_datetime(df["사용일자_str"], format="%Y%m%d", errors="coerce")

    for col in ["승차총승객수", "하차총승객수"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    df["승하차합"] = df["승차총승객수"] + df["하차총승객수"]
    return df

df = preprocess(df_raw)

# 2025년 10월 데이터 필터
df_202510 = df[
    (df["사용일자_dt"].dt.year == 2025) &
    (df["사용일자_dt"].dt.month == 10)
]

if df_202510.empty:
    st.error("데이터에 2025년 10월 정보가 없습니다.")
    st.stop()

available_dates = sorted(df_202510["사용일자_dt"].dt.date.unique())
st.sidebar.header("필터")

date_sel = st.sidebar.selectbox("날짜 선택", available_dates)
lines = sorted(df_202510["노선명"].unique())
line_sel = st.sidebar.selectbox("호선 선택", lines)


# --------------------------
# 🚇 상위 10개 역 계산
# --------------------------

mask = (
    (df["사용일자_dt"].dt.date == date_sel) &
    (df["노선명"] == line_sel)
)
df_selected = df[mask]

top10 = (
    df_selected.groupby("역명", as_index=False)["승하차합"]
    .sum()
    .sort_values("승하차합", ascending=False)
    .head(10)
)

# --------------------------
# 🎨 색상 설정 (1등 빨강, 나머지 파랑 그라데이션)
# --------------------------

def blue_gradient(n):
    base = (0, 102, 204)
    alphas = [0.90 - i * (0.70 / max(1, n - 1)) for i in range(n)]
    return [f"rgba({base[0]}, {base[1]}, {base[2]}, {a:.3f})" for a in alphas]

colors = ["rgba(255,0,0,1)"]  # 1등 빨강
if len(top10) > 1:
    colors += blue_gradient(len(top10) - 1)


# --------------------------
# 📈 Plotly 그래프
# --------------------------

fig = go.Figure(
    data=go.Bar(
        x=top10["역명"],
        y=top10["승하차합"],
        marker=dict(color=colors),
        text=top10["승하차합"],
        textposition="auto"
    )
)

fig.update_layout(
    title=f"{date_sel} — {line_sel} 상위 10개 역 (승차+하차 합)",
    xaxis_title="역명",
    yaxis_title="승하차합",
    template="plotly_white",
    xaxis_tickangle=-45
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("데이터")
st.dataframe(top10)
