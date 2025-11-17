
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
