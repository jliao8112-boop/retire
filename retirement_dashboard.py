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
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f1f3f5 100%);
        border-radius: 12px;
        padding: 20px 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        text-align: center;
        border-top: 4px solid #8CB35A;
        margin-bottom: 25px;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
    }
    .metric-label {
        font-size: 1.1rem;
        color: #6c757d;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: clamp(1.5rem, 2.5vw, 2.2rem); 
        font-weight: 700;
        color: #2b2d42;
    }
    .status-good { color: #38b000 !important; }
    .status-warn { color: #d00000 !important; }
    
    /* 戰略評估卡片樣式 */
    .strategy-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #f8f9fa;
        border-left: 6px solid #6c757d;
        margin-bottom: 20px;
    }
    .strategy-title { font-size: 1.3rem; font-weight: 700; margin-bottom: 10px; }
    .strategy-text { font-size: 1.05rem; line-height: 1.6; color: #495057; }
</style>
""", unsafe_allow_html=True)

st.title("ETF資產與退休提領的財務自由模擬面板")
st.write("---")

# ==========================================
# 2. 參數輸入區
# ==========================================
st.subheader("⚙️ 參數設定區")

col1, col2 = st.columns(2)
with col1:
    today_date = st.date_input("今天日期", datetime.date(2026, 7, 5))
with col2:
    birth_date = st.date_input("出生日期", datetime.date(1984, 1, 1), min_value=datetime.date(1965, 1, 1), max_value=datetime.date(2065, 12, 31))

start_work_date = st.date_input("開始工作日期", datetime.date(2010, 1, 1))

col3, col4, col5 = st.columns(3)
with col3:
    military_months = st.number_input("當兵年資 (月)", value=0, min_value=0, step=1)
with col4:
    exclude_months = st.number_input("不計年資 (月)", value=0, min_value=0, step=1)
with col5:
    retire_age = st.number_input("退休年齡 (歲)", value=60, min_value=1, max_value=100, step=1)

col6, col7 = st.columns(2)
with col6:
    principal = st.number_input("初始本金 (元)", value=360000, step=100000)
with col7:
    annual_contribution = st.number_input("每年投入金額 (元)", value=360000, step=10000)

col8, col9, col10 = st.columns(3)
with col8:
    expected_return_rate_pct = st.slider("預期報酬率 (%)", min_value=0.0, max_value=50.0, value=7.0, step=0.1)
    expected_return_rate = expected_return_rate_pct / 100
with col10:
    inflation_rate_pct = st.slider("預估通膨率 (%)", min_value=0.0, max_value=10.0, value=2.0, step=0.1)
    inflation_rate = inflation_rate_pct / 100
with col9:
    auto_link = st.checkbox("🔗 啟用提領率自動連動", value=True, help="公式：預期報酬率 - 通膨率 - 1% (安全邊際)")
    if auto_link:
        linked_rate = max(0.0, expected_return_rate_pct - inflation_rate_pct - 1.0)
        withdrawal_rate_pct = st.number_input("初始提領率 (%) [連動中]", value=linked_rate, disabled=True)
    else:
        withdrawal_rate_pct = st.slider("初始提領率 (%)", min_value=0.0, max_value=15.0, value=4.0, step=0.1)
    withdrawal_rate = withdrawal_rate_pct / 100

st.write("---")
st.markdown("#### 🔹 退休後現金流與生活支出設定 (通用版)")
col11, col12 = st.columns(2)
with col11:
    monthly_pension = st.number_input("預估每月月退俸 (元)", value=30000, step=5000)
with col12:
    monthly_expenses = st.number_input("預估退休後每月家庭總支出 (元)", value=80000, step=5000)

st.write("---")

# ==========================================
# 3. 核心運算邏輯
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
# 4. 頂部狀態列
# ==========================================
st.subheader("📊 核心預估指標")
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
        <div class="metric-value">{retire_tenure_years:.2f} <span style="font-size:1.2rem;">年</span></div>
    </div>
    """, unsafe_allow_html=True)
with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">退休啟動本金</div>
        <div class="metric-value">{retire_starting_principal:,} <span style="font-size:1.2rem;">元</span></div>
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
        <div class="metric-value">{monthly_payout:,} <span style="font-size:1.2rem;">元</span></div>
        <div class="metric-label {status_class}" style="margin-top:5px;">{status_text}</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 5. 退休現金流餘裕與理財戰略評估
# ==========================================
st.subheader("⚖️ 退休現金流與理財戰略評估")

total_monthly_income = monthly_pension + monthly_payout
cash_flow_gap = total_monthly_income - monthly_expenses

# 依據資金缺口決定戰略與風險定等
if cash_flow_gap >= 0:
    strategy_title = "穩定發展，維持現狀"
    strategy_desc = "目前的被動現金流已能完全覆蓋預估支出。建議維持現有步調，將核心資金持續配置於全市場大盤指數股票型基金（如 006208），享受市場長期的穩定增長，不需刻意追求高風險標的。"
    risk_level = "極低（資產具備高度防禦力）"
    border_color = "#38b000"
elif cash_flow_gap >= -15000:
    strategy_title = "資金緊平衡，需調整收支"
    strategy_desc = "現金流略顯不足，任何非計畫性的開銷都可能侵蝕老本。建議在退休前透過「本金平均攤還（本金利息一起還）」的還款策略加速降低負債利息，並適度調高每年的投入金額與存款，提前加深資金池。"
    risk_level = "中度（需嚴守財務紀律，控管每月經常性花費）"
    border_color = "#f5a623"
else:
    strategy_title = "存在顯著缺口，尋求高效標的"
    strategy_desc = "常態現金流無法支撐預估支出。建議在原有的大盤配置外，利用量化觀測系統尋找獲利更高的板塊（如半導體、人工智慧產業鏈）。務必耐心等待技術面量縮打底，精準買進甜甜價，以拉高整體年化報酬率。"
    risk_level = "較高（具備產業集中度風險，須嚴格執行停損與控管投資部位）"
    border_color = "#d00000"

# 顯示比較數據與戰略卡片
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
# 6. 視覺化圖表與明細
# ==========================================
st.subheader("📈 50年資產水位長期變化趨勢")

fig = px.line(
    df_simulation, 
    x="觀測年度", 
    y="期末資產結餘", 
    template="plotly_white"
)
fig.update_traces(line=dict(color="#8CB35A", width=4), mode='lines')
fig.update_layout(
    yaxis_title="資產結餘 (TWD)",
    xaxis_title="觀測年度 (西元)",
    xaxis=dict(dtick=5),
    hovermode="x unified",
    margin=dict(l=0, r=0, t=30, b=0)
)
st.plotly_chart(fig, use_container_width=True)

with st.expander("查看 50 年詳細流水帳數據", expanded=False):
    df_formatted = df_simulation.copy()
    for col in ["期初資產本金", "預期投資收益", "抗通膨提領金額", "期末資產結餘"]:
        df_formatted[col] = df_formatted[col].map(lambda x: f"{x:,}")
    st.dataframe(df_formatted, use_container_width=True, hide_index=True)