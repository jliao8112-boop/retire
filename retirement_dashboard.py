import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ==========================================
# 1. 網頁全域設定與自訂 CSS
# ==========================================
st.set_page_config(page_title="通用版個人/家庭財務戰情中心", layout="wide", page_icon="🏦")

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 12px;
        padding: 25px 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        text-align: center;
        border-top: 4px solid #457b9d;
        margin-bottom: 25px;
    }
    .metric-label { font-size: 1.1rem; color: #6c757d; font-weight: 600; margin-bottom: 12px; }
    .metric-value { font-size: clamp(1.5rem, 2.5vw, 2rem); font-weight: 700; color: #1d3557; }
    .status-excellent { color: #2a9d8f !important; font-weight: bold; }
    .status-warning { color: #e9c46a !important; font-weight: bold; }
    .status-danger { color: #e63946 !important; font-weight: bold; }
    
    .strategy-box {
        padding: 25px 30px;
        border-radius: 12px;
        background-color: #f8f9fa;
        border-left: 6px solid #457b9d;
        margin-top: 15px;
        margin-bottom: 25px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    .strategy-title { font-size: 1.35rem; font-weight: 700; margin-bottom: 15px; color: #1d3557;}
    .strategy-text { font-size: 1.1rem; line-height: 1.8; color: #495057; }
    
    .alert-box { background-color: #fff3f3; border-left: 6px solid #e63946; }
    .alert-title { color: #e63946; font-weight: bold; font-size: 1.25rem; margin-bottom: 12px; }
    
    .streamlit-expanderHeader { font-size: 1.1rem !important; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 狀態管理 (Session State) 與資料匯入/匯出設定
# ==========================================
default_values = {
    "planning_mode": "雙人/家庭",
    "dependent_children": 1,
    "dependent_elders": 1,
    "annual_income": 1100000, 
    "annual_expense": 850000,
    "cash_assets": 500000,
    "real_estate_value": 10000000,
    "loan_principal": 5000000,
    "loan_interest_rate": 2.1,
    "loan_years_remaining": 20,
    "child_age": 10,
    "college_start_age": 18,
    "college_years": 4,
    "annual_college_cost": 250000,
    "user_principal": 1500000,
    "user_annual_contribution": 150000,
    "user_years_to_retire": 15,
    "user_monthly_pension": 25000,
    "spouse_principal": 1000000,
    "spouse_annual_contribution": 100000,
    "spouse_years_to_retire": 15,
    "spouse_monthly_pension": 25000,
    "expected_return_pct": 6.0,
    "post_retire_expense": 60000,
    "basic_inflation_pct": 2.0,
    "special_inflation_pct": 3.5,
    "exp1_name": "", "exp1_year": 0, "exp1_amount": 0,
    "exp2_name": "", "exp2_year": 0, "exp2_amount": 0,
    "exp3_name": "", "exp3_year": 0, "exp3_amount": 0,
}

key_mapping = {
    "規劃模式": "planning_mode", "扶養子女數": "dependent_children", "扶養長輩數": "dependent_elders",
    "年總收入": "annual_income", "年總基礎支出": "annual_expense", "高流動現金存款": "cash_assets",
    "不動產現值": "real_estate_value", "剩餘貸款本金": "loan_principal", "貸款年利率": "loan_interest_rate",
    "剩餘攤還年限": "loan_years_remaining", "子女目前年齡": "child_age", "預計就讀大學年齡": "college_start_age",
    "預計就讀年數": "college_years", "大學每年總花費": "annual_college_cost",
    "參與者A_初始本金": "user_principal", "參與者A_每年投入金額": "user_annual_contribution",
    "參與者A_距離退休年數": "user_years_to_retire", "參與者A_預估月退俸": "user_monthly_pension",
    "參與者B_初始本金": "spouse_principal", "參與者B_每年投入金額": "spouse_annual_contribution",
    "參與者B_距離退休年數": "spouse_years_to_retire", "參與者B_預估月退俸": "spouse_monthly_pension",
    "預期年化報酬率": "expected_return_pct", "退休後每月總支出": "post_retire_expense",
    "基本生活通膨率": "basic_inflation_pct", "特殊專案通膨率": "special_inflation_pct",
    "支出1名稱": "exp1_name", "支出1幾年後": "exp1_year", "支出1總額": "exp1_amount",
    "支出2名稱": "exp2_name", "支出2幾年後": "exp2_year", "支出2總額": "exp2_amount",
    "支出3名稱": "exp3_name", "支出3幾年後": "exp3_year", "支出3總額": "exp3_amount"
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
                    val = row['設定值']
                    if state_key == "planning_mode": 
                        st.session_state[state_key] = str(val)
                    elif isinstance(st.session_state[state_key], int): 
                        st.session_state[state_key] = int(val) if pd.notna(val) else 0
                    elif isinstance(st.session_state[state_key], float): 
                        st.session_state[state_key] = float(val) if pd.notna(val) else 0.0
                    else: 
                        st.session_state[state_key] = str(val) if pd.notna(val) else ""
            st.success("設定檔匯入成功！")
        except Exception as e:
            st.error("檔案格式錯誤或讀取失敗。")
            
    st.divider()
    st.header("⚙️ 財務參數輸入")
    
    planning_mode = st.radio("選擇財務規劃模式", ["雙人/家庭", "單人"], index=0 if st.session_state["planning_mode"] == "雙人/家庭" else 1, horizontal=True)
    st.session_state["planning_mode"] = planning_mode
    prefix = "家庭" if planning_mode == "雙人/家庭" else "個人"
    st.write("")

    with st.expander(f"👥 扶養與收支現況 (主計處中位數參考)", expanded=False):
        dependent_children = st.number_input("扶養子女數 (人)", value=st.session_state["dependent_children"], step=1)
        dependent_elders = st.number_input("扶養長輩數 (人)", value=st.session_state["dependent_elders"], step=1)
        st.divider()
        annual_income = st.number_input(f"{prefix}年總收入 (元)", value=st.session_state["annual_income"], step=50000)
        annual_expense = st.number_input(f"{prefix}年總基礎支出 (元)", value=st.session_state["annual_expense"], step=50000, help="不含貸款還款之基本生活開銷")
        st.divider()
        cash_assets = st.number_input("高流動現金存款 (元)", value=st.session_state["cash_assets"], step=50000)
        real_estate_value = st.number_input("不動產現值 (元)", value=st.session_state["real_estate_value"], step=500000)

    with st.expander("🏦 負債與攤還設定 (本金平均攤還)", expanded=True):
        loan_principal = st.number_input("剩餘貸款本金 (元)", value=st.session_state["loan_principal"], step=100000)
        loan_interest_rate = st.number_input("貸款年利率 (%)", value=st.session_state["loan_interest_rate"], step=0.1)
        loan_years_remaining = st.number_input("剩餘攤還年限 (年)", value=st.session_state["loan_years_remaining"], step=1)

    with st.expander("🎓 子女高等教育經費 (套用特殊通膨)", expanded=True):
        child_age = st.number_input("子女目前年齡 (歲)", value=st.session_state["child_age"], step=1)
        college_start_age = st.number_input("預計就讀大學年齡 (歲)", value=st.session_state["college_start_age"], step=1)
        college_years = st.number_input("預計就讀年數 (年)", value=st.session_state["college_years"], step=1)
        annual_college_cost = st.number_input("大學每年總花費 (元/年)", value=st.session_state["annual_college_cost"], step=10000, help="全台公私立大學生年開銷中位數約落在 25 萬上下。")

    with st.expander("📌 自訂階段性重大支出 (選填)", expanded=True):
        st.caption("支援 3 筆重大支出 (如：購屋頭期款、長輩照護基金)，將套用特殊專案通膨率計算。")
        for i in range(1, 4):
            c1, c2, c3 = st.columns([2, 1, 1.5], gap="small")
            st.session_state[f"exp{i}_name"] = c1.text_input(f"支出 {i} 名稱", value=st.session_state[f"exp{i}_name"], key=f"name_{i}")
            st.session_state[f"exp{i}_year"] = c2.number_input("幾年後", value=st.session_state[f"exp{i}_year"], step=1, key=f"year_{i}")
            st.session_state[f"exp{i}_amount"] = c3.number_input("現值總額", value=st.session_state[f"exp{i}_amount"], step=50000, key=f"amt_{i}")
            if i < 3: st.write("")

    with st.expander("👨 參與者 A：財務規劃與模擬", expanded=True):
        user_principal = st.number_input("初始本金 (元)", value=st.session_state["user_principal"], step=50000)
        user_annual_contribution = st.number_input("每年投入金額 (元)", value=st.session_state["user_annual_contribution"], step=10000)
        user_years_to_retire = st.slider("距離退休尚有幾年？", 0, 40, st.session_state["user_years_to_retire"])
        user_monthly_pension = st.number_input("預估月退俸 (元)", value=st.session_state["user_monthly_pension"], step=5000)

    if planning_mode == "雙人/家庭":
        with st.expander("👩 參與者 B：財務規劃與模擬", expanded=True):
            spouse_principal = st.number_input("參與者B_初始本金 (元)", value=st.session_state["spouse_principal"], step=50000)
            spouse_annual_contribution = st.number_input("參與者B_每年投入金額 (元)", value=st.session_state["spouse_annual_contribution"], step=10000)
            spouse_years_to_retire = st.slider("參與者B_距離退休尚有幾年？", 0, 40, st.session_state["spouse_years_to_retire"])
            spouse_monthly_pension = st.number_input("參與者B_預估月退俸 (元)", value=st.session_state["spouse_monthly_pension"], step=5000)
    else:
        spouse_principal = 0; spouse_annual_contribution = 0; spouse_years_to_retire = 0; spouse_monthly_pension = 0
        
    with st.expander("📈 總體經濟參數 (雙軌通膨)", expanded=True):
        expected_return_pct = st.slider("預期年化報酬率 (%)", 0.0, 20.0, st.session_state["expected_return_pct"], 0.1)
        expected_return = expected_return_pct / 100
        post_retire_expense = st.number_input("預估退休後『每月』總支出 (元)", value=st.session_state["post_retire_expense"], step=5000)
        st.divider()
        basic_inflation_pct = st.slider("基本生活通膨率 (%)", 0.0, 10.0, st.session_state["basic_inflation_pct"], 0.1)
        basic_inflation = basic_inflation_pct / 100
        special_inflation_pct = st.slider("特殊專案通膨率 (%)", 0.0, 15.0, st.session_state["special_inflation_pct"], 0.1, help="套用於自訂階段性重大支出與大學教育經費")
        special_inflation = special_inflation_pct / 100

    st.divider()
    st.download_button(
        label="📥 匯出個人設定檔 (CSV)",
        data=pd.DataFrame({"參數名稱": list(key_mapping.keys()), "設定值": [st.session_state[k] for k in key_mapping.values()]}).to_csv(index=False).encode('utf-8-sig'),
        file_name=f"{prefix}財務設定檔_{datetime.date.today().strftime('%Y%m%d')}.csv", mime="text/csv"
    )

# ==========================================
# 3. 核心運算：本金平均攤還演算法與資產推算
# ==========================================
def calculate_annual_debt_payment(principal, annual_rate, years, current_year_index):
    """計算本金平均攤還（本金利息一起還）特定年度的總現金流流出"""
    if years <= 0 or principal <= 0 or current_year_index >= years:
        return 0
        
    monthly_rate = annual_rate / 100 / 12
    total_months = years * 12
    monthly_principal = principal / total_months
    start_month = current_year_index * 12
    annual_interest = 0
    
    for m in range(start_month, start_month + 12):
        if m < total_months:
            remaining_principal = principal - (monthly_principal * m)
            annual_interest += remaining_principal * monthly_rate
            
    annual_principal = monthly_principal * 12 if current_year_index < years else 0
    return annual_principal + annual_interest

first_year_debt_pay = calculate_annual_debt_payment(loan_principal, loan_interest_rate, loan_years_remaining, 0)

total_financial_assets = user_principal + spouse_principal
monthly_expense_now = (annual_expense + first_year_debt_pay) / 12 if (annual_expense + first_year_debt_pay) > 0 else 1

emergency_months = cash_assets / monthly_expense_now if monthly_expense_now > 0 else 0
savings_rate = ((annual_income - annual_expense - first_year_debt_pay) / annual_income) * 100 if annual_income > 0 else 0
total_assets_value = cash_assets + total_financial_assets + real_estate_value
debt_ratio = (loan_principal / total_assets_value) * 100 if total_assets_value > 0 else 0

current_passive_income = (total_financial_assets * expected_return) / 12
pre_retire_fi_rate = (current_passive_income / monthly_expense_now) * 100 if monthly_expense_now > 0 else 0

future_asset_u = user_principal
for _ in range(user_years_to_retire): future_asset_u = future_asset_u * (1 + expected_return) + user_annual_contribution

future_asset_s = spouse_principal if planning_mode == "雙人/家庭" else 0
if planning_mode == "雙人/家庭":
    for _ in range(spouse_years_to_retire): future_asset_s = future_asset_s * (1 + expected_return) + spouse_annual_contribution

total_future_assets = future_asset_u + future_asset_s
total_future_pension = user_monthly_pension + spouse_monthly_pension
future_passive_income = (total_future_assets * expected_return) / 12
post_retire_fi_rate = ((total_future_pension + future_passive_income) / post_retire_expense) * 100 if post_retire_expense > 0 else 0

safe_em_months = 6 if planning_mode == "雙人/家庭" else 9
warn_em_months = 3 if planning_mode == "雙人/家庭" else 6

# ==========================================
# 4. 主畫面：分頁架構
# ==========================================
st.title(f"🏦 通用版{prefix}財務戰情中心")
st.write("")

tab1, tab2 = st.tabs(["🏥 第一階段：財務體質與雙階段自由度", "🚀 第二階段：長期退休資產壓力測試"])

with tab1:
    st.write("")
    st.markdown("### 🛡️ 基礎防禦指標")
    c1, c2, c3 = st.columns(3, gap="large") 
    
    em_color = "status-excellent" if emergency_months >= safe_em_months else ("status-warning" if emergency_months >= warn_em_months else "status-danger")
    c1.markdown(f'<div class="metric-card"><div class="metric-label">緊急預備金</div><div class="metric-value {em_color}">{emergency_months:.1f} <span style="font-size:1.1rem;">個月</span></div><div style="font-size:0.9rem; color:#888; margin-top:8px;">{prefix}安全基準: {safe_em_months}個月</div></div>', unsafe_allow_html=True)

    sv_color = "status-excellent" if savings_rate >= 30 else ("status-warning" if savings_rate >= 15 else "status-danger")
    c2.markdown(f'<div class="metric-card"><div class="metric-label">首年年度淨儲蓄率</div><div class="metric-value {sv_color}">{savings_rate:.1f} <span style="font-size:1.1rem;">%</span></div></div>', unsafe_allow_html=True)

    db_color = "status-excellent" if debt_ratio <= 30 else ("status-warning" if debt_ratio <= 60 else "status-danger")
    c3.markdown(f'<div class="metric-card"><div class="metric-label">負債資產比</div><div class="metric-value {db_color}">{debt_ratio:.1f} <span style="font-size:1.1rem;">%</span></div></div>', unsafe_allow_html=True)

    st.divider()
    
    st.markdown("### 🎯 雙階段財務獨立度評估")
    c4, c5, c6 = st.columns(3, gap="large")
    
    c4.markdown(f'<div class="metric-card" style="border-top-color:#e9c46a;"><div class="metric-label">退休前財務獨立度</div><div class="metric-value" style="color:#e9c46a;">{pre_retire_fi_rate:.1f} <span style="font-size:1.1rem;">%</span></div><div style="font-size:0.9rem; color:#888; margin-top:8px;">現有資產孳息覆蓋當下生活</div></div>', unsafe_allow_html=True)
    c5.markdown(f'<div class="metric-card" style="border-top-color:#2a9d8f;"><div class="metric-label">退休後財務獨立度</div><div class="metric-value" style="color:#2a9d8f;">{post_retire_fi_rate:.1f} <span style="font-size:1.1rem;">%</span></div><div style="font-size:0.9rem; color:#888; margin-top:8px;">被動總收入覆蓋退休生活</div></div>', unsafe_allow_html=True)
    c6.markdown(f'<div class="metric-card" style="border-top-color:#457b9d;"><div class="metric-label">預估退休時總流動資產</div><div class="metric-value">{int(total_future_assets):,} <span style="font-size:1.1rem;">元</span></div><div style="font-size:0.9rem; color:#888; margin-top:8px;">(邁入退休年份時之預估值)</div></div>', unsafe_allow_html=True)

    st.divider()

    st.markdown("### 🧭 演算法戰略診斷報告")
    
    if pre_retire_fi_rate >= 100: pre_strat = "<b>完全財務自由：</b>當下的資產孳息已超越目前開銷。現階段的工作純屬個人選擇，無需急於將閒置資金全部投入，可將目標設定為觀察名單，耐心等待優質資產來到<b>甜甜價</b>時再進行長線佈局，同時開始提高生活品質。"
    elif pre_retire_fi_rate >= 50: pre_strat = "<b>具備半退休底氣：</b>資產已具備強大防禦力。請保持年度投入紀律，避免盲目擴張消費，耐心等待資產複利增長。"
    else: pre_strat = "<b>高度依賴主動收入：</b>目前資產孳息不足以支撐現有生活。首要任務是保住本業收入，透過提高「淨儲蓄率」加大投入力道。"

    if post_retire_fi_rate >= 150: post_strat = "<b>資產跨世代溢出：</b>未來的被動現金流將遠超預估支出。建議將多餘額度用於高階醫療保險、極致旅遊體驗，或啟動資產傳承規劃。"
    elif post_retire_fi_rate >= 100: post_strat = "<b>安全降落無虞：</b>被動收入能完美覆蓋退休生活。退休後只需將部位維持在全市場大盤指數股票型基金，遵循安全提領率紀律提領，無需承擔過多選股風險。"
    else: post_strat = "<b>存在未來現金流缺口：</b>預估的被動收入不足以支撐退休生活。請務必拉長累積期，或在下方壓力測試區塊參考「危機應急指南」。"

    st.markdown(f"""
    <div class="strategy-box" style="border-left-color: #e9c46a;">
        <div class="strategy-title">🏃‍♂️ 累積期 (現在) 操作策略</div>
        <div class="strategy-text">{pre_strat}</div>
    </div>
    <div class="strategy-box" style="border-left-color: #2a9d8f;">
        <div class="strategy-title">🌴 提領期 (未來) 操作策略</div>
        <div class="strategy-text">{post_strat}</div>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------
# Tab 2: 長期退休資產壓力測試
# ------------------------------------------
with tab2:
    st.write("")
    current_year = datetime.date.today().year
    asset_u, asset_s = user_principal, spouse_principal
    current_annual_expense = post_retire_expense * 12
    sim_rows = []
    bankrupt_year = None
    
    for i in range(1, 51):
        year_label = current_year + i
        user_retired = i > user_years_to_retire
        spouse_retired = (i > spouse_years_to_retire) if planning_mode == "雙人/家庭" else False
        
        inv_income_u = int(asset_u * expected_return) if asset_u > 0 else 0
        inv_income_s = int(asset_s * expected_return) if asset_s > 0 else 0
        
        cont_u = user_annual_contribution if not user_retired else 0
        cont_s = spouse_annual_contribution if not spouse_retired else 0
        
        pension_u = user_monthly_pension * 12 if user_retired else 0
        pension_s = spouse_monthly_pension * 12 if (spouse_retired and planning_mode == "雙人/家庭") else 0
        total_pension_received = pension_u + pension_s
        
        # 貸款支出 (本金平均攤還)
        debt_expense_this_year = calculate_annual_debt_payment(loan_principal, loan_interest_rate, loan_years_remaining, i-1)

        if i > 1: current_annual_expense = int(current_annual_expense * (1 + basic_inflation))
            
        # 計算當年度教育經費 (套用特殊專案通膨)
        child_age_this_year = child_age + i
        if college_start_age <= child_age_this_year < college_start_age + college_years:
            edu_expense_this_year = int(annual_college_cost * ((1 + special_inflation) ** i))
        else:
            edu_expense_this_year = 0

        # 檢測自訂階段性重大支出 (套用特殊專案通膨率)
        special_expense_this_year = 0
        for j in range(1, 4):
            if st.session_state[f"exp{j}_name"] != "" and st.session_state[f"exp{j}_year"] == i:
                special_expense_this_year += int(st.session_state[f"exp{j}_amount"] * ((1 + special_inflation) ** i))
            
        base_shortfall = max(0, current_annual_expense - total_pension_received) if (user_retired or spouse_retired) else 0
        total_shortfall_needed = base_shortfall + special_expense_this_year + debt_expense_this_year + edu_expense_this_year
        
        if total_shortfall_needed > 0:
            if cont_u >= total_shortfall_needed:
                cont_u -= total_shortfall_needed
                total_shortfall_needed = 0
            elif (cont_u + cont_s) >= total_shortfall_needed:
                total_shortfall_needed -= cont_u
                cont_u = 0
                cont_s -= total_shortfall_needed
                total_shortfall_needed = 0
            else:
                total_shortfall_needed -= (cont_u + cont_s)
                cont_u = 0
                cont_s = 0
                
        actual_withdrawal = total_shortfall_needed
        
        asset_u = asset_u + inv_income_u + cont_u
        asset_s = asset_s + inv_income_s + cont_s
        
        if actual_withdrawal > 0:
            if asset_u >= actual_withdrawal: asset_u -= actual_withdrawal
            else:
                actual_withdrawal -= asset_u; asset_u = 0; asset_s -= actual_withdrawal
                if asset_s < 0: asset_s = 0
                    
        total_family_asset = asset_u + asset_s
        if total_family_asset <= 0 and bankrupt_year is None and (user_retired or spouse_retired or special_expense_this_year > 0 or edu_expense_this_year > 0):
            bankrupt_year = year_label
            
        row_data = {
            "觀測年度": year_label,
            "參與者A資金結餘": int(asset_u),
            "總流動資產": int(total_family_asset),
            "年度總月退俸": int(total_pension_received),
            "通膨後預估支出": int(current_annual_expense) if (user_retired or spouse_retired) else 0,
            "子女教育支出": int(edu_expense_this_year),
            "重大專案支出": int(special_expense_this_year),
            "貸款攤還流出": int(debt_expense_this_year),
            "從資產提領金額": int(total_shortfall_needed)
        }
        if planning_mode == "雙人/家庭": row_data["參與者B資金結餘"] = int(asset_s)
        sim_rows.append(row_data)

    df_sim = pd.DataFrame(sim_rows)
    
    if bankrupt_year:
        st.markdown(f"""
        <div class="strategy-box alert-box">
            <div class="alert-title">🚨 資金枯竭危機應急指南 (系統預估於 {bankrupt_year} 年破產)</div>
            <div class="strategy-text">
                系統偵測到未來的現金流缺口將吃光所有本金。請考慮採取以下防禦戰術：<br><br>
                <b>1. 啟動半退休 (咖啡師退休) 模式：</b> 退休後尋找輕鬆的兼職工作（每月只需補足少許現金流），即可巨幅降低指數股票型基金資金池的提領壓力，讓資產起死回生。<br>
                <b>2. 延後退休臨界點：</b> 將「距離退休尚有幾年」調高 2 至 3 年。多累積 3 年的本金與少提領 3 年的花費，將產生巨大的數學複利差異。<br>
                <b>3. 債務與固定支出重組：</b> 檢視是否有信貸或未繳清的車貸，在退休前必須清償完畢。同時調降「預估退休後每月總支出」至基礎維生水準。<br>
                <b>4. 建構醫療險防線：</b> 資金枯竭最常見的致命傷是突發疾病。請確保退休前已具備完善的實支實付醫療險，避免大筆醫藥費一次性擊垮資金池。
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"### 📈 {prefix}資產長期軌跡")
    fig = go.Figure()
    
    if planning_mode == "雙人/家庭":
        fig.add_trace(go.Scatter(x=df_sim['觀測年度'], y=df_sim['參與者B資金結餘'], mode='lines', line=dict(width=0.5, color='#457b9d'), stackgroup='one', name='參與者B資金池'))
    
    fig.add_trace(go.Scatter(x=df_sim['觀測年度'], y=df_sim['參與者A資金結餘'], mode='lines', line=dict(width=0.5, color='#8CB35A'), stackgroup='one', name='參與者A資金池'))
    
    if bankrupt_year: fig.add_vline(x=bankrupt_year, line_dash="dot", line_color="#e63946", annotation_text=f"{bankrupt_year}年資產歸零")
        
    if user_years_to_retire > 0: fig.add_vline(x=current_year + user_years_to_retire, line_dash="dash", line_color="#e9c46a", annotation_text="參與者A退休", annotation_position="top left")
    if planning_mode == "雙人/家庭" and spouse_years_to_retire > 0: fig.add_vline(x=current_year + spouse_years_to_retire, line_dash="dash", line_color="#e9c46a", annotation_text="參與者B退休", annotation_position="top left")

    fig.update_layout(
        yaxis_title="金融資產結餘 (TWD)", 
        xaxis_title="觀測年度", 
        hovermode="x unified", 
        template="plotly_white",
        margin=dict(t=50, b=50)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("")
    with st.expander("📊 查看完整退休流水帳", expanded=False):
        df_formatted = df_sim.copy()
        for col in df_formatted.columns:
            if col != '觀測年度': df_formatted[col] = df_formatted[col].map(lambda x: f"{x:,}")
        st.dataframe(df_formatted, use_container_width=True, hide_index=True)