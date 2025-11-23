import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. 페이지 설정 및 제목
st.set_page_config(
    page_title="🍫 초콜릿 풍미 분석 대시보드",
    page_icon="🍫",
    layout="wide"
)
st.title("🌈 제조국별 초콜릿 평점 분석 대시보드")
st.markdown("---")

# 2. 데이터 로드 및 전처리 함수 (캐싱 적용)
@st.cache_data
def load_data():
    # 데이터 파일 경로 설정 (streamlit_app.py와 같은 폴더에 있다고 가정)
    file_path = 'flavors_of_cacao.csv'
    
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"데이터 파일 '{file_path}'을(를) 찾을 수 없습니다. 파일을 확인해주세요.")
        return pd.DataFrame()

    # 컬럼명 전처리 (줄바꿈 제거 및 공백 정리)
    df.columns = df.columns.str.replace('\n', ' ').str.strip()
    
    # Cocoa Percent 숫자 변환 ('%' 제거)
    if df['Cocoa Percent'].dtype == 'object':
        df['Cocoa Percent'] = df['Cocoa Percent'].str.replace('%', '').astype(float)
    
    # 주요 컬럼 이름 변경
    df.rename(columns={
        'Company (Maker-if known)': 'Company',
        'Specific Bean Origin or Bar Name': 'Origin_Bar_Name',
        'Company Location': 'Location',
        'Cocoa Percent': 'Cocoa_Percent'
    }, inplace=True)
    
    return df

df = load_data()

if df.empty:
    st.stop() # 데이터 로드 실패 시 앱 중지

# --- 판다스 데이터 요약 (Sidebar) ---
st.sidebar.header("📊 데이터 개요 (Pandas)")
st.sidebar.markdown(f"**총 리뷰 초콜릿 수:** {df.shape[0]:,}개")
st.sidebar.markdown(f"**전체 평균 평점:** **{df['Rating'].mean():.2f}점**")
st.sidebar.markdown(f"**전체 평균 카카오 함량:** {df['Cocoa_Percent'].mean():.1f}%")

st.sidebar.markdown("---")

# 4. 사용자 선택 필터 (Sidebar)
st.sidebar.header("🌍 제조국 선택")
countries = sorted(df['Location'].unique())
selected_country = st.sidebar.selectbox(
    "초콜릿 제조국 (Company Location)을 선택하세요:", 
    countries,
    index=countries.index('U.S.A.') if 'U.S.A.' in countries else 0 # 기본값 설정
)

# 선택된 국가로 데이터 필터링
filtered_df = df[df['Location'] == selected_country]

# --- 메인 화면: 선택된 국가 요약 ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(f"선택 국가 ({selected_country})의 초콜릿 수", f"{filtered_df.shape[0]} 개")
with col2:
    st.metric("이 국가의 평균 평점", f"{filtered_df['Rating'].mean():.2f} 점")
with col3:
    max_rating_bar = filtered_df.loc[filtered_df['Rating'].idxmax()]
    st.metric("최고 평점 초콜릿", f"{max_rating_bar['Origin_Bar_Name']} ({max_rating_bar['Rating']}점)")

st.markdown("---")

# 5. Plotly 인터랙티브 막대 그래프
st.subheader(f"📊 {selected_country} 초콜릿 상세 평점 (무지개 색상)")

if not filtered_df.empty:
    # 그래프 가독성을 위해 평점 기준으로 내림차순 정렬 (Top 50개만 표시)
    plot_df = filtered_df.sort_values(by='Rating', ascending=False).head(50) 
    
    fig = px.bar(
        plot_df,
        x='Origin_Bar_Name',
        y='Rating',
        color='Rating',  # 평점에 따라 색상 변경
        hover_data=['Company', 'Cocoa_Percent', 'Review Date'],
        title=f"'{selected_country}' 제조 초콜릿 평점 현황",
        labels={'Origin_Bar_Name': '초콜릿 이름 / 원두 기원', 'Rating': '평점'},
        color_continuous_scale='Rainbow', # 요청하신 무지개 색상 스케일 적용
        range_color=[1, 5] # 평점 범위 고정 (색상 일관성 유지)
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=600,
        xaxis_title="초콜릿 바 이름 / 원두 기원",
        yaxis_title="평점 (1.0 - 5.0)"
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("해당 국가의 데이터가 없습니다.")

# 6. 원본 데이터 상세 보기
with st.expander("📝 필터링된 데이터 상세 테이블"):
    st.dataframe(filtered_df.style.format({
        "Cocoa_Percent": "{:.1f}%", 
        "Rating": "{:.2f}"
    }), 
    use_container_width=True)
