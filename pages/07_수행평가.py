# pages/analysis.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
import os

st.set_page_config(page_title="데이터 꼼꼼 요약 + 인터랙티브 그래프", layout="wide")

st.title("🍦 Frozen Dessert Production — 데이터 꼼꼼 요약/시각화")
st.write("파일: `./Frozen_Dessert_Production.csv` 에서 데이터를 불러와서 자동으로 분석해줄게요. 편하게 둘러봐~ 😎")

# ------------------------
# 1) CSV 로드 (루트 -> 대체경로 지원)
# ------------------------
default_paths = [
    "./Frozen_Dessert_Production.csv",
    "/workspace/Frozen_Dessert_Production.csv",
    "/app/Frozen_Dessert_Production.csv",
    "/mnt/data/Frozen_Dessert_Production.csv",
]
csv_path = None
for p in default_paths:
    if os.path.exists(p):
        csv_path = p
        break

if csv_path is None:
    st.error("❗ CSV 파일을 루트에 `Frozen_Dessert_Production.csv`로 업로드해 주세요.")
    st.stop()

st.success(f"✅ 파일 로드됨: `{csv_path}`")
df = pd.read_csv(csv_path)

# ------------------------
# 2) 기본 전처리: 날짜 칼럼 찾기/변환
# ------------------------
df_original = df.copy()
date_col = None
# heuristics: 'date' 칼럼 이름 유무, 혹은 첫번째 칼럼이 날짜형식인지 검사
for c in df.columns:
    if "date" in c.lower():
        date_col = c
        break

if date_col is None:
    # 시도: 첫 번째 칼럼이 날짜로 변환 가능한지
    first = df.columns[0]
    try:
        pd.to_datetime(df[first])
        date_col = first
    except Exception:
        pass

if date_col is None:
    st.error("❗ 날짜 칼럼을 자동으로 찾을 수 없었어. CSV에 날짜형 칼럼(예: DATE)이 있어야 해.")
    st.write("현재 칼럼:", list(df.columns))
    st.stop()

# 날짜 변환
df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
df = df.sort_values(by=date_col).reset_index(drop=True)

# 수치 칼럼 선택: 날짜 칼럼 외의 첫 번째 수치형 칼럼 사용
num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
if not num_cols:
    # 시도: 강제로 두번째 칼럼을 numeric 변환
    other_cols = [c for c in df.columns if c != date_col]
    if other_cols:
        c = other_cols[0]
        df[c] = pd.to_numeric(df[c], errors="coerce")
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

if not num_cols:
    st.error("❗ 숫자(수치) 칼럼을 찾지 못했어. 날짜 외에 생산량/지수 같은 수치 칼럼이 필요해.")
    st.stop()

value_col = num_cols[0]

st.markdown("### 📄 원본 데이터 미리보기")
st.dataframe(df.head(10), use_container_width=True)

# ------------------------
# 3) 꼼꼼한 pandas 요약
# ------------------------
st.markdown("## 🧾 자동 요약 (pandas 기반)")

col1, col2, col3 = st.columns([1,1,1])

with col1:
    st.subheader("기본 정보")
    st.write(f"- 행 수: **{df.shape[0]}**")
    st.write(f"- 열 수: **{df.shape[1]}**")
    st.write(f"- 날짜 칼럼: **{date_col}**")
    st.write(f"- 값 칼럼(분석 대상): **{value_col}**")

with col2:
    st.subheader("결측치 요약")
    na_counts = df.isna().sum()
    st.write(na_counts[na_counts > 0] if na_counts.sum() > 0 else "결측치 없음 👍")

with col3:
    st.subheader("기간")
    min_date = df[date_col].min()
    max_date = df[date_col].max()
    st.write(f"- 시작: **{min_date.date()}**")
    st.write(f"- 종료: **{max_date.date()}**")
    st.write(f"- 기간 길이: **{(max_date - min_date).days} days**")

st.markdown("### 📊 기초 통계")
st.write(df[value_col].describe().to_frame().T)

# 상위/하위 이벤트
st.markdown("### 🏆 상/하위 시점 (값 기준)")
top5 = df.nlargest(5, value_col)[[date_col, value_col]]
bot5 = df.nsmallest(5, value_col)[[date_col, value_col]]
c1, c2 = st.columns(2)
with c1:
    st.write("✅ 상위 5 시점")
    st.dataframe(top5.assign(**{date_col: top5[date_col].dt.date}))
with c2:
    st.write("🔻 하위 5 시점")
    st.dataframe(bot5.assign(**{date_col: bot5[date_col].dt.date}))

# 변화량(연평균 성장률 등)
st.markdown("### 📈 변화 요약")
df = df.dropna(subset=[date_col, value_col]).copy()
if df.shape[0] >= 2:
    # 전체 변화, CAGR-like
    first_val = df.iloc[0][value_col]
    last_val = df.iloc[-1][value_col]
    total_change = last_val - first_val
    pct_change = (last_val / first_val - 1) * 100 if first_val != 0 else np.nan
    st.write(f"- 시작 값: **{first_val:.4g}**, 최근 값: **{last_val:.4g}**")
    st.write(f"- 전체 변화: **{total_change:.4g}** ({pct_change:.2f}%)")
else:
    st.write("데이터가 충분하지 않아서 변화 요약을 만들 수 없어 🤔")

# ------------------------
# 4) Plotly 그래프: 1등 빨간색, 나머지 그라데이션
# ------------------------
st.markdown("## 📉 인터랙티브 그래프 (Plotly) — 최고값은 빨강! 🔴")
# normalize values to [0,1]
vals = df[value_col].values
vmin, vmax = np.nanmin(vals), np.nanmax(vals)
if np.isnan(vmin) or np.isnan(vmax):
    st.error("수치 데이터가 유효하지 않습니다.")
    st.stop()

# 색상 맵 생성: 기본적으로 plotly의 연속 색상 팔레트를 사용하고, 최고값은 빨강으로 override
# we will sample a sequential colorscale for non-max points
colorscale = px.colors.sequential.Plasma  # nice gradient
# function to map normalized value to a color from colorscale
from plotly.colors import sample_colorscale

norm = (vals - vmin) / (vmax - vmin) if vmax != vmin else np.zeros_like(vals)
sampled = sample_colorscale(colorscale, list(norm))  # list of hex colors

# override the index(es) where value==max to bright red
max_idx = np.where(vals == vmax)[0]
for i in max_idx:
    sampled[i] = "#ff4136"  # red

# build figure: line + markers colored individually
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df[date_col],
    y=vals,
    mode='lines+markers',
    marker=dict(size=8, color=sampled),
    line=dict(color='rgba(100,100,100,0.2)', width=2),
    hovertemplate=f"%{{x|%Y-%m-%d}}<br>{value_col}: %{{y:.4f}}<extra></extra>"
))

fig.update_layout(
    title=f"{value_col} over Time",
    xaxis_title=str(date_col),
    yaxis_title=str(value_col),
    template="plotly_white",
    hovermode="x unified",
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# 강조: 최고값 정보 카드
if len(max_idx) > 0:
    mdate = df.iloc[max_idx[0]][date_col].date()
    mval = df.iloc[max_idx[0]][value_col]
    st.info(f"🔴 최고값: **{mval:.4g}** — 시점: **{mdate}**")

# ------------------------
# 5) 간단한 해석(자동 문장, 1줄 후기 형태)
# ------------------------
st.markdown("## 🧠 자동 해석 — 왜 이 값이 중요한지 한줄 후기")
# heuristic comments
if pct_change > 10:
    summary_line = f"요약: 장기적으로 **상승 추세**를 보여줘! 최근 값이 시작값보다 {pct_change:.1f}% 더 높아 — 성장 성향이 있어 보여. 📈"
elif pct_change < -10:
    summary_line = f"요약: 장기적으로 **하락 추세**야. 최근 값이 시작값보다 {abs(pct_change):.1f}% 낮아. 주의 필요! ⚠️"
else:
    summary_line = "요약: 큰 변화 없이 **안정적**인 흐름을 보여줘 — 안정형 데이터야. 🧘‍♀️"

st.write(summary_line)

# 한줄 후기(친근한 톤)
st.markdown("**한줄 후기(친근):**")
st.write("이 데이터, 한눈에 보기엔 안정적인데 꼭 최고점을 한번 찍어본 시점은 체크해봐! 그때 뭔가 이벤트가 있었을 수도 있어. 🍰✨")

# ------------------------
# 6) 다운로드: 요약 CSV로 제공
# ------------------------
st.markdown("## 💾 요약 파일 다운로드")
summary_df = pd.DataFrame({
    "start_date": [min_date.date()],
    "end_date": [max_date.date()],
    "rows": [df.shape[0]],
    "value_column": [value_col],
    "min_value": [vmin],
    "max_value": [vmax],
    "latest_value": [last_val if 'last_val' in locals() else np.nan],
})
st.download_button("요약 CSV 다운로드 (summary.csv) 📥", summary_df.to_csv(index=False), file_name="summary.csv", mime="text/csv")

st.write("끝! 필요한 추가 분석(예: 연도별 집계, 계절성 분석, 이동평균 등)도 바로 만들어줄게. 말만 해~ 😄")
