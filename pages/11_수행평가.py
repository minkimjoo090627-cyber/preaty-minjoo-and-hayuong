import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 페이지 설정
st.set_page_config(
    page_title="Cacao Flavors Dashboard",
    page_icon="🍫",
    layout="wide"
)

# 데이터 로드 함수 (캐싱 적용)
@st.cache_data
def load_data():
    # 파일 경로 설정 (코드가 pages 폴더 안에 있으므로 상위 폴더로 이동)
    file_path = os.path.join(os.path.dirname(__file__), '../flavors_of_cacao.csv')
    
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        # 로컬 테스트나 경로가 다를 경우를 대비한 예외 처리
        try:
            df = pd.read_csv('flavors_of_cacao.csv')
        except:
            st.error("데이터 파일을 찾을 수 없습니다. 'flavors_of_cacao.csv' 파일 위치를 확인해주세요.")
            return pd.DataFrame()

    # 1. 컬럼명 전처리 (줄바꿈 제거 및 공백 정리)
    df.columns = df.columns.str.replace('\n', ' ').str.strip()
    
    # 2. Cocoa Percent 숫자 변환 ('%' 제거)
    if df['Cocoa Percent'].dtype == 'object':
        df['Cocoa Percent'] = df['Cocoa Percent'].str.replace('%', '').astype(float)
    
    # 3. 주요 컬럼 이름 변경 (편의상)
    df.rename(columns={
        'Company (Maker-if known)': 'Company',
        'Specific Bean Origin or Bar Name': 'Origin_Bar_Name',
        'Company Location': 'Location',
        'Cocoa Percent': 'Cocoa_Percent'
    }, inplace=True)
    
    return df

# 메인 앱 로직
def main():
    st.title("🍫 전 세계 초콜릿 풍미 분석 대시보드")
    st.markdown("이 대시보드는 **Flavors of Cacao** 데이터셋을 기반으로 제조국별 초콜릿 평점을 시각화합니다.")

    df = load_data()
    
    if df.empty:
        return

    # 사이드바: 데이터 요약 및 필터
    st.sidebar.header("📊 데이터 요약")
    st.sidebar.markdown(f"**총 리뷰 수:** {df.shape[0]}개")
    st.sidebar.markdown(f"**평균 평점:** {df['Rating'].mean():.2f}점")
    st.sidebar.markdown(f"**평균 카카오 함량:** {df['Cocoa_Percent'].mean():.1f}%")
    st.sidebar.markdown("---")

    st.sidebar.header("🌍 필터 설정")
    # 제조국 선택 (가나다/알파벳 순 정렬)
    countries = sorted(df['Location'].unique())
    selected_country = st.sidebar.selectbox("제조국(Company Location)을 선택하세요:", countries)

    # 선택된 국가로 데이터 필터링
    filtered_df = df[df['Location'] == selected_country]

    # --- 메인 화면 구성 ---

    # 1. 선택된 국가 정보 요약
    st.subheader(f"📍 {selected_country} 초콜릿 분석")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("등록된 초콜릿 수", f"{filtered_df.shape[0]} 개")
    with col2:
        st.metric("이 국가의 평균 평점", f"{filtered_df['Rating'].mean():.2f} 점")
    with col3:
        max_rating = filtered_df['Rating'].max()
        st.metric("최고 평점", f"{max_rating} 점")

    st.divider()

    # 2. Plotly 막대 그래프 (무지개 색상)
    st.subheader("🌈 초콜릿 별 평점 시각화")
    
    if not filtered_df.empty:
        # 그래프 가독성을 위해 평점 기준으로 내림차순 정렬
        filtered_df = filtered_df.sort_values(by='Rating', ascending=False)
        
        fig = px.bar(
            filtered_df,
            x='Origin_Bar_Name',
            y='Rating',
            color='Rating',  # 평점에 따라 색상 변경
            hover_data=['Company', 'Cocoa_Percent', 'Review Date'],
            title=f"{selected_country} - 초콜릿 별 평점 현황",
            labels={'Origin_Bar_Name': '초콜릿 이름 (원산지)', 'Rating': '평점'},
            color_continuous_scale='Rainbow', # 무지개 색상 스케일 적용
            range_color=[1, 5] # 평점 범위 고정 (색상 일관성 유지)
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            height=600,
            xaxis_title="초콜릿 바 이름 / 원두 기원",
            yaxis_title="평점 (1-5)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("해당 국가의 데이터가 없습니다.")

    # 3. 데이터프레임 원본 보기 (옵션)
    with st.expander("📋 상세 데이터 보기"):
        st.dataframe(filtered_df.style.format({"Cocoa_Percent": "{:.1f}%", "Rating": "{:.2f}"}))

if __name__ == "__main__":
    main()
