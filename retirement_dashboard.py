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
        margin-bottom: 25px;
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
    "user_principal": 10000000,
    "user_annual_contribution": 120000,
    "user_years_to_retire": 9,
    "user_monthly_pension": 35000,
    "spouse_principal": 360000,
    "spouse_annual_contribution": 360000,
    "spouse_years_to_retire": 18,
    "spouse_monthly_pension": 35000,
    "expected_return_pct": 7.0,
    "post_retire_expense": 75000,
    "inflation_pct": 2.0
}

key_mapping = {
    "家庭年總收入": "annual_income",
    "家庭年總支出": "annual_expense",
    "年固定還款總額": "annual_debt_pay",
    "高流動性現金存款": "cash_assets",
    "不動產現值": "real_estate_value",
    "總負債餘額": "total_debt",
    "主力_初始本金": "user_principal",
    "主力_每年投入金額": "user_annual_contribution",
    "主力_距離退休年數": "user_years_to_retire",
    "主力_預估月退俸": "user_monthly_pension",
    "配偶_初始本金": "spouse_principal",
    "配偶_每年投入金額": "spouse_annual_contribution",
    "配偶_距離退休年數": "spouse_years_to_retire",
    "配偶_預估月退俸": "spouse_monthly_pension",
    "預期年化報酬率(%)": "expected_return_pct",
    "預估退休後每月支出": "post_retire_expense",
    "預估年通膨率(%)": "inflation_pct"
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
                param_name = row['參數名稱']
                param_value = row['設定值']
                if param_name in key_mapping:
                    state_key = key_mapping[param_name]
                    if isinstance(st.session_state[state_key], int):
                        st.session_state[state_key] = int(param_value)
                    else:
                        st.session_state[state_key] = float(param_value)
            st.success("設定檔匯入成功！參數已更新。")
        except Exception as e:
            st.error("檔案格式錯誤或讀取失敗，請確認檔案來源。")
            
    st.write("---")
    st.header("⚙️ 家庭財務參數輸入")
    
    with st.expander("💼 家庭收支與資產現況", expanded=False):
        annual_income = st.number_input("家庭年總收入 (元)", value=st.session_state["annual_income"], step=50000, key="annual_income")
        annual_expense = st.number_input("家庭年總支出 (含食衣住行育樂) (元)", value=st.session_state["annual_expense"], step=50000, key="annual_expense")
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
        expected_return_pct = st.slider("投資組合預期年化報酬率 (%)", 0.0, 20.0, st.session_state["expected_return_pct"], 0.1, key="expected_return_pct")
        expected_return = expected_return_pct / 100
        post_retire_expense = st.number_input("預估退休後『每月』總支出 (元)", value=st.session_state["post_retire_expense"], step=5000, key="post_retire_expense")
        inflation_pct = st.slider("預估年通膨率 (%)", 0.0, 10.0, st.session_state["inflation_pct"], 0.1, key="inflation_pct")
        inflation = inflation_pct / 100

    # ------------------------------------------
    # 匯出個人設定檔功能
    # ------------------------------------------
    st.write("---")
    st.subheader("💾 匯出設定")
    user_settings = {
        "參數名稱": list(key_mapping.keys()),
        "設定值": [st.session_state[k] for k in key_mapping.values()]
    }
    df_settings = pd.DataFrame(user_settings)
    csv_data = df_settings.to_csv(index=False).encode('utf-8-sig')
    
    st.download_button(
        label="📥 匯出個人設定檔 (CSV)",
        data=csv_data,
        file_name=f"家庭雙引擎財務設定檔_{datetime.date.today().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# ==========================================
# 3. 核心運算：財務穩健度指標
# ==========================================
total_financial_assets = user_principal + spouse_principal
total_assets = cash_assets + total_financial_assets + real_estate_value
monthly_expense_now = annual_expense / 12

# 1. 緊急預備金月數
emergency_months = cash_assets / monthly_expense_now if monthly_expense_now > 0 else 0
# 2. 儲蓄率
net_savings = annual_income - annual_expense - annual_debt_pay
savings_rate = (net_savings / annual_income) * 100 if annual_income > 0 else 0
# 3. 負債資產比
debt_ratio = (total_debt / total_assets) * 100 if total_assets > 0 else 0
# 4. 財務自由度 (以雙方未來月退俸總和評估)
total_future_pension = user_monthly_pension + spouse_monthly_pension
freedom_rate = (total_future_pension / post_retire_expense) * 100 if post_retire_expense > 0 else 0

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
    
    if emergency_months >= 6:
        em_status, em_color = "安全水位", "status-excellent"
    elif emergency_months >= 3:
        em_status, em_color = "勉強及格", "status-warning"
    else:
        em_status, em_color = "極度危險", "status-danger"
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">緊急預備金</div><div class="metric-value">{emergency_months:.1f} <span style="font-size:1.1rem;">個月</span></div><div class="metric-label {em_color}">{em_status}</div></div>', unsafe_allow_html=True)

    if savings_rate >= 30:
        sv_status, sv_color = "攻擊力極強", "status-excellent"
    elif savings_rate >= 15:
        sv_status, sv_color = "穩健累積", "status-warning"
    else:
        sv_status, sv_color = "入不敷出/漏財", "status-danger"
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">年度淨儲蓄率</div><div class="metric-value">{savings_rate:.1f} <span style="font-size:1.1rem;">%</span></div><div class="metric-label {sv_color}">{sv_status}</div></div>', unsafe_allow_html=True)

    if debt_ratio <= 30:
        db_status, db_color = "槓桿健康", "status-excellent"
    elif debt_ratio <= 60:
        db_status, db_color = "需注意現金流", "status-warning"
    else:
        db_status, db_color = "擴張破產風險", "status-danger"
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">負債資產比</div><div class="metric-value">{debt_ratio:.1f} <span style="font-size:1.1rem;">%</span></div><div class="metric-label {db_color}">{db_status}</div></div>', unsafe_allow_html=True)

    if freedom_rate >= 100:
        fr_status, fr_color = "完全財務自由", "status-excellent"
    elif freedom_rate >= 50:
        fr_status, fr_color = "具備半退休底氣", "status-warning"
    else:
        fr_status, fr_color = "需高度依賴主動收入", "status-danger"
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">預估財務自由度</div><div class="metric-value">{freedom_rate:.1f} <span style="font-size:1.1rem;">%</span></div><div class="metric-label {fr_color}">{fr_status}</div></div>', unsafe_allow_html=True)

    # 戰略總結 (依據財務自由度動態生成，去除數字標籤)
    if freedom_rate >= 100:
        strategy_text = f"<b>當前狀態：完全財務自由。</b><br>未來的被動收入已完全涵蓋退休基本開銷。建議將未來重心轉往資產傳承與高品質生活體驗。投資策略上，只需維持全市場大盤指數股票型基金（如 006208）作為底倉，並可搭配您的量化系統捕捉市場甜甜價作為輔助，無需承擔過多風險，資產便能生生不息。"
        border_color = "#2a9d8f"
    elif freedom_rate >= 50:
        strategy_text = f"<b>當前狀態：具備半退休底氣。</b><br>基礎生活已有一定保障，但仍需提領部分投資資產填補缺口。請嚴格執行每年的投入計畫，持續擴大資金池，配合技術指標在量縮打底時精準佈局，加速將財務自由度推向 100%。"
        border_color = "#e9c46a"
    else:
        strategy_text = f"<b>當前狀態：需高度依賴主動收入。</b><br>退休後現金流缺口顯著，面臨較大資產枯竭風險。首要任務是檢視日常開銷、提升年度淨儲蓄率，並盡可能提高每年的投入金額。建議尋求穩健增長的市值型標的，避免投機短線，耐心利用時間建立防禦護城河。"
        border_color = "#e63946"

    st.markdown(f"""
    <div class="strategy-box" style="border-left-color: {border_color};">
        <div class="strategy-title">💡 演算法戰略診斷報告</div>
        <div class="strategy-text">
            {strategy_text}<br><br>
            <b>資產防禦力備註：</b>目前緊急預備金可支撐 {emergency_months:.1f} 個月，負債佔總資產比例為 {debt_ratio:.1f}%。
        </div>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------
# Tab 2: 長期退休資產壓力測試 (雙引擎模擬)
# ------------------------------------------
with tab2:
    current_year = datetime.date.today().year
    simulation_years = 50
    
    asset_u = user_principal
    asset_s = spouse_principal
    current_annual_expense = post_retire_expense * 12
    
    sim_rows = []
    bankrupt_year = None
    
    for i in range(1, simulation_years + 1):
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
        
        if i > 1:
            current_annual_expense = int(current_annual_expense * (1 + inflation))
            
        # 若家庭中至少有一人退休，便開始評估資金缺口
        if user_retired or spouse_retired:
            shortfall = max(0, current_annual_expense - total_pension_received)
        else:
            shortfall = 0
            
        asset_u = asset_u + inv_income_u + cont_u
        asset_s = asset_s + inv_income_s + cont_s
        
        actual_withdrawal = shortfall
        if shortfall > 0:
            if asset_u >= shortfall:
                asset_u -= shortfall
            else:
                shortfall -= asset_u
                asset_u = 0
                asset_s -= shortfall
                if asset_s < 0:
                    asset_s = 0
                    
        total_family_asset = asset_u + asset_s
        if total_family_asset <= 0 and bankrupt_year is None and (user_retired or spouse_retired):
            bankrupt_year = year_label
            
        sim_rows.append({
            "觀測年度": year_label,
            "主力資金結餘": int(asset_u),
            "配偶資金結餘": int(asset_s),
            "家庭總流動資產": int(total_family_asset),
            "年度總月退俸": int(total_pension_received),
            "通膨後年度預估支出": int(current_annual_expense) if (user_retired or spouse_retired) else 0,
            "需從資產提領金額": int(actual_withdrawal)
        })

    df_sim = pd.DataFrame(sim_rows)
    
    st.markdown("### 📈 家庭雙引擎資產長期軌跡")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_sim['觀測年度'], y=df_sim['配偶資金結餘'],
        mode='lines', line=dict(width=0.5, color='#457b9d'), stackgroup='one', name='配偶資金池'
    ))
    fig.add_trace(go.Scatter(
        x=df_sim['觀測年度'], y=df_sim['主力資金結餘'],
        mode='lines', line=dict(width=0.5, color='#8CB35A'), stackgroup='one', name='主力資金池'
    ))
    
    if bankrupt_year:
        fig.add_vline(x=bankrupt_year, line_dash="dot", line_color="#e63946", annotation_text=f"{bankrupt_year}年資產歸零")
        
    user_retire_year_label = current_year + user_years_to_retire
    spouse_retire_year_label = current_year + spouse_years_to_retire
    
    if user_years_to_retire > 0:
        fig.add_vline(x=user_retire_year_label, line_dash="dash", line_color="#e9c46a", annotation_text="主力退休", annotation_position="top left")
    if spouse_years_to_retire > 0:
        fig.add_vline(x=spouse_retire_year_label, line_dash="dash", line_color="#e9c46a", annotation_text="配偶退休", annotation_position="top left")

    fig.update_layout(yaxis_title="金融資產結餘 (TWD)", xaxis_title="觀測年度", hovermode="x unified", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("查看完整雙引擎退休流水帳", expanded=False):
        df_formatted = df_sim.copy()
        for col in df_formatted.columns:
            if col != '觀測年度':
                df_formatted[col] = df_formatted[col].map(lambda x: f"{x:,}")
        st.dataframe(df_formatted, use_container_width=True, hide_index=True)