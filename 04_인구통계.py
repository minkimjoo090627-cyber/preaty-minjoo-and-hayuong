"""
Streamlit 앱: 서울시(자치구) 연령별 인구수 인터랙티브 시각화
- 파일 업로드 허용 (CSV). 업로드하지 않으면 `/mnt/data/population.csv` 자동 로드 시도.
- 인코딩 자동 탐지(cp949, euc-kr, utf-8-sig 순)
- 행정구역 선택 시 나이(x축) vs 인구수(y축) 꺾은선(인터랙티브, Plotly)
- 우측 사이드바에 requirements 파일 내용을 표시 및 다운로드 버튼 제공
- 코드 복사할 수 있게 전체 코드가 화면(=이 파일)로 표시됩니다.

사용법 (로컬 또는 Streamlit Cloud):
1) 이 파일을 `streamlit_app.py`로 저장합니다.
2) (선택) `requirements.txt` 를 만들거나 앱 내부의 다운로드 버튼으로 받습니다.
3) 실행: `streamlit run streamlit_app.py`

"""

import io
import re
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="서울시 연령별 인구 시각화", layout="wide")

# ------------------------- 유틸 함수 -------------------------

def try_read_csv(file_like):
    """여러 인코딩으로 CSV 읽기 시도"""
    encodings = ['utf-8-sig', 'cp949', 'euc-kr', 'utf-8']
    last_exc = None
    for enc in encodings:
        try:
            return pd.read_csv(file_like, encoding=enc)
        except Exception as e:
            last_exc = e
            file_like.seek(0)
    raise last_exc


def clean_numeric_column(col):
    """쉼표 제거 후 정수 변환. 비어있거나 '-' 등은 0으로 처리"""
    if pd.api.types.is_numeric_dtype(col):
        return col.astype('Int64')
    return col.astype(str).str.replace(',', '').str.replace('\u200b','').str.replace(' ', '') \
              .replace({'': '0', '-': '0', 'nan': '0', 'NaN': '0'}) \
              .fillna('0').astype(int)


def extract_age_cols(columns):
    """열 이름에서 'N세' 또는 '100세 이상' 형태의 나이 열을 찾아 (정수 나이, 컬럼명) 리스트 반환"""
    age_cols = []
    for col in columns:
        # 예: '2025년10월_거주자_0세' 또는 '2025년10월_거주자_100세 이상'
        m = re.search(r'(\d{1,3})세\s*이상', col)
        if m:
            age = int(m.group(1))
            age_cols.append((age, col))
            continue
        m2 = re.search(r'(\d{1,3})세(?!\s*이상)', col)
        if m2:
            age = int(m2.group(1))
            age_cols.append((age, col))
    # 정렬: 나이 순. 단, 100세 이상을 100으로 취급(맨끝)
    age_cols_sorted = sorted(age_cols, key=lambda x: (x[0] if x[0] < 100 else 101))
    return age_cols_sorted


# ------------------------- 사이드바: 데이터 입력 -------------------------
st.sidebar.title("데이터 입력")
uploaded_file = st.sidebar.file_uploader("CSV 파일 업로드 (인코딩 자동 감지)", type=['csv'])
use_sample = st.sidebar.checkbox("샘플 데이터 사용 (내장)", value=False)

sample_note = """
앱은 업로드된 CSV를 우선 사용합니다. 업로드가 없으면 `/mnt/data/population.csv` 경로를 시도합니다n
파일 구조: 첫 열은 '행정구역', 다음에 '..._총인구수', 그리고 '..._0세' ~ '..._100세 이상' 형태의 연령별 열이어야 합니다.
"""
st.sidebar.info(sample_note)

# ------------------------- 데이터 로드 -------------------------

df = None

if uploaded_file is not None and not use_sample:
    try:
        # file-like 객체는 seek가 가능
        df = try_read_csv(uploaded_file)
        st.sidebar.success("업로드 파일 로드 성공")
    except Exception as e:
        st.sidebar.error(f"파일 로드 실패: {e}")

if df is None:
    # 업로드 없거나 로드 실패 시 로컬 경로 시도
    try:
        with open('/mnt/data/population.csv', 'rb') as f:
            df = try_read_csv(io.BytesIO(f.read()))
        st.sidebar.success("/mnt/data/population.csv 로드 성공")
    except Exception:
        df = None

if df is None and use_sample:
    # 간단한 샘플 생성 (예시용)
    ages = list(range(0, 101))
    cols = ['행정구역', '2025년10월_거주자_총인구수'] + [f'2025년10월_거주자_{a}세' for a in ages] + ['2025년10월_거주자_100세 이상']
    sample_rows = [
        ["서울특별시", 9246276] + [int(40000 * (0.98 ** (a/10))) for a in ages] + [1343],
        ["종로구", 135791] + [int(400 * (0.99 ** (a/10))) for a in ages] + [32],
        ["중구", 116927] + [int(500 * (0.99 ** (a/10))) for a in ages] + [18],
    ]
    df = pd.DataFrame(sample_rows, columns=cols)
    st.sidebar.success("샘플 데이터 생성 완료")

if df is None:
    st.warning("데이터가 없습니다. CSV를 업로드하거나 use_sample 옵션을 켜거나, 앱에 `/mnt/data/population.csv`를 배치하세요.")
    st.stop()

# ------------------------- 데이터 정제 -------------------------

# 컬럼명 공백 제거
orig_columns = df.columns.tolist()
clean_columns = [c.strip() for c in orig_columns]
df.columns = clean_columns

# 행정구역에서 코드 분리 (예: '서울특별시 (1100000000)')
if '행정구역' in df.columns:
    df['행정구역_원본'] = df['행정구역'].astype(str)
    m = df['행정구역_원본'].str.extract(r"^(.+?)\s*\((\d+)\)\s*$")
    if m.notnull().all(axis=None):
        df.loc[:, '행정구역명'] = m[0].fillna(df['행정구역_원본'])
        df.loc[:, '행정구역코드'] = m[1]
    else:
        df.loc[:, '행정구역명'] = df['행정구역_원본']
        df.loc[:, '행정구역코드'] = ''
else:
    st.error("'행정구역' 컬럼을 찾을 수 없습니다. CSV 구조를 확인하세요.")
    st.stop()

# 연령 관련 컬럼 추출
age_cols = extract_age_cols(df.columns)
if not age_cols:
    st.error("데이터에서 'N세' 형태의 연령별 컬럼을 찾지 못했습니다.")
    st.stop()

# 연령 컬럼명과 나이 리스트
age_to_col = {age: col for age, col in age_cols}
ages_sorted = [age for age, col in age_cols]

# 연령별 숫자형 변환
for age, col in age_cols:
    try:
        df[col] = clean_numeric_column(df[col])
    except Exception:
        # 실패 시 전체 문자열 → 숫자 변환 시도
        df[col] = df[col].astype(str).str.replace(',', '').fillna('0').replace({'': '0', '-': '0'}).astype(int)

# 총인구수도 정제 시도
if '2025년10월_거주자_총인구수' in df.columns:
    try:
        df['총인구수'] = clean_numeric_column(df['2025년10월_거주자_총인구수'])
    except Exception:
        df['총인구수'] = df['2025년10월_거주자_총인구수']

# 표시용 이름 인덱스
df_display = df.copy()
if '행정구역명' in df_display.columns:
    df_display.index = df_display['행정구역명']

# ------------------------- 레이아웃: 컨트롤과 그래프 -------------------------

st.title("서울시 연령별 인구 — 꺾은선 그래프")
col1, col2 = st.columns([1, 2])

with col1:
    st.header("설정")
    region = st.selectbox("지역구 선택", options=df_display.index.tolist(), index=0)
    smoothing = st.checkbox("이동평균(3점) 적용", value=False)
    show_points = st.checkbox("데이터 포인트 표시", value=True)
    log_scale = st.checkbox("세로축 로그 스케일", value=False)

with col2:
    st.header("그래프")
    # 선택된 지역 데이터 준비
    row = df_display.loc[region]
    y_values = [int(row[age_to_col[age]]) for age in ages_sorted]
    x_values = ages_sorted.copy()

    plot_df = pd.DataFrame({'age': x_values, 'population': y_values})

    if smoothing and len(plot_df) >= 3:
        plot_df['population_smoothed'] = plot_df['population'].rolling(3, center=True, min_periods=1).mean()
        y_col = 'population_smoothed'
    else:
        y_col = 'population'

    fig = px.line(plot_df, x='age', y=y_col, markers=show_points,
                  title=f"{region} — 연령별 인구수",
                  labels={'age': '나이 (세)', y_col: '인구수'})

    # 툴팁에 원래 population도 표시
    fig.update_traces(hovertemplate='나이: %{x}세<br>인구수: %{y:,}')
    fig.update_layout(hovermode='x unified', xaxis=dict(dtick=5))
    if log_scale:
        fig.update_yaxes(type='log')

    st.plotly_chart(fig, use_container_width=True)

# ------------------------- 다운로드: 요구사항 파일 -------------------------

requirements_txt = """
streamlit>=1.24
pandas>=1.5
plotly>=5.0
""".strip()

with st.expander("요구사항 파일 (requirements.txt) 및 앱 파일 보기/다운로드"):
    st.subheader("requirements.txt 내용")
    st.code(requirements_txt, language='text')
    st.download_button("requirements.txt 다운로드", requirements_txt, file_name='requirements.txt')

    st.subheader("앱 전체 코드 (복사 가능)")
    # 이 파일의 소스 코드를 표시(사용자가 복사 가능)
    import inspect
    this_src = inspect.getsource(inspect.getmodule(inspect.currentframe()))
    st.text_area("앱 코드 (전체)", this_src, height=400)

# ------------------------- 추가 정보: 간단 통계 -------------------------

with st.expander("데이터 통계 요약"):
    st.write(f"데이터 행 개수: {len(df_display)}  |  연령 칼럼 수: {len(age_cols)}")
    top5 = df_display[['총인구수']].sort_values('총인구수', ascending=False).head(5)
    st.write("총인구수 상위 5개 지역")
    st.dataframe(top5)

# ------------------------- 끝 -------------------------
