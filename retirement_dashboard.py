import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go
import plotly.express as px

# ==========================================
# 1. 網頁全域設定與自訂 CSS
# ==========================================
st.set_page_config(page_title="通用版家庭財務戰情中心", layout="wide", page_icon="🏦")

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 12px;
        padding: 20px 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        text-align: center;
        border-top: 4px solid #457b9d;
        margin-bottom: 20px;
    }
    .metric-label { font-size: 1.05rem; color: #6c757d; font-weight: 600; margin-bottom: 8px; }
    .metric-value { font-size: clamp(1.4rem, 2vw, 1.8rem); font-weight: 700; color: #1d3557; }
    .status-excellent { color: #2a9d8f !important; font-weight: bold; }
    .status-warning { color: #e9c46a !important; font-weight: bold; }
    .status-danger { color: #e63946 !important; font-weight: bold; }
    .strategy-box {
        padding: 22px;
        border-radius: 12px;
        background-color: #f8f9fa;
        border-left: 6px solid #457b9d;
        margin-bottom: 25px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    .strategy-title { font-size: 1.25rem; font-weight: 700; margin-bottom: 12px; color: #1d3557;}
    .strategy-text { font-size: 1.05rem; line-height: 1.6; color: #495057; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 側邊欄：通用版家庭資產負債輸入區
# ==========================================
with st.sidebar:
    st.header("⚙️ 家庭財務參數輸入")
    
    with st.expander("💼 家庭收支現況 (年計)", expanded=True):
        annual_income = st.number_input("家庭年總收入 (元)", value=1900000, step=50000)
        annual_expense = st.number_input("家庭年總支出 (含食衣住行育樂) (元)", value=900000, step=50000)
        annual_debt_pay = st.number_input("年固定還款總額 (房貸/車貸) (元)", value=320000, step=10000)
        
    with st.expander("🏦 資產與負債盤點", expanded=True):
        cash_assets = st.number_input("高流動性現金存款 (元)", value=1000000, step=50000)
        invest_assets = st.number_input("目前金融投資資產 (股票/ETF) (元)", value=9000000, step=100000)
        real_estate_value = st.number_input("不動產現值 (自住+投資) (元)", value=15000000, step=500000)
        total_debt = st.number_input("總負債餘額 (房貸+信貸+車貸) (元)", value=1600000, step=100000)
        
    with st.expander("🎯 退休模擬參數", expanded=True):
        years_to_retire = st.slider("距離主要退休尚有幾年？", 0, 40, 9)
        post_retire_expense = st.number_input("預估退休後『每月』支出 (元)", value=75000, step=5000)
        monthly_pension = st.number_input("預估退休後『每月』總被動收入/月退俸", value=70000, step=5000)
        expected_return = st.slider("投資組合預期年化報酬率 (%)", 0.0, 20.0, 7.0, 0.1) / 100
        inflation = st.slider("預估年通膨率 (%)", 0.0, 10.0, 2.0, 0.1) / 100

# ==========================================
# 3. 核心運算：財務穩健度指標
# ==========================================
total_assets = cash_assets + invest_assets + real_estate_value
monthly_expense_now = annual_expense / 12

# 1. 緊急預備金月數
emergency_months = cash_assets / monthly_expense_now if monthly_expense_now > 0 else 0
# 2. 儲蓄率
net_savings = annual_income - annual_expense - annual_debt_pay
savings_rate = (net_savings / annual_income) * 100 if annual_income > 0 else 0
# 3. 負債資產比
debt_ratio = (total_debt / total_assets) * 100 if total_assets > 0 else 0
# 4. 財務自由度
freedom_rate = (monthly_pension / post_retire_expense) * 100 if post_retire_expense > 0 else 0

# ==========================================
# 4. 主畫面：分頁架構
# ==========================================
st.title("🏦 通用版家庭財務戰情中心")
tab1, tab2 = st.tabs(["🏥 第一階段：家庭財務體質診斷", "🚀 第二階段：長期退休資產壓力測試"])

# ------------------------------------------
# Tab 1: 家庭財務體質診斷
# ------------------------------------------
with tab1:
    st.markdown("### 📊 核心穩健度指標評估")
    c1, c2, c3, c4 = st.columns(4)
    
    # 緊急預備金評估
    if emergency_months >= 6:
        em_status, em_color = "安全水位", "status-excellent"
    elif emergency_months >= 3:
        em_status, em_color = "勉強及格", "status-warning"
    else:
        em_status, em_color = "極度危險", "status-danger"
        
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">緊急預備金</div>
            <div class="metric-value">{emergency_months:.1f} <span style="font-size:1.1rem;">個月</span></div>
            <div class="metric-label {em_color}">{em_status}</div>
        </div>
        """, unsafe_allow_html=True)

    # 儲蓄率評估
    if savings_rate >= 30:
        sv_status, sv_color = "攻擊力極強", "status-excellent"
    elif savings_rate >= 15:
        sv_status, sv_color = "穩健累積", "status-warning"
    else:
        sv_status, sv_color = "入不敷出/漏財", "status-danger"
        
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">年度淨儲蓄率</div>
            <div class="metric-value">{savings_rate:.1f} <span style="font-size:1.1rem;">%</span></div>
            <div class="metric-label {sv_color}">{sv_status}</div>
        </div>
        """, unsafe_allow_html=True)

    # 負債比評估
    if debt_ratio <= 30:
        db_status, db_color = "槓桿健康", "status-excellent"
    elif debt_ratio <= 60:
        db_status, db_color = "需注意現金流", "status-warning"
    else:
        db_status, db_color = "過度擴張破產風險", "status-danger"
        
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">負債資產比</div>
            <div class="metric-value">{debt_ratio:.1f} <span style="font-size:1.1rem;">%</span></div>
            <div class="metric-label {db_color}">{db_status}</div>
        </div>
        """, unsafe_allow_html=True)

    # 財務自由度評估
    if freedom_rate >= 100:
        fr_status, fr_color = "完全財務自由", "status-excellent"
    elif freedom_rate >= 50:
        fr_status, fr_color = "具備半退休底氣", "status-warning"
    else:
        fr_status, fr_color = "需高度依賴主動收入", "status-danger"
        
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">預估財務自由度</div>
            <div class="metric-value">{freedom_rate:.1f} <span style="font-size:1.1rem;">%</span></div>
            <div class="metric-label {fr_color}">{fr_status}</div>
        </div>
        """, unsafe_allow_html=True)

    # 戰略總結
    st.markdown(f"""
    <div class="strategy-box">
        <div class="strategy-title">💡 演算法戰略診斷報告</div>
        <div class="strategy-text">
            <b>資金池擴張能力：</b>目前家庭每年可產生 <b>{net_savings:,} 元</b> 的淨現金流。建議將此資金分為兩筆：一筆投入全市場大盤 ETF (如 006208) 作為長線底倉，另一筆作為量化交易的狙擊資金。<br><br>
            <b>風險防禦力：</b>負債佔總資產比例僅 {debt_ratio:.1f}%，處於極度健康的狀態。預備金足以支撐 {emergency_months:.1f} 個月，抗暴震能力強。在這種財務體質下，可承受較高的市場波動，不需急於清償低利房貸，應讓資金在市場享受複利。
        </div>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------
# Tab 2: 長期退休資產壓力測試
# ------------------------------------------
with tab2:
    # 退休模擬運算邏輯
    sim_rows = []
    current_invest = invest_assets
    current_annual_post_expense = post_retire_expense * 12
    bankrupt_year = None
    
    # 累積期 (距離退休前)
    for y in range(years_to_retire):
        inv_income = int(current_invest * expected_return)
        current_invest = current_invest + inv_income + net_savings
        
    retire_starting_assets = current_invest
    
    # 提領期 (退休後 40 年)
    current_balance = retire_starting_assets
    for i in range(1, 41):
        inv_income = int(current_balance * expected_return) if current_balance > 0 else 0
        
        if i > 1:
            current_annual_post_expense = int(current_annual_post_expense * (1 + inflation))
            
        shortfall = max(0, current_annual_post_expense - (monthly_pension * 12))
        
        current_balance = current_balance + inv_income - shortfall
        if current_balance <= 0:
            current_balance = 0
            if bankrupt_year is None: bankrupt_year = i
            
        sim_rows.append({
            "退休後年度": i,
            "期初資產": current_balance + shortfall - inv_income,
            "投資收益": inv_income,
            "需提領金額 (補足缺口)": shortfall,
            "期末結餘": current_balance
        })

    df_sim = pd.DataFrame(sim_rows)
    
    st.markdown("### 📈 退休後 40 年流動資產消耗軌跡")
    
    fig = px.area(
        df_sim, 
        x="退休後年度", 
        y="期末結餘", 
        template="plotly_white",
        color_discrete_sequence=["#457b9d"]
    )
    fig.update_traces(line=dict(width=3))
    
    if bankrupt_year:
        fig.add_vline(x=bankrupt_year, line_dash="dot", line_color="#e63946", annotation_text=f"第{bankrupt_year}年資產歸零")
        
    fig.update_layout(yaxis_title="金融資產結餘 (TWD)", xaxis_title="退休後年度", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("查看完整退休提領流水帳", expanded=False):
        st.dataframe(df_sim, use_container_width=True)