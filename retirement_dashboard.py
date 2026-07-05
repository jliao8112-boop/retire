import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

# ==========================================
# 1. 網頁全域設定與自訂 CSS
# ==========================================
st.set_page_config(page_title="退休提領財務自由模擬面板", layout="wide")

st.markdown("""
<style>
    /* 漸層數據卡片樣式 */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 12px;
        padding: 20px 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        text-align: center;
        border-top: 4px solid #8CB35A;
        margin-bottom: 25px;
        transition: transform 0.2s ease-in-out;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.06);
    }
    .metric-label {
        font-size: 1.05rem;
        color: #6c757d;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: clamp(1.4rem, 2.2vw, 2rem); 
        font-weight: 700;
        color: #2b2d42;
    }
    .status-good { color: #38b000 !important; font-weight: 600; }
    .status-warn { color: #d00000 !important; font-weight: 600; }
    
    /* 戰略評估卡片樣式 */
    .strategy-box {
        padding: 22px;
        border-radius: 12px;
        background-color: #f8f9fa;
        border-left: 6px solid #6c757d;
        margin-bottom: 25px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    .strategy-title { font-size: 1.25rem; font-weight: 700; margin-bottom: 12px; color: #212529;}
    .strategy-text { font-size: 1.05rem; line-height: 1.6; color: #495057; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 側邊欄 (Sidebar) - 參數設定樞紐
# ==========================================
with st.sidebar:
    st.header("⚙️ 核心控制面板")
    st.write("---")
    
    with st.expander("📅 日期與年資設定", expanded=True):
        today_date = st.date_input("今天日期", datetime.date(2026, 7, 5))
        birth_date = st.date_input("出生日期", datetime.date(1984, 1, 1), min_value=datetime.date(1965, 1, 1), max_value=datetime.date(2065, 12, 31))
        start_work_date = st.date_input("開始工作日期", datetime.date(2010, 1, 1), min_value=datetime.date(1980, 1, 1), max_value=datetime.date(2080, 12, 31))
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            military_months = st.number_input("當兵年資(月)", value=0, min_value=0, step=1)
        with col_s2:
            exclude_months = st.number_input("不計年資(月)", value=0, min_value=0, step=1)
            
        retire_age = st.number_input("預定退休年齡 (歲)", value=60, min_value=1, max_value=100, step=1)

    with st.expander("💰 退休前資產累積參數", expanded=True):
        principal = st.number_input("目前初始本金 (元)", value=360000, step=10000)
        annual_contribution = st.number_input("每年預計投入金額 (元)", value=360000, step=10000)
        
        expected_return_rate_pct = st.slider("長期預期報酬率 (%)", min_value=0.0, max_value=50.0, value=7.0, step=0.1)
        expected_return_rate = expected_return_rate_pct / 100

    with st.expander("📉 退休後提領與通膨", expanded=True):
        inflation_rate_pct = st.slider("預估年通膨率 (%)", min_value=0.0, max_value=10.0, value=2.0, step=0.1)
        inflation_rate = inflation_rate_pct / 100
        
        auto_link = st.checkbox("🔗 啟用提領率自動連動", value=True, help="公式：預期報酬率 - 通膨率 - 1% (安全邊際)")
        if auto_link:
            linked_rate = max(0.0, expected_return_rate_pct - inflation_rate_pct - 1.0)
            withdrawal_rate_pct = st.number_input("初始年提領率 (%) [連動中]", value=linked_rate, disabled=True)
        else:
            withdrawal_rate_pct = st.slider("初始年提領率 (%)", min_value=0.0, max_value=15.0, value=4.0, step=0.1)
        withdrawal_rate = withdrawal_rate_pct / 100

    with st.expander("💳 退休現金流檢視 (通用版)", expanded=True):
        monthly_pension = st.number_input("預估每月月退俸 (元)", value=30000, step=5000)
        monthly_expenses = st.number_input("預估退休後每月家庭總支出 (元)", value=80000, step=5000)

# ==========================================
# 3. 核心運算邏輯 (背景處理)
# ==========================================
retire_year = birth_date.year + retire_age
try:
    retire_date = datetime.date(retire_year, birth_date.month, birth_date.day)
except ValueError: 
    retire_date = datetime.date(retire_year, birth_date.month, birth_date.day - 1)

years_to_retire = max(0, retire_year - today_date.year)

base_work_months = (retire_date.year - start_work_date.year) * 12 + (retire_date.month - start_work_date.month)
total_net_months = max(0, base_work_months + military_months - exclude_months)
retire_tenure_years = total_net_months / 12

calc_periods = max(0, years_to_retire - 1)
accumulated_value = principal
for _ in range(calc_periods):
    accumulated_value = accumulated_value * (1 + expected_return_rate) + annual_contribution
retire_starting_principal = int(accumulated_value)

simulation_rows = []
current_balance = retire_starting_principal
initial_withdrawal = int(current_balance * withdrawal_rate)
current_withdrawal = initial_withdrawal

for i in range(1, 51):
    calendar_year = retire_year + i - 1
    investment_income = int(current_balance * expected_return_rate)
    
    if i > 1:
        current_withdrawal = int(current_withdrawal * (1 + inflation_rate))
        
    ending_balance = current_balance + investment_income - current_withdrawal
    
    simulation_rows.append({
        "觀測年度": calendar_year,
        "期初資產本金": current_balance,
        "預期投資收益": investment_income,
        "抗通膨提領金額": current_withdrawal,
        "期末資產結餘": ending_balance
    })
    current_balance = ending_balance

df_simulation = pd.DataFrame(simulation_rows)
final_asset_balance = df_simulation.iloc[-1]["期末資產結餘"]
monthly_payout = int(initial_withdrawal / 12)

# ==========================================
# 4. 主畫面 - 總覽與視覺化
# ==========================================
st.title("退休前的財務規劃")
st.write("---")

st.markdown("### 📊 核心預估指標")
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">預估退休日期</div>
        <div class="metric-value">{retire_date.strftime('%Y/%m/%d')}</div>
        <div style="font-size:0.9rem; color:#888;">(尚有 {years_to_retire} 年)</div>
    </div>
    """, unsafe_allow_html=True)
with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">連動退休年資</div>
        <div class="metric-value">{retire_tenure_years:.2f} <span style="font-size:1.1rem;">年</span></div>
    </div>
    """, unsafe_allow_html=True)
with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">退休啟動本金</div>
        <div class="metric-value">{retire_starting_principal:,} <span style="font-size:1.1rem;">元</span></div>
    </div>
    """, unsafe_allow_html=True)

if final_asset_balance > retire_starting_principal:
    status_text = "資產持續增長"
    status_class = "status-good"
else:
    status_text = "資產有枯竭風險"
    status_class = "status-warn"

with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">月均可提領金額</div>
        <div class="metric-value">{monthly_payout:,} <span style="font-size:1.1rem;">元</span></div>
        <div class="metric-label {status_class}" style="margin-top:5px;">{status_text}</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 5. 退休現金流餘裕與理財戰略評估
# ==========================================
st.markdown("### ⚖️ 退休現金流與理財戰略評估")

total_monthly_income = monthly_pension + monthly_payout
cash_flow_gap = total_monthly_income - monthly_expenses

if cash_flow_gap >= 0:
    strategy_title = "穩定發展，維持現狀"
    strategy_desc = "目前的被動現金流已能完全覆蓋預估支出。建議維持現有步調，耐心在市場量縮時佈局甜甜價，無需刻意追求高風險標的。"
    risk_level = "極低（資產具備高度防禦力）"
    border_color = "#38b000"
elif cash_flow_gap >= -15000:
    strategy_title = "資金緊平衡，需微調收支"
    strategy_desc = "現金流略顯不足。建議在退休前透過本金平均攤還（本金利息一起還）的還款策略加速降低負債，並適度調高每年的投入金額。"
    risk_level = "中度（需嚴守財務紀律，控管每月經常性花費）"
    border_color = "#f5a623"
else:
    strategy_title = "存在顯著缺口，尋求高效標的"
    strategy_desc = "常態現金流無法支撐預估支出。建議利用量化觀測系統尋找獲利更高的板塊（如半導體產業鏈）。務必耐心等待技術面量縮打底，精準買進以拉高整體年化報酬率。"
    risk_level = "較高（具備產業集中度風險，須嚴格執行控管）"
    border_color = "#d00000"

c1, c2, c3 = st.columns(3)
c1.metric("預估每月總進帳 (月退+提領)", f"{total_monthly_income:,} 元")
c2.metric("預估每月家庭支出", f"{monthly_expenses:,} 元")
c3.metric("每月現金流餘額", f"{cash_flow_gap:,} 元", delta_color="normal" if cash_flow_gap >=0 else "inverse")

st.markdown(f"""
<div class="strategy-box" style="border-left-color: {border_color};">
    <div class="strategy-title">💡 系統理財建議：{strategy_title}</div>
    <div class="strategy-text">{strategy_desc}</div>
    <div class="strategy-text" style="margin-top: 10px; font-weight: bold; color: {border_color};">⚠️ 系統風險定等：{risk_level}</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 6. 視覺化圖表與明細 (高階漸層與輔助線質感)
# ==========================================
st.markdown("### 📈 50年資產水位長期變化趨勢")

# 繪製帶有面積漸層的折線圖
fig = px.line(
    df_simulation, 
    x="觀測年度", 
    y="期末資產結餘", 
    template="plotly_white"
)

# 升級質感：加粗線條並填入半透明漸層
fig.update_traces(
    line=dict(color="#8CB35A", width=4), 
    mode='lines',
    fill='tozeroy',
    fillcolor='rgba(140, 179, 90, 0.15)'
)

# 新增輔助線：標示退休啟動本金的「安全底線」
fig.add_hline(
    y=retire_starting_principal,
    line_dash="dash",
    line_color="#d00000",
    annotation_text="退休啟動本金 (資產安全底線)",
    annotation_position="bottom right",
    annotation_font_color="#d00000"
)

# 優化游標懸浮提示 (Hover Tooltip) 與排版
fig.update_layout(
    yaxis_title="資產結餘 (TWD)",
    xaxis_title="觀測年度 (西元)",
    xaxis=dict(dtick=5),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="white", font_size=14),
    margin=dict(l=0, r=0, t=20, b=0)
)
st.plotly_chart(fig, use_container_width=True)

# 資料框架 (DataFrame) 格式化輸出
with st.expander("查看 50 年詳細流水帳資料框架 (DataFrame)", expanded=False):
    df_formatted = df_simulation.copy()
    for col in ["期初資產本金", "預期投資收益", "抗通膨提領金額", "期末資產結餘"]:
        df_formatted[col] = df_formatted[col].map(lambda x: f"{x:,}")
    st.dataframe(df_formatted, use_container_width=True, hide_index=True)