import streamlit as st

st.set_page_config(
    page_title="계절별 독감 발생률 분석",
    page_icon="🦠",
    layout="wide"
)

st.markdown("""
<style>
    .main-title {
        font-size: 2.8rem;
        font-weight: 900;
        color: #1a1a2e;
        text-align: center;
        padding: 30px 0 10px 0;
    }
    .sub-title {
        font-size: 1.2rem;
        color: #4a4a6a;
        text-align: center;
        margin-bottom: 40px;
    }
    .card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 16px;
        padding: 30px;
        color: white;
        text-align: center;
        margin: 10px;
        cursor: pointer;
    }
    .info-box {
        background-color: #f0f4ff;
        border-left: 5px solid #4361ee;
        border-radius: 8px;
        padding: 18px 22px;
        margin: 10px 0;
        color: #1a1a2e;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🦠 계절별 독감 발생률 분석</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">2014-15 ~ 2025-26 시즌 인플루엔자 데이터 × 서울 기온 데이터 기반 분석</div>', unsafe_allow_html=True)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="card">
        <h2>📊 Page 1</h2>
        <h3>독감 발생률 전체 분석</h3>
        <p>시즌별 ILI 추이, 계절별 평균 비교,<br>히트맵, 유행 지속 기간 분석</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <h2>🌡️ Page 2</h2>
        <h3>날씨와 독감 상관관계</h3>
        <p>기온 vs ILI 산점도, 상관계수,<br>기온 구간별 분석, 이중 축 비교</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
<div class="info-box">
<b>📁 데이터 출처</b><br>
• 인플루엔자 의사환자(ILI) 분율 — 질병관리청 (2014-15 ~ 2025-26 시즌)<br>
• 서울 일별 기온 데이터 — 기상청 지점 108 (1907 ~ 2026년)<br><br>
<b>👈 왼쪽 사이드바에서 페이지를 선택하세요.</b>
</div>
""", unsafe_allow_html=True)
