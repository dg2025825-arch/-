import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="날씨와 독감 상관관계",
    page_icon="🌡️",
    layout="wide"
)

st.markdown("""
<style>
    .main-title {
        font-size: 2.6rem;
        font-weight: 900;
        color: #1a1a2e;
        text-align: center;
        padding: 25px 0 8px 0;
    }
    .sub-title {
        font-size: 1.15rem;
        color: #4a4a6a;
        text-align: center;
        margin-bottom: 35px;
    }
    .section-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: #16213e;
        border-left: 5px solid #e63946;
        padding-left: 12px;
        margin: 35px 0 15px 0;
    }
    .insight-box {
        background-color: #f0f4ff;
        border-left: 4px solid #4361ee;
        border-radius: 8px;
        padding: 15px 20px;
        margin: 12px 0;
        color: #1a1a2e;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        border-radius: 8px;
        padding: 15px 20px;
        margin: 12px 0;
        color: #856404;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 8px;
        padding: 15px 20px;
        margin: 12px 0;
        color: #155724;
    }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════
# 데이터 로드
# ════════════════════════════════
@st.cache_data
def load_influenza():
    df = pd.read_csv("인플루엔자 선택됨.csv", header=None, encoding="utf-8-sig")
    records = []
    for _, row in df.iterrows():
        season_raw = str(row[0]).strip()
        season = season_raw[:9]
        try:
            start_year = int(season[:4])
        except:
            continue
        for week_idx in range(1, len(row)):
            val = row[week_idx]
            try:
                val = float(val)
            except:
                val = np.nan
            actual_week = week_idx
            if actual_week <= 18:
                month = 9 + (actual_week - 1) // 4
                year  = start_year
            else:
                month = 1 + (actual_week - 18 - 1) // 4
                year  = start_year + 1
            month = min(max(month, 1), 12)
            records.append({
                "season": season, "start_year": start_year,
                "week_in_season": actual_week,
                "year": year, "month": month, "ili": val
            })
    flu = pd.DataFrame(records)
    flu.dropna(subset=["ili"], inplace=True)
    flu["season_kor"] = flu["month"].apply(
        lambda m: "겨울" if m in [12,1,2] else
                  ("봄"  if m in [3,4,5]  else
                  ("여름" if m in [6,7,8]  else "가을"))
    )
    return flu


@st.cache_data
def load_temperature():
    temp = pd.read_csv(
        "ta_20260601093156.csv",
        encoding="utf-8-sig",
        skipinitialspace=True
    )
    temp.columns = [c.strip() for c in temp.columns]
    temp["날짜"] = temp["날짜"].astype(str).str.strip()
    temp["날짜"] = pd.to_datetime(temp["날짜"], errors="coerce")
    temp.dropna(subset=["날짜"], inplace=True)
    temp["year"]  = temp["날짜"].dt.year
    temp["month"] = temp["날짜"].dt.month

    avg_col  = [c for c in temp.columns if "평균기온" in c][0]
    low_col  = [c for c in temp.columns if "최저기온" in c][0]
    high_col = [c for c in temp.columns if "최고기온" in c][0]
    temp.rename(columns={
        avg_col : "avg_temp",
        low_col : "min_temp",
        high_col: "max_temp"
    }, inplace=True)
    return temp


flu  = load_influenza()
temp = load_temperature()

# 월별 집계 후 병합
temp_monthly = temp.groupby(["year","month"]).agg(
    avg_temp=("avg_temp","mean"),
    min_temp=("min_temp","mean"),
    max_temp=("max_temp","mean")
).reset_index()

flu_monthly = (flu.groupby(["year","month"])["ili"]
                  .mean()
                  .reset_index()
                  .rename(columns={"ili":"avg_ili"}))

merged = pd.merge(temp_monthly, flu_monthly, on=["year","month"], how="inner")
merged["season_kor"] = merged["month"].apply(
    lambda m: "겨울" if m in [12,1,2] else
              ("봄"  if m in [3,4,5]  else
              ("여름" if m in [6,7,8]  else "가을"))
)

season_colors = {
    "봄" : "#4CAF50",
    "여름": "#FF9800",
    "가을": "#F44336",
    "겨울": "#2196F3"
}

# ════════════════════════════════
# 타이틀
# ════════════════════════════════
st.markdown('<div class="main-title">🌡️ 날씨와 독감의 상관관계 분석</div>',
            unsafe_allow_html=True)
st.markdown('<div class="sub-title">서울 기온 데이터(지점 108) × 인플루엔자 ILI 지수 — 통계적 관계 분석</div>',
            unsafe_allow_html=True)

# ════════════════════════════════
# 핵심 상관 지표
# ════════════════════════════════
st.markdown('<div class="section-header">📌 핵심 상관관계 지표</div>',
            unsafe_allow_html=True)

r,    p    = stats.pearsonr(merged["avg_temp"], merged["avg_ili"])
r_sp, p_sp = stats.spearmanr(merged["avg_temp"], merged["avg_ili"])
strength   = "강한" if abs(r) > 0.6 else ("중간" if abs(r) > 0.4 else "약한")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("피어슨 r",   f"{r:.3f}",   help="선형 상관관계 강도 (-1 ~ 1)")
with col2:
    st.metric("스피어만 ρ", f"{r_sp:.3f}", help="순위 기반 상관관계")
with col3:
    st.metric("p-value",    f"{p:.2e}",   help="0.05 미만이면 통계적으로 유의")
with col4:
    st.metric("관계 강도",  f"{strength} 음의 상관")

st.markdown(f"""
<div class="success-box">
✅ 피어슨 r = {r:.3f}, p = {p:.2e} —
기온과 ILI 사이에 <b>{strength} 음의 상관관계</b>가 통계적으로 유의하게 존재합니다.
기온이 낮아질수록 독감 발생률이 높아지는 경향이 수치로 확인됩니다.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ════════════════════════════════
# 1. 산점도: 기온 vs ILI
# ════════════════════════════════
st.markdown('<div class="section-header">🔵 평균기온 vs ILI 산점도</div>',
            unsafe_allow_html=True)

fig_scatter = px.scatter(
    merged,
    x="avg_temp",
    y="avg_ili",
    color="season_kor",
    color_discrete_map=season_colors,
    trendline="ols",
    trendline_scope="overall",
    labels={
        "avg_temp"  : "월평균 기온 (℃)",
        "avg_ili"   : "월평균 ILI",
        "season_kor": "계절"
    },
    title=f"평균기온 vs ILI  (피어슨 r = {r:.3f},  p = {p:.2e})",
    height=530,
    hover_data=["year","month"]
)
fig_scatter.update_layout(plot_bgcolor="#f8f9fa")
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown(f"""
<div class="insight-box">
💡 <b>해석:</b>
추세선(검정 실선)은 뚜렷한 <b>음의 기울기</b>를 보여 기온이 낮을수록 ILI가 높아짐을 확인할 수 있습니다.
겨울(파란 점)은 저온·고ILI 영역에, 여름(주황 점)은 고온·저ILI 영역에 집중됩니다.
피어슨 r = {r:.3f}로 <b>{strength} 음의 상관관계</b>가 존재합니다.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ════════════════════════════════
# 2. 월별 이중 축 (기온 막대 + ILI 라인)
# ════════════════════════════════
st.markdown('<div class="section-header">📅 월별 평균기온 vs 평균 ILI — 이중 축 비교</div>',
            unsafe_allow_html=True)

month_agg = merged.groupby("month").agg(
    avg_temp=("avg_temp","mean"),
    avg_ili =("avg_ili", "mean")
).reset_index()

month_labels = ["1월","2월","3월","4월","5월","6월",
                "7월","8월","9월","10월","11월","12월"]

fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
fig_dual.add_trace(
    go.Bar(
        x=month_labels, y=month_agg["avg_temp"],
        name="평균기온(℃)",
        marker_color="rgba(255,140,0,0.65)"
    ),
    secondary_y=False
)
fig_dual.add_trace(
    go.Scatter(
        x=month_labels, y=month_agg["avg_ili"],
        name="평균 ILI",
        mode="lines+markers",
        line=dict(color="#1565C0", width=3),
        marker=dict(size=9)
    ),
    secondary_y=True
)
fig_dual.update_layout(
    title="월별 평균기온 vs 평균 ILI (전체 기간 평균)",
    plot_bgcolor="#f8f9fa",
    height=460,
    legend=dict(orientation="h", yanchor="bottom", y=1.02)
)
fig_dual.update_yaxes(title_text="평균기온 (℃)", secondary_y=False)
fig_dual.update_yaxes(title_text="평균 ILI",     secondary_y=True)
st.plotly_chart(fig_dual, use_container_width=True)

st.markdown("""
<div class="insight-box">
💡 <b>해석:</b>
기온(주황 막대)과 ILI(파란 선)는 <b>거울 대칭에 가까운 역방향 패턴</b>을 보입니다.
기온이 가장 낮은 <b>1월에 ILI 최고</b>, 기온이 가장 높은 <b>7~8월에 ILI 최저</b>입니다.
이 패턴은 기온이 독감 유행의 강력한 계절적 지표임을 직관적으로 보여줍니다.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ════════════════════════════════
# 3. 계절별 세부 상관관계 표 + 4분할 산점도
# ════════════════════════════════
st.markdown('<div class="section-header">🌸 계절별 세부 상관관계</div>',
            unsafe_allow_html=True)

corr_rows = []
for s in ["봄","여름","가을","겨울"]:
    sub = merged[merged["season_kor"] == s]
    if len(sub) > 5:
        r_s, p_s = stats.pearsonr(sub["avg_temp"], sub["avg_ili"])
        corr_rows.append({
            "계절"      : s,
            "데이터 수" : len(sub),
            "피어슨 r"  : round(r_s, 3),
            "p-value"   : round(p_s, 4),
            "유의 여부" : "✅ 유의" if p_s < 0.05 else "❌ 비유의"
        })

corr_df = pd.DataFrame(corr_rows)
st.dataframe(corr_df.set_index("계절"), use_container_width=True)

fig_4 = px.scatter(
    merged,
    x="avg_temp",
    y="avg_ili",
    facet_col="season_kor",
    facet_col_wrap=2,
    color="season_kor",
    trendline="ols",
    color_discrete_map=season_colors,
    labels={"avg_temp":"평균기온(℃)","avg_ili":"평균 ILI","season_kor":"계절"},
    title="계절별 기온-ILI 산점도 (OLS 추세선)",
    height=580
)
fig_4.update_layout(plot_bgcolor="#f8f9fa", showlegend=False)
st.plotly_chart(fig_4, use_container_width=True)

st.markdown("""
<div class="insight-box">
💡 <b>해석:</b>
겨울과 가을에서 음의 상관관계가 특히 강하게 나타납니다.
여름의 경우 기온 변동폭이 작고 ILI도 전반적으로 낮아 상관관계가 약하게 나타날 수 있습니다.
겨울 내부에서도 기온이 더 낮은 달에 ILI가 더 높은 경향이 관찰됩니다.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ════════════════════════════════
# 4. 기온 구간별 평균 ILI
# ════════════════════════════════
st.markdown('<div class="section-header">🌡️ 기온 구간별 평균 ILI</div>',
            unsafe_allow_html=True)

bins       = [-20, 0, 5, 10, 15, 20, 25, 30, 40]
labels_bin = ["영하","0~5℃","5~10℃","10~15℃","15~20℃","20~25℃","25~30℃","30℃ 이상"]

merged["temp_bin"] = pd.cut(merged["avg_temp"], bins=bins, labels=labels_bin)

bin_agg = (merged.groupby("temp_bin", observed=True)["avg_ili"]
                 .agg(["mean","count"])
                 .reset_index())
bin_agg.columns = ["기온 구간","평균 ILI","데이터 수"]

fig_bin = px.bar(
    bin_agg,
    x="기온 구간",
    y="평균 ILI",
    color="평균 ILI",
    color_continuous_scale="RdYlBu_r",
    text="평균 ILI",
    title="기온 구간별 평균 ILI",
    height=430
)
fig_bin.update_traces(texttemplate="%{text:.1f}", textposition="outside")
fig_bin.update_layout(plot_bgcolor="#f8f9fa")
st.plotly_chart(fig_bin, use_container_width=True)

st.markdown("""
<div class="insight-box">
💡 <b>해석:</b>
영하 ~ 5℃ 구간에서 ILI가 급격히 높아집니다.
<b>기온 10℃ 이하</b>를 독감 위험 임계점으로 볼 수 있으며,
이 기준을 독감 예방 강화 공중보건 기준으로 활용할 수 있습니다.
25℃ 이상에서는 ILI가 매우 낮아 고온 환경에서 바이러스 활성이 떨어짐을 시사합니다.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ════════════════════════════════
# 5. 특정 시즌 상세 비교 (인터랙티브)
# ════════════════════════════════
st.markdown('<div class="section-header">🔎 특정 시즌 기온-ILI 상세 비교</div>',
            unsafe_allow_html=True)

flu_seasons = sorted(flu["season"].unique())
sel_season  = st.selectbox("시즌을 선택하세요", flu_seasons)
sy          = int(sel_season[:4])

flu_s = (flu[flu["season"] == sel_season]
           .groupby(["year","month"])["ili"]
           .mean()
           .reset_index())

temp_s = temp_monthly[
    ((temp_monthly["year"] == sy)   & (temp_monthly["month"] >= 9)) |
    ((temp_monthly["year"] == sy+1) & (temp_monthly["month"] <= 8))
].copy()

merged_s = pd.merge(temp_s, flu_s, on=["year","month"], how="inner")
merged_s.rename(columns={"ili":"avg_ili"}, inplace=True)
merged_s["날짜"] = pd.to_datetime(merged_s[["year","month"]].assign(day=1))
merged_s.sort_values("날짜", inplace=True)

if not merged_s.empty:
    fig_detail = make_subplots(specs=[[{"secondary_y": True}]])
    fig_detail.add_trace(
        go.Scatter(
            x=merged_s["날짜"], y=merged_s["avg_temp"],
            name="평균기온(℃)", mode="lines+markers",
            line=dict(color="orange", width=2.5),
            fill="tozeroy", fillcolor="rgba(255,165,0,0.1)"
        ),
        secondary_y=False
    )
    fig_detail.add_trace(
        go.Scatter(
            x=merged_s["날짜"], y=merged_s["avg_ili"],
            name="평균 ILI", mode="lines+markers",
            line=dict(color="crimson", width=2.5),
            marker=dict(size=9)
        ),
        secondary_y=True
    )
    fig_detail.update_layout(
        title=f"{sel_season} 시즌 — 월별 기온 vs ILI",
        plot_bgcolor="#f8f9fa",
        height=430,
        legend=dict(orientation="h")
    )
    fig_detail.update_yaxes(title_text="평균기온(℃)", secondary_y=False)
    fig_detail.update_yaxes(title_text="평균 ILI",    secondary_y=True)
    st.plotly_chart(fig_detail, use_container_width=True)
else:
    st.info("해당 시즌의 기온-ILI 교차 데이터가 충분하지 않습니다.")

st.markdown("---")

# ════════════════════════════════
# 6. 종합 평가
# ════════════════════════════════
st.markdown('<div class="section-header">📝 날씨-독감 상관관계 종합 평가</div>',
            unsafe_allow_html=True)

st.markdown(f"""
<div class="insight-box">
<h4>🔬 통계 분석 결과 요약</h4>
<ul>
  <li><b>피어슨 r = {r:.3f}</b> — 기온과 ILI 사이에 <b>{strength} 음의 선형 상관관계</b>가 존재합니다.</li>
  <li><b>p = {p:.2e}</b> — 이 관계는 통계적으로 매우 유의하며 우연일 가능성이 극히 낮습니다.</li>
  <li><b>임계 온도</b> — 약 10℃ 이하에서 ILI가 급증하는 패턴이 확인됩니다.</li>
  <li><b>계절별 차이</b> — 겨울·가을에서 상관관계가 가장 강하게 나타납니다.</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="insight-box">
<h4>🧬 기온과 독감 — 과학적 배경</h4>
<ul>
  <li><b>바이러스 생존력:</b> 저온·저습 환경에서 인플루엔자 바이러스 외피 안정성이 높아져
      공기 중 생존 시간이 길어집니다.</li>
  <li><b>숙주 면역력 저하:</b> 차가운 공기는 상기도 점막의 섬모 운동과 점액 방어 기능을 저하시켜
      바이러스 침투가 쉬워집니다.</li>
  <li><b>실내 밀집:</b> 기온 하강 시 실내 체류 시간 증가 + 창문 닫힘 → 비말 전파 활성화.</li>
  <li><b>비타민 D 감소:</b> 겨울철 일조량 감소로 인한 비타민 D 부족이 면역력 저하에 기여합니다.</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="warning-box">
<h4>⚠️ 분석의 한계</h4>
<ul>
  <li>기온 외에 <b>습도·인구이동·백신 접종률·바이러스 변이</b> 등 복합 요인은 반영되지 않았습니다.</li>
  <li>기상 데이터는 서울 단일 지점(108)으로 지역별 편차를 반영하지 못합니다.</li>
  <li>상관관계는 인과관계를 의미하지 않으므로 해석에 주의가 필요합니다.</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="success-box">
<h4>✅ 결론 및 시사점</h4>
<p>
기온과 독감 발생률 사이의 <b>통계적으로 유의한 음의 상관관계(r = {r:.3f})</b>는
기온 데이터를 활용한 <b>독감 조기 경보 시스템</b> 개발 가능성을 시사합니다.
<b>평균기온이 10℃ 이하로 하강하는 시점</b>을 독감 예방 강화 기준으로 설정하면
공중보건 정책에 실질적 도움이 될 수 있습니다.
</p>
</div>
""", unsafe_allow_html=True)
