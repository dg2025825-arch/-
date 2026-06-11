import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="계절별 독감 발생률 분석",
    page_icon="🦠",
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
        border-left: 5px solid #0f3460;
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
                "season"        : season,
                "start_year"    : start_year,
                "week_in_season": actual_week,
                "year"          : year,
                "month"         : month,
                "ili"           : val
            })

    flu = pd.DataFrame(records)
    flu.dropna(subset=["ili"], inplace=True)

    flu["season_kor"] = flu["month"].apply(
        lambda m: "겨울" if m in [12,1,2] else
                  ("봄"  if m in [3,4,5]  else
                  ("여름" if m in [6,7,8]  else "가을"))
    )
    return flu


flu = load_influenza()

season_order  = ["봄", "여름", "가을", "겨울"]
season_colors = {
    "봄" : "#4CAF50",
    "여름": "#FF9800",
    "가을": "#F44336",
    "겨울": "#2196F3"
}

# ════════════════════════════════
# 타이틀
# ════════════════════════════════
st.markdown('<div class="main-title">🦠 계절별 독감 발생률 분석</div>',
            unsafe_allow_html=True)
st.markdown('<div class="sub-title">질병관리청 인플루엔자 의사환자(ILI) 분율 데이터 기반 | 2014-15 ~ 2025-26 시즌</div>',
            unsafe_allow_html=True)

# ════════════════════════════════
# 핵심 지표 4개
# ════════════════════════════════
st.markdown('<div class="section-header">📌 핵심 통계 요약</div>',
            unsafe_allow_html=True)

season_avg  = flu.groupby("season_kor")["ili"].mean()
overall_max = flu["ili"].max()
max_row     = flu.loc[flu["ili"].idxmax()]
total_seasons = flu["season"].nunique()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📈 전체 최고 ILI",   f"{overall_max:.1f}")
with col2:
    st.metric("🏔️ 최고 발생 시즌",  max_row["season"])
with col3:
    st.metric("❄️ 겨울 평균 ILI",   f"{season_avg.get('겨울', 0):.1f}")
with col4:
    st.metric("☀️ 여름 평균 ILI",   f"{season_avg.get('여름', 0):.1f}")

st.markdown("---")

# ════════════════════════════════
# 1. 시즌별 ILI 주간 추이 (라인차트)
# ════════════════════════════════
st.markdown('<div class="section-header">📈 시즌별 ILI 주간 추이</div>',
            unsafe_allow_html=True)

all_seasons = sorted(flu["season"].unique())
selected    = st.multiselect("시즌 선택 (복수 가능)", options=all_seasons, default=all_seasons)
filtered    = flu[flu["season"].isin(selected)]

fig_line = px.line(
    filtered,
    x="week_in_season",
    y="ili",
    color="season",
    labels={
        "week_in_season": "시즌 내 주차",
        "ili"           : "ILI (외래환자 1000명당)",
        "season"        : "시즌"
    },
    title="시즌별 ILI 주간 추이",
    height=500
)
fig_line.add_hline(
    y=6.6,
    line_dash="dash",
    line_color="red",
    annotation_text="유행 기준 (6.6)",
    annotation_position="top right"
)
fig_line.update_layout(
    plot_bgcolor="#f8f9fa",
    paper_bgcolor="white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig_line, use_container_width=True)

st.markdown("""
<div class="insight-box">
💡 <b>해석:</b>
빨간 점선(유행 기준 ILI = 6.6)을 초과하는 구간이 실질적 독감 유행 시기입니다.
대부분의 시즌에서 <b>15~30주차(12월~2월, 겨울)</b>에 최고점을 기록합니다.
특히 2016-2017 시즌은 1월 초 조기 폭증(86.2), 2024-2025 시즌은 최대 99.8을 기록하며
역대 최고 수준을 보였습니다.
코로나19 대유행 시기(2020-21·2021-22)에는 방역 조치의 영향으로 독감이 사실상 소멸 수준으로 억제되었습니다.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ════════════════════════════════
# 2. 계절별 평균 ILI 막대 + 박스플롯
# ════════════════════════════════
st.markdown('<div class="section-header">🌸 계절별 평균 ILI 비교</div>',
            unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    season_means = (flu.groupby("season_kor")["ili"]
                       .agg(["mean","std"])
                       .reindex(season_order))

    fig_bar = go.Figure()
    for s in season_order:
        r_ = season_means.loc[s]
        fig_bar.add_trace(go.Bar(
            name=s,
            x=[s],
            y=[r_["mean"]],
            error_y=dict(type="data", array=[r_["std"]], visible=True),
            marker_color=season_colors[s],
            text=f'{r_["mean"]:.1f}',
            textposition="outside"
        ))
    fig_bar.update_layout(
        title="계절별 평균 ILI (± 표준편차)",
        yaxis_title="평균 ILI",
        showlegend=False,
        height=400,
        plot_bgcolor="#f8f9fa"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_b:
    fig_box = px.box(
        flu,
        x="season_kor",
        y="ili",
        color="season_kor",
        category_orders={"season_kor": season_order},
        color_discrete_map=season_colors,
        title="계절별 ILI 분포 (Box Plot)",
        labels={"season_kor":"계절","ili":"ILI"},
        height=400
    )
    fig_box.update_layout(showlegend=False, plot_bgcolor="#f8f9fa")
    st.plotly_chart(fig_box, use_container_width=True)

st.markdown("""
<div class="insight-box">
💡 <b>해석:</b>
겨울 평균 ILI가 여름 대비 약 <b>4~6배</b> 높게 나타납니다.
박스플롯에서 겨울의 상한선(최대값)이 매우 높고 분포도 넓어,
해마다 유행 강도의 편차가 크다는 것을 알 수 있습니다.
반면 여름은 ILI가 낮고 분포도 좁아 안정적입니다.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ════════════════════════════════
# 3. 시즌 × 월 히트맵
# ════════════════════════════════
st.markdown('<div class="section-header">🗓️ 시즌 × 월별 ILI 히트맵</div>',
            unsafe_allow_html=True)

pivot = flu.pivot_table(values="ili", index="season", columns="month", aggfunc="mean")
pivot = pivot.reindex(columns=list(range(1, 13)))

fig_heat = px.imshow(
    pivot,
    labels=dict(x="월", y="시즌", color="ILI"),
    x=[f"{m}월" for m in range(1, 13)],
    color_continuous_scale="RdYlBu_r",
    title="시즌 × 월별 평균 ILI 히트맵",
    height=480
)
fig_heat.update_layout(plot_bgcolor="#f8f9fa")
st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("""
<div class="insight-box">
💡 <b>해석:</b>
짙은 붉은색(고위험)이 <b>1~2월</b>에 집중됩니다.
2020-21·2021-22 시즌은 전체적으로 색이 옅어 코로나19 방역 조치의 효과를 시각적으로 확인할 수 있습니다.
2022-23 시즌부터 다시 붉어지며 독감이 재확산되는 양상이 뚜렷합니다.
2025-26 시즌은 가을(10~11월)부터 이미 붉은색을 띠어 <b>조기 유행</b> 패턴이 주목됩니다.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ════════════════════════════════
# 4. 시즌별 최고 ILI & 유행 지속 기간
# ════════════════════════════════
st.markdown('<div class="section-header">🏆 시즌별 최고 ILI 및 유행 지속 기간</div>',
            unsafe_allow_html=True)

threshold    = 6.6
summary_rows = []
for s in all_seasons:
    s_df     = flu[flu["season"] == s]
    peak     = s_df["ili"].max()
    duration = int((s_df["ili"] >= threshold).sum())
    summary_rows.append({
        "시즌"             : s,
        "최고 ILI"         : round(peak, 1),
        "유행 지속 기간(주)": duration
    })

summary_df = pd.DataFrame(summary_rows)

col_c, col_d = st.columns(2)

with col_c:
    fig_peak = px.bar(
        summary_df,
        x="시즌", y="최고 ILI",
        color="최고 ILI",
        color_continuous_scale="Reds",
        title="시즌별 최고 ILI",
        text="최고 ILI",
        height=420
    )
    fig_peak.add_hline(y=threshold, line_dash="dash", line_color="navy",
                       annotation_text=f"유행 기준 ({threshold})")
    fig_peak.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig_peak.update_layout(plot_bgcolor="#f8f9fa", xaxis_tickangle=-30)
    st.plotly_chart(fig_peak, use_container_width=True)

with col_d:
    fig_dur = px.bar(
        summary_df,
        x="시즌", y="유행 지속 기간(주)",
        color="유행 지속 기간(주)",
        color_continuous_scale="Blues",
        title="시즌별 유행 지속 기간(주)",
        text="유행 지속 기간(주)",
        height=420
    )
    fig_dur.update_traces(texttemplate="%{text}주", textposition="outside")
    fig_dur.update_layout(plot_bgcolor="#f8f9fa", xaxis_tickangle=-30)
    st.plotly_chart(fig_dur, use_container_width=True)

st.dataframe(summary_df.set_index("시즌"), use_container_width=True)

st.markdown("""
<div class="insight-box">
💡 <b>해석:</b>
2024-2025 시즌은 최고 ILI 99.8로 역대 최고를 기록했으며,
2018-2019 시즌은 유행 지속 기간이 가장 길었습니다.
2020-2022 시즌은 유행 기준을 넘지 못한 사실상 독감 소멸 시기였습니다.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ════════════════════════════════
# 5. 종합 분석 및 평가
# ════════════════════════════════
st.markdown('<div class="section-header">📝 종합 분석 및 평가</div>',
            unsafe_allow_html=True)

st.markdown("""
<div class="insight-box">
<h4>🔍 주요 발견 사항</h4>
<ul>
  <li><b>강한 계절성:</b> 인플루엔자는 매년 겨울철(12~2월)에 집중 발생하며,
      여름(6~8월)에는 발생률이 현저히 낮아지는 뚜렷한 계절 패턴을 보입니다.</li>
  <li><b>유행 강도 해마다 다름:</b> 시즌별 최고 ILI는 최저 약 2(코로나 시기)에서
      최고 99.8(2024-25)까지 매우 큰 편차를 보입니다.</li>
  <li><b>코로나19 방역의 독감 억제 효과:</b> 2020-2022년 마스크 착용·사회적 거리두기 시행 기간 동안
      독감 유행이 사실상 소멸되었습니다. 이는 비약물적 개입이 독감 억제에도 매우 효과적임을 보여주는
      자연 실험 사례입니다.</li>
  <li><b>방역 해제 후 반등:</b> 2022-23 시즌부터 독감이 빠르게 재유행하였고,
      2023-24·2024-25 시즌에는 대규모 유행이 다시 발생했습니다.</li>
  <li><b>2025-26 시즌 이상 조기 유행:</b> 통상 12~1월에 정점을 찍는 독감이 이 시즌에는
      9~11월부터 이례적으로 높은 수치(50~70대)를 기록하고 있어 주목이 필요합니다.</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="warning-box">
<h4>⚠️ 데이터 유의사항</h4>
<ul>
  <li>ILI(인플루엔자 의사환자)는 실제 확진자 수가 아닌
      <b>외래환자 1000명당 의심 증상자 비율</b>로, 실제 감염 규모와 차이가 있을 수 있습니다.</li>
  <li>일부 주차에 결측값이 존재하며 본 분석에서는 해당 값을 제외하였습니다.</li>
  <li>주차 → 월 변환은 근사치입니다.</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="success-box">
<h4>✅ 결론</h4>
<p>
인플루엔자는 <b>뚜렷한 겨울 집중형 계절 감염병</b>입니다.
매년 11월부터 예방접종을 완료하고, 12월~2월에는 손 씻기·환기·마스크 착용 등
개인 위생을 강화하는 것이 데이터로 입증된 가장 효과적인 예방 전략입니다.
</p>
</div>
""", unsafe_allow_html=True)
