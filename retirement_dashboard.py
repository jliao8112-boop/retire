import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go

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
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    .strategy-title { font-size: 1.25rem; font-weight: 700; margin-bottom: 12px; color: #1d3557;}
    .strategy-text { font-size: 1.05rem; line-height: 1.6; color: #495057; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 狀態管理 (Session State) 與資料匯入
# ==========================================
default_values = {
    "annual_income": 950000,
    "annual_expense": 800000,
    "annual_debt_pay": 120000,
    "cash_assets": 500000,
    "real_estate_value": 12000000,
    "total_debt": 2500000,
    "user_principal": 2000000,
    "user_annual_contribution": 120000,
    "user_years_to_retire": 9,
    "user_monthly_pension": 35000,
    "spouse_principal": 160000,
    "spouse_annual_contribution": 160000,
    "spouse_years_to_retire": 18,
    "spouse_monthly_pension": 35000,
    "expected_return_pct": 7.0,
    "post_retire_expense": 75000,
    "inflation_pct": 2.0
}

key_mapping = {
    "家庭年總收入": "annual_income", "家庭年總支出": "annual_expense", "年固定還款總額": "annual_debt_pay",
    "高流動性現金存款": "cash_assets", "不動產現值": "real_estate_value", "總負債餘額": "total_debt",
    "主力_初始本金": "user_principal", "主力_每年投入金額": "user_annual_contribution", 
    "主力_距離退休年數": "user_years_to_retire", "主力_預估月退俸": "user_monthly_pension",
    "配偶_初始本金": "spouse_principal", "配偶_每年投入金額": "spouse_annual_contribution", 
    "配偶_距離退休年數": "spouse_years_to_retire", "配偶_預估月退俸": "spouse_monthly_pension",
    "預期年化報酬率(%)": "expected_return_pct", "預估退休後每月支出": "post_retire_expense", "預估年通膨率(%)": "inflation_pct"
}

for key, val in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = val

with st.sidebar:
    st.header("📂 設定檔管理")
    uploaded_file = st.file_uploader("匯入個人設定檔 (CSV)", type="csv")
    if uploaded_file is not None:
        try:
            df_upload = pd.read_csv(uploaded_file)
            for index, row in df_upload.iterrows():
                if row['參數名稱'] in key_mapping:
                    state_key = key_mapping[row['參數名稱']]
                    st.session_state[state_key] = int(row['設定值']) if isinstance(st.session_state[state_key], int) else float(row['設定值'])
            st.success("設定檔匯入成功！參數已更新。")
        except:
            st.error("檔案格式錯誤或讀取失敗。")
            
    st.write("---")
    st.header("⚙️ 家庭財務參數輸入")
    
    with st.expander("💼 家庭收支與資產現況", expanded=False):
        annual_income = st.number_input("家庭年總收入 (元)", value=st.session_state["annual_income"], step=50000, key="annual_income")
        annual_expense = st.number_input("家庭年總支出 (元)", value=st.session_state["annual_expense"], step=50000, key="annual_expense")
        annual_debt_pay = st.number_input("年固定還款總額 (元)", value=st.session_state["annual_debt_pay"], step=10000, key="annual_debt_pay")
        cash_assets = st.number_input("高流動現金存款 (元)", value=st.session_state["cash_assets"], step=50000, key="cash_assets")
        real_estate_value = st.number_input("不動產現值 (元)", value=st.session_state["real_estate_value"], step=500000, key="real_estate_value")
        total_debt = st.number_input("總負債餘額 (元)", value=st.session_state["total_debt"], step=100000, key="total_debt")

    with st.expander("👨 主力：財務規劃與模擬", expanded=True):
        user_principal = st.number_input("主力_初始本金 (元)", value=st.session_state["user_principal"], step=50000, key="user_principal")
        user_annual_contribution = st.number_input("主力_每年投入金額 (元)", value=st.session_state["user_annual_contribution"], step=10000, key="user_annual_contribution")
        user_years_to_retire = st.slider("主力_距離退休尚有幾年？", 0, 40, st.session_state["user_years_to_retire"], key="user_years_to_retire")
        user_monthly_pension = st.number_input("主力_預估月退俸 (元)", value=st.session_state["user_monthly_pension"], step=5000, key="user_monthly_pension")

    with st.expander("👩 配偶：財務規劃與模擬", expanded=True):
        spouse_principal = st.number_input("配偶_初始本金 (元)", value=st.session_state["spouse_principal"], step=50000, key="spouse_principal")
        spouse_annual_contribution = st.number_input("配偶_每年投入金額 (元)", value=st.session_state["spouse_annual_contribution"], step=10000, key="spouse_annual_contribution")
        spouse_years_to_retire = st.slider("配偶_距離退休尚有幾年？", 0, 40, st.session_state["spouse_years_to_retire"], key="spouse_years_to_retire")
        spouse_monthly_pension = st.number_input("配偶_預估月退俸 (元)", value=st.session_state["spouse_monthly_pension"], step=5000, key="spouse_monthly_pension")
        
    with st.expander("📈 總體經濟與家庭共同參數", expanded=True):
        expected_return_pct = st.slider("預期年化報酬率 (%)", 0.0, 20.0, st.session_state["expected_return_pct"], 0.1, key="expected_return_pct")
        expected_return = expected_return_pct / 100
        post_retire_expense = st.number_input("預估退休後『每月』總支出 (元)", value=st.session_state["post_retire_expense"], step=5000, key="post_retire_expense")
        inflation_pct = st.slider("預估年通膨率 (%)", 0.0, 10.0, st.session_state["inflation_pct"], 0.1, key="inflation_pct")
        inflation = inflation_pct / 100

    st.write("---")
    st.download_button(
        label="📥 匯出個人設定檔 (CSV)",
        data=pd.DataFrame({"參數名稱": list(key_mapping.keys()), "設定值": [st.session_state[k] for k in key_mapping.values()]}).to_csv(index=False).encode('utf-8-sig'),
        file_name=f"家庭雙引擎財務設定檔_{datetime.date.today().strftime('%Y%m%d')}.csv", mime="text/csv"
    )

# ==========================================
# 3. 核心運算：基礎穩健度與未來資產推算
# ==========================================
total_financial_assets = user_principal + spouse_principal
monthly_expense_now = annual_expense / 12

emergency_months = cash_assets / monthly_expense_now if monthly_expense_now > 0 else 0
savings_rate = ((annual_income - annual_expense - annual_debt_pay) / annual_income) * 100 if annual_income > 0 else 0
debt_ratio = (total_debt / (cash_assets + total_financial_assets + real_estate_value)) * 100 if (cash_assets + total_financial_assets + real_estate_value) > 0 else 0

# 預估雙方抵達各自退休點時的資產水位
future_asset_u = user_principal
for _ in range(user_years_to_retire): future_asset_u = future_asset_u * (1 + expected_return) + user_annual_contribution

future_asset_s = spouse_principal
for _ in range(spouse_years_to_retire): future_asset_s = future_asset_s * (1 + expected_return) + spouse_annual_contribution

total_future_assets = future_asset_u + future_asset_s

# ==========================================
# 4. 雙階段財務自由度計算
# ==========================================
# [退休前] 財務自由度 = (當前金融資產的預期月收益) / 當前月支出
current_passive_income = (total_financial_assets * expected_return) / 12
pre_retire_fi_rate = (current_passive_income / monthly_expense_now) * 100 if monthly_expense_now > 0 else 0

# [退休後] 財務自由度 = (雙月退俸 + 未來累積資產的預期月收益) / 退休後月支出
future_passive_income = (total_future_assets * expected_return) / 12
total_future_pension = user_monthly_pension + spouse_monthly_pension
post_retire_fi_rate = ((total_future_pension + future_passive_income) / post_retire_expense) * 100 if post_retire_expense > 0 else 0

# ==========================================
# 5. 主畫面：分頁架構
# ==========================================
st.title("🏦 通用版家庭財務戰情中心")
tab1, tab2 = st.tabs(["🏥 第一階段：家庭財務體質與雙階段自由度", "🚀 第二階段：長期退休資產壓力測試"])

with tab1:
    st.markdown("### 🛡️ 基礎防禦指標")
    c1, c2, c3 = st.columns(3)
    
    em_color = "status-excellent" if emergency_months >= 6 else ("status-warning" if emergency_months >= 3 else "status-danger")
    c1.markdown(f'<div class="metric-card"><div class="metric-label">緊急預備金</div><div class="metric-value">{emergency_months:.1f} <span style="font-size:1.1rem;">個月</span></div></div>', unsafe_allow_html=True)

    sv_color = "status-excellent" if savings_rate >= 30 else ("status-warning" if savings_rate >= 15 else "status-danger")
    c2.markdown(f'<div class="metric-card"><div class="metric-label">年度淨儲蓄率</div><div class="metric-value">{savings_rate:.1f} <span style="font-size:1.1rem;">%</span></div></div>', unsafe_allow_html=True)

    db_color = "status-excellent" if debt_ratio <= 30 else ("status-warning" if debt_ratio <= 60 else "status-danger")
    c3.markdown(f'<div class="metric-card"><div class="metric-label">負債資產比</div><div class="metric-value">{debt_ratio:.1f} <span style="font-size:1.1rem;">%</span></div></div>', unsafe_allow_html=True)

    st.markdown("### 🎯 雙階段財務自由度評估")
    c4, c5, c6 = st.columns(3)
    
    pre_fi_color = "status-excellent" if pre_retire_fi_rate >= 100 else ("status-warning" if pre_retire_fi_rate >= 50 else "status-danger")
    c4.markdown(f'<div class="metric-card" style="border-top-color:#e9c46a;"><div class="metric-label">退休前財務自由度 (當下戰鬥力)</div><div class="metric-value" style="color:#e9c46a;">{pre_retire_fi_rate:.1f} <span style="font-size:1.1rem;">%</span></div><div style="font-size:0.9rem; color:#888;">僅靠現有資產孳息覆蓋當下生活</div></div>', unsafe_allow_html=True)

    post_fi_color = "status-excellent" if post_retire_fi_rate >= 100 else ("status-warning" if post_retire_fi_rate >= 50 else "status-danger")
    c5.markdown(f'<div class="metric-card" style="border-top-color:#2a9d8f;"><div class="metric-label">退休後財務自由度 (未來護城河)</div><div class="metric-value" style="color:#2a9d8f;">{post_retire_fi_rate:.1f} <span style="font-size:1.1rem;">%</span></div><div style="font-size:0.9rem; color:#888;">月退俸 + 未來滾存資產覆蓋退休生活</div></div>', unsafe_allow_html=True)

    c6.markdown(f'<div class="metric-card" style="border-top-color:#457b9d;"><div class="metric-label">預估退休時總流動資產</div><div class="metric-value">{int(total_future_assets):,} <span style="font-size:1.1rem;">元</span></div><div style="font-size:0.9rem; color:#888;">(雙方皆達退休年份時之預估值)</div></div>', unsafe_allow_html=True)

    # ------------------------------------------
    # 動態戰略建議生成
    # ------------------------------------------
    st.markdown("### 🧭 演算法戰略診斷報告")
    
    # 退休前策略
    if pre_retire_fi_rate >= 100:
        pre_strat = "<b>完全財務自由：</b>您當下的資產孳息已超越目前開銷。現階段的工作純屬個人選擇，可大膽嘗試高風險/高成就感的職涯轉換，或開始提高當下的生活品質。"
    elif pre_retire_fi_rate >= 50:
        pre_strat = "<b>具備半退休底氣 (Coast FIRE)：</b>資產已具備強大防禦力。現階段策略：保持目前的年度投入紀律，避免盲目擴張消費，耐心等待時間將資產推上複利陡坡。"
    else:
        pre_strat = "<b>高度依賴主動收入：</b>目前資產孳息尚不足以支撐現有生活。現階段策略：首要任務是保住本業收入，透過提高「年度淨儲蓄率」來加大資金池注入的力道。"

    # 退休後策略
    if post_retire_fi_rate >= 150:
        post_strat = "<b>資產跨世代溢出：</b>未來的被動現金流將遠超預估支出。策略建議：將多餘的提領額度用於規劃高階醫療保險、極致享樂體驗（如長途旅行），並可提前啟動子女的資產傳承規劃。"
    elif post_retire_fi_rate >= 100:
        post_strat = "<b>安全降落無虞：</b>未來的月退俸加上資產孳息能完美覆蓋退休生活。策略建議：退休後只需將部位維持在全市場大盤 ETF，按紀律提領，無需承擔選股風險。"
    else:
        post_strat = "<b>存在未來現金流缺口：</b>預估的被動收入不足以支撐退休生活。策略建議：您必須在退休前利用量化交易尋找高勝率的波段標的來拉高總資產，或計畫在退休後兼職以降低提領壓力。"

    st.markdown(f"""
    <div class="strategy-box" style="border-left-color: #e9c46a;">
        <div class="strategy-title">🏃‍♂️ 累積期 (退休前) 操作策略</div>
        <div class="strategy-text">{pre_strat}</div>
    </div>
    <div class="strategy-box" style="border-left-color: #2a9d8f;">
        <div class="strategy-title">🌴 提領期 (退休後) 操作策略</div>
        <div class="strategy-text">{post_strat}</div>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------
# Tab 2: 長期退休資產壓力測試 (保持不變)
# ------------------------------------------
with tab2:
    current_year = datetime.date.today().year
    asset_u, asset_s = user_principal, spouse_principal
    current_annual_expense = post_retire_expense * 12
    sim_rows = []
    bankrupt_year = None
    
    for i in range(1, 51):
        year_label = current_year + i
        user_retired = i > user_years_to_retire
        spouse_retired = i > spouse_years_to_retire
        
        inv_income_u = int(asset_u * expected_return) if asset_u > 0 else 0
        inv_income_s = int(asset_s * expected_return) if asset_s > 0 else 0
        
        cont_u = user_annual_contribution if not user_retired else 0
        cont_s = spouse_annual_contribution if not spouse_retired else 0
        
        pension_u = user_monthly_pension * 12 if user_retired else 0
        pension_s = spouse_monthly_pension * 12 if spouse_retired else 0
        total_pension_received = pension_u + pension_s
        
        if i > 1: current_annual_expense = int(current_annual_expense * (1 + inflation))
            
        shortfall = max(0, current_annual_expense - total_pension_received) if (user_retired or spouse_retired) else 0
            
        asset_u = asset_u + inv_income_u + cont_u
        asset_s = asset_s + inv_income_s + cont_s
        
        actual_withdrawal = shortfall
        if shortfall > 0:
            if asset_u >= shortfall: asset_u -= shortfall
            else:
                shortfall -= asset_u; asset_u = 0; asset_s -= shortfall
                if asset_s < 0: asset_s = 0
                    
        total_family_asset = asset_u + asset_s
        if total_family_asset <= 0 and bankrupt_year is None and (user_retired or spouse_retired):
            bankrupt_year = year_label
            
        sim_rows.append({"觀測年度": year_label, "主力資金結餘": int(asset_u), "配偶資金結餘": int(asset_s), "家庭總流動資產": int(total_family_asset), "年度總月退俸": int(total_pension_received), "通膨後年度預估支出": int(current_annual_expense) if (user_retired or spouse_retired) else 0, "需從資產提領金額": int(actual_withdrawal)})

    df_sim = pd.DataFrame(sim_rows)
    st.markdown("### 📈 家庭雙引擎資產長期軌跡")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_sim['觀測年度'], y=df_sim['配偶資金結餘'], mode='lines', line=dict(width=0.5, color='#457b9d'), stackgroup='one', name='配偶資金池'))
    fig.add_trace(go.Scatter(x=df_sim['觀測年度'], y=df_sim['主力資金結餘'], mode='lines', line=dict(width=0.5, color='#8CB35A'), stackgroup='one', name='主力資金池'))
    
    if bankrupt_year: fig.add_vline(x=bankrupt_year, line_dash="dot", line_color="#e63946", annotation_text=f"{bankrupt_year}年資產歸零")
        
    if user_years_to_retire > 0: fig.add_vline(x=current_year + user_years_to_retire, line_dash="dash", line_color="#e9c46a", annotation_text="主力退休", annotation_position="top left")
    if spouse_years_to_retire > 0: fig.add_vline(x=current_year + spouse_years_to_retire, line_dash="dash", line_color="#e9c46a", annotation_text="配偶退休", annotation_position="top left")

    fig.update_layout(yaxis_title="金融資產結餘 (TWD)", xaxis_title="觀測年度", hovermode="x unified", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)