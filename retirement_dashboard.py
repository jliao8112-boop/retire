import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

# ==========================================
# 1. 網頁全域設定與自訂 CSS (美化版面與自適應字體)
# ==========================================
st.set_page_config(page_title="退休提領財務自由模擬面板", layout="wide")

st.markdown("""
<style>
    /* 漸層數據卡片樣式 */
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
    /* 自適應字體大小，隨螢幕縮放 */
    .metric-value {
        font-size: clamp(1.5rem, 2.5vw, 2.2rem); 
        font-weight: 700;
        color: #2b2d42;
    }
    .status-good { color: #38b000 !important; }
    .status-warn { color: #d00000 !important; }
</style>
""", unsafe_allow_html=True)

st.title("ETF資產與退休提領的財務自由模擬面板")
st.write("---")

# ==========================================
# 2. 參數輸入區 (簡潔網格佈局)
# ==========================================
st.subheader("⚙️ 參數設定區")

# 第一列輸入 (日期)
col1, col2 = st.columns(2)
with col1:
    today_date = st.date_input("今天日期", datetime.date(2026, 7, 5))
with col2:
    birth_date = st.date_input("出生日期", datetime.date(1984, 1, 1), min_value=datetime.date(1965, 1, 1), max_value=datetime.date(2065, 12, 31))

start_work_date = st.date_input("開始工作日期", datetime.date(2010, 1, 1))

# 第二列輸入 (年資與退休年齡)
col3, col4, col5 = st.columns(3)
with col3:
    military_months = st.number_input("當兵年資 (月)", value=0, min_value=0, step=1)
with col4:
    exclude_months = st.number_input("不計年資 (月)", value=0, min_value=0, step=1)
with col5:
    retire_age = st.number_input("退休年齡 (歲)", value=60, min_value=1, max_value=100, step=1)

# 第三列輸入 (資金)
col6, col7 = st.columns(2)
with col6:
    principal = st.number_input("初始本金 (元)", value=3600000, step=100000)
with col7:
    annual_contribution = st.number_input("每年投入金額 (元)", value=360000, step=10000)

# 第四列輸入 (比率滑桿)
col8, col9, col10 = st.columns(3)
with col8:
    expected_return_rate = st.slider("預期報酬率 (%)", min_value=0.0, max_value=50.0, value=7.0, step=0.1) / 100
with col9:
    withdrawal_rate = st.slider("初始提領率 (%)", min_value=0.0, max_value=15.0, value=4.0, step=0.1) / 100
with col10:
    inflation_rate = st.slider("預估通膨率 (%)", min_value=0.0, max_value=10.0, value=2.0, step=0.1) / 100

st.write("---")

# ==========================================
# 3. 核心運算邏輯 (包含 -1 年校正)
# ==========================================
# 推算退休日期
retire_year = birth_date.year + retire_age
try:
    retire_date = datetime.date(retire_year, birth_date.month, birth_date.day)
except ValueError: # 處理 2/29 閏年問題
    retire_date = datetime.date(retire_year, birth_date.month, birth_date.day - 1)

years_to_retire = max(0, retire_year - today_date.year)

# 聯動退休年資計算
base_work_months = (retire_date.year - start_work_date.year) * 12 + (retire_date.month - start_work_date.month)
total_net_months = max(0, base_work_months + military_months - exclude_months)
retire_tenure_years = total_net_months / 12

# 【核心修正】退休啟動本金計算 (實務保留最後一年彈性，迴圈次數 = 距離年數 - 1)
calc_periods = max(0, years_to_retire - 1)
accumulated_value = principal
for _ in range(calc_periods):
    accumulated_value = accumulated_value * (1 + expected_return_rate) + annual_contribution
retire_starting_principal = int(accumulated_value)

# 提領期 50 年模擬計算
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

# 狀態判斷
if final_asset_balance > retire_starting_principal:
    status_text = "資產持續增長 (永遠花不完)"
    status_class = "status-good"
else:
    status_text = "資產有枯竭風險"
    status_class = "status-warn"

# ==========================================
# 4. 頂部狀態列 (漸層數據卡片輸出)
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
with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">月均可提領金額</div>
        <div class="metric-value">{monthly_payout:,} <span style="font-size:1.2rem;">元</span></div>
        <div class="metric-label {status_class}" style="margin-top:5px;">{status_text}</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 5. 視覺化圖表與明細
# ==========================================
st.subheader("📈 50年資產水位長期變化趨勢")

# 繪製平滑折線圖
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

# 資料表格式化輸出
with st.expander("查看 50 年詳細流水帳數據", expanded=False):
    df_formatted = df_simulation.copy()
    for col in ["期初資產本金", "預期投資收益", "抗通膨提領金額", "期末資產結餘"]:
        df_formatted[col] = df_formatted[col].map(lambda x: f"{x:,}")
    st.dataframe(df_formatted, use_container_width=True, hide_index=True)