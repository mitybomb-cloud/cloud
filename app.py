import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from supabase import create_client, Client
import os

st.set_page_config(page_title='홈앤쇼핑 월별 직급별 교육 현황', layout='wide')
st.title('홈앤쇼핑 월별 직급별 교육 현황')

# Supabase 연결
@st.cache_resource
def init_supabase() -> Client:
    supabase_url = os.getenv('SUPABASE_URL', 'https://lxctrbmrjeypvctkpckl.supabase.co')
    supabase_key = os.getenv('SUPABASE_KEY')

    if not supabase_key:
        st.error('SUPABASE_KEY 환경 변수를 설정해주세요.')
        st.stop()

    return create_client(supabase_url, supabase_key)

# Supabase에서 데이터 로드
@st.cache_data
def load_data():
    supabase = init_supabase()
    response = supabase.table('ethics_training').select('*').execute()

    df = pd.DataFrame(response.data)
    df = df.rename(columns={
        'month': '월',
        'department': '부서',
        'course_name': '교육과정명',
        'total_employees': '전사인원',
        'completed': '이수자',
        'not_completed': '미이수자',
        'enrollment_rate': '수강진도율',
        'completion_rate': '완료율'
    })
    df['완료율_숫자'] = df['완료율'].astype(float)
    return df

df = load_data()

# 사이드바 필터
st.sidebar.header('필터')
months = ['전체'] + sorted(df['월'].unique().tolist())
selected_month = st.sidebar.selectbox('월 선택', months)

ranks = ['임원급', '관리직', '일반직']
selected_ranks = st.sidebar.multiselect('직급 선택', ranks, default=ranks)

# 필터링
if selected_month == '전체':
    filtered_df = df[df['부서'].isin(selected_ranks)]
else:
    filtered_df = df[(df['월'] == selected_month) & (df['부서'].isin(selected_ranks))]

# KPI 카드
col1, col2, col3, col4 = st.columns(4)

total_people = filtered_df['전사인원'].sum()
total_completed = filtered_df['이수자'].sum()
total_non_completed = filtered_df['미이수자'].sum()
avg_completion_rate = filtered_df['완료율_숫자'].mean()

col1.metric('전체 대상 인원', f'{total_people:,}명')
col2.metric('총 이수자', f'{total_completed:,}명')
col3.metric('총 미이수자', f'{total_non_completed:,}명', delta=f'{total_non_completed}명', delta_color='inverse')
col4.metric('평균 완료율', f'{avg_completion_rate:.1f}%')

st.divider()

# 데이터 테이블 (미이수자 빨간색 강조)
st.subheader('교육 현황 상세')
display_df = filtered_df[['월', '부서', '교육과정명', '전사인원', '이수자', '미이수자', '완료율']].copy()

def highlight_non_completion(val):
    if isinstance(val, (int, float)) and val > 0:
        return 'background-color: #ffcccc; color: #ff4444; font-weight: bold'
    return ''

styled = display_df.style.map(highlight_non_completion, subset=['미이수자'])
st.dataframe(styled, use_container_width=True, hide_index=True)

st.divider()

# 원형 그래프 (직급별 3개)
st.subheader('직급별 이수 현황')

col1, col2, col3 = st.columns(3)

for idx, (col, rank) in enumerate(zip([col1, col2, col3], ranks)):
    rank_data = filtered_df[filtered_df['부서'] == rank]
    completed = rank_data['이수자'].sum()
    non_completed = rank_data['미이수자'].sum()

    fig = go.Figure(data=[go.Pie(
        labels=['이수자', '미이수자'],
        values=[completed, non_completed],
        marker=dict(colors=['#2ecc71', '#ff6b6b']),
        hovertemplate='<b>%{label}</b><br>인원: %{value}명<br>비율: %{percent}<extra></extra>',
        textposition='inside',
        textinfo='label+percent'
    )])

    fig.update_layout(
        title=f'{rank} ({completed + non_completed}명)',
        height=400,
        margin=dict(l=0, r=0, t=40, b=0)
    )

    col.plotly_chart(fig, use_container_width=True)

st.divider()

# 월별 완료율 추이
st.subheader('월별 평균 완료율')
monthly_completion = df[df['부서'].isin(selected_ranks)].groupby('월')['완료율_숫자'].mean().reset_index()
monthly_completion['월'] = pd.Categorical(monthly_completion['월'], categories=['1월', '2월', '3월', '4월', '5월', '6월'], ordered=True)
monthly_completion = monthly_completion.sort_values('월')

fig_line = go.Figure()
fig_line.add_trace(go.Scatter(
    x=monthly_completion['월'],
    y=monthly_completion['완료율_숫자'],
    mode='lines+markers',
    line=dict(color='#3498db', width=3),
    marker=dict(size=10),
    hovertemplate='%{x}<br>완료율: %{y:.1f}%<extra></extra>'
))

fig_line.update_layout(
    xaxis_title='월',
    yaxis_title='완료율 (%)',
    height=400,
    yaxis=dict(range=[90, 101]),
    hovermode='x unified'
)

st.plotly_chart(fig_line, use_container_width=True)
