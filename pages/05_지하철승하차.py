# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="지하철 상위역 시각화", layout="wide")

st.title("📊 지하철 상위 10개 역 — (승차+하차) 기준")
st.markdown(
    "CSV 파일(`/mnt/data/subway.csv`)을 읽어 2025년 10월 중 선택한 날짜와 호선의 상위 10개 역을 그립니다. "
    "색상: 1등 = 빨강, 나머지 = 파란색 그라데이션."
)

@st.cache_data
def load_data(path="/mnt/data/subway.csv"):
    # 시도: cp949(윈도우 한국어), 실패하면 utf-8
    for enc in ("cp949", "utf-8", "euc-kr"):
        try:
            df = pd.read_csv(path, encoding=enc)
            return df
        except Exception as e:
            last_err = e
    raise last_err

def preprocess(df):
    # 컬럼 이름 통일(공백/대소문자 이슈 대비)
    df = df.rename(columns=lambda c: c.strip())
    # 사용일자 -> datetime (YYYYMMDD 예상)
    if "사용일자" in df.columns:
        df["사용일자_str"] = df["사용일자"].astype(str)
        df["사용일자_dt"] = pd.to_datetime(df["사용일자_str"], format="%Y%m%d", errors="coerce")
    else:
        st.error("CSV에 '사용일자' 컬럼이 없습니다.")
        return df

    # 승/하차 컬럼 존재 확인 및 숫자형 변환
    for col in ["승차총승객수", "하차총승객수"]:
        if col not in df.columns:
            st.error(f"CSV에 '{col}' 컬럼이 없습니다.")
            return df
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # 합계 컬럼 추가
    df["승하차합"] = df["승차총승객수"] + df["하차총승객수"]
    return df

def blue_gradient_colors(n):
    """
    n >= 1. Returns list of rgba strings where the first will be reserved for red externally.
    For blue gradient we return n colors with alpha descending from ~0.95 to 0.25.
    """
    base = (0, 102, 204)  # blue
    if n == 0:
        return []
    # produce n alphas between 0.95 and 0.25
    alphas = [0.95 - i * (0.70 / max(1, n-1)) for i in range(n)]
    return [f"rgba({base[0]}, {base[1]}, {base[2]}, {alpha:.3f})" for alpha in alphas]

# Load & preprocess
with st.spinner("데이터 불러오는 중..."):
    try:
        df_raw = load_data()
    except Exception as e:
        st.exception(e)
        st.stop()

df = preprocess(df_raw)

# 날짜 필터: 2025년 10월만 표시
df_2025_10 = df[df["사용일자_dt"].notna() & (df["사용일자_dt"].dt.year == 2025) & (df["사용일자_dt"].dt.month == 10)]
if df_2025_10.empty:
    st.warning("데이터에 2025년 10월 데이터가 없습니다. 전체 데이터에서 선택하려면 '모두 보기'를 체크하세요.")
    use_all = st.checkbox("모두 보기 (10월이 아닐 수도 있음)", value=False)
    if use_all:
        available_dates = sorted(df["사용일자_dt"].dropna().unique())
    else:
        st.stop()
else:
    available_dates = sorted(df_2025_10["사용일자_dt"].dropna().dt.date.unique())

# 사이드바 컨트롤
st.sidebar.header("필터")
date_sel = st.sidebar.selectbox("날짜 선택 (2025년 10월)", available_dates, index=0)
# Ensure date_sel is a date object
if isinstance(date_sel, datetime):
    date_sel = date_sel.date()

# 호선 선택: available on that date
if not use_all if 'use_all' in locals() and not use_all else True:
    df_for_lines = df[df["사용일자_dt"].dt.date == date_sel]
else:
    df_for_lines = df.copy()

lines = sorted(df_for_lines["노선명"].dropna().unique())
if not lines:
    st.error("선택한 날짜/조건에 해당하는 '노선명'이 없습니다.")
    st.stop()

line_sel = st.sidebar.selectbox("호선 선택", lines, index=0)

# 집계
if not use_all if 'use_all' in locals() and not use_all else True:
    mask = (df["사용일자_dt"].dt.date == date_sel) & (df["노선명"] == line_sel)
else:
    mask = (df["노선명"] == line_sel)

df_selected = df[mask].copy()

if df_selected.empty:
    st.warning("선택한 날짜와 호선에 해당하는 데이터가 없습니다.")
    st.stop()

# 역별 합계 집계
top10 = (
    df_selected.groupby("역명", dropna=False, as_index=False)["승하차합"]
    .sum()
    .sort_values("승하차합", ascending=False)
    .head(10)
)

# Prepare colors: first red, others blue gradient
n = len(top10)
if n == 0:
    st.warning("해당 조건에 맞는 역 데이터가 없습니다.")
    st.stop()

reds = ["rgba(255,0,0,1.0)"]  # 1st place
blue_colors = blue_gradient_colors(max(0, n - 1))
# If there are fewer than 10 (e.g., n<10), still assign
colors = []
if n >= 1:
    colors.append(reds[0])
if n > 1:
    colors.extend(blue_colors[: n - 1])

# Make Plotly bar chart
stations = top10["역명"].astype(str).tolist()
values = top10["승하차합"].tolist()

fig = go.Figure(
    data=go.Bar(
        x=stations,
        y=values,
        marker=dict(color=colors),
        text=values,
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>승하차합: %{y}<extra></extra>',
    )
)

fig.update_layout(
    title=f"{date_sel} — {line_sel} 호선 기준 상위 {n}개 역 (승차+하차 합)",
    xaxis_title="역명",
    yaxis_title="승하차합",
    template="plotly_white",
    xaxis_tickangle=-45,
    margin=dict(t=70, b=120)
)

st.plotly_chart(fig, use_container_width=True)

# 하단: 데이터 테이블 및 다운로드
with st.expander("데이터 확인 (상위 목록)"):
    st.dataframe(top10.reset_index(drop=True))

csv = top10.to_csv(index=False).encode("utf-8-sig")
st.download_button("Top10 CSV 다운로드", data=csv, file_name=f"top10_{date_sel}_{line_sel}.csv", mime="text/csv")
