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
# 2. 狀態管理 (Session State 初始化)
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
    "college_start_age": 18,
    "college_years": 4,
    "annual_college_cost": 250000,
    "user_principal": 1500000,
    "user_annual_contribution": 150000,
    "user_years_to_retire": 15,
    "user_pension_strategy": "正常請領",
    "user_monthly_pension": 25000,
    "user_lump_sum": 2000000,
    "spouse_principal": 1000000,
    "spouse_annual_contribution": 100000,
    "spouse_years_to_retire": 15,
    "spouse_pension_strategy": "正常請領",
    "spouse_monthly_pension": 25000,
    "spouse_lump_sum": 2000000,
    "expected_return_pct": 6.0,
    "post_retire_expense": 60000,
    "basic_inflation_pct": 2.0,
    "special_inflation_pct": 3.5,
    "exp1_name": "", "exp1_year": 0, "exp1_amount": 0,
    "exp2_name": "", "exp2_year": 0, "exp2_amount": 0,
    "exp3_name": "", "exp3_year": 0, "exp3_amount": 0,
}

for i in range(1, 6):
    default_values[f"child_{i}_age"] = 10 - (i-1)*2 if (10 - (i-1)*2) > 0 else 0

key_mapping = {
    "規劃模式": "planning_mode", "扶養子女數": "dependent_children", "扶養長輩數": "dependent_elders",
    "年總收入": "annual_income", "年總基礎支出": "annual_expense", "高流動現金存款": "cash_assets",
    "不動產現值": "real_estate_value", "剩餘貸款本金": "loan_principal", "貸款年利率": "loan_interest_rate",
    "剩餘攤還年限": "loan_years_remaining", "預計就讀大學年齡": "college_start_age",
    "預計就讀年數": "college_years", "每人每年大學總花費": "annual_college_cost",
    "參與者A_初始本金": "user_principal", "參與者A_每年投入金額": "user_annual_contribution",
    "參與者A_距離退休年數": "user_years_to_retire", "參與者A_請領策略": "user_pension_strategy",
    "參與者A_預估月退俸": "user_monthly_pension", "參與者A_預估一次請領": "user_lump_sum",
    "參與者B_初始本金": "spouse_principal", "參與者B_每年投入金額": "spouse_annual_contribution",
    "參與者B_距離退休年數": "spouse_years_to_retire", "參與者B_請領策略": "spouse_pension_strategy",
    "參與者B_預估月退俸": "spouse_monthly_pension", "參與者B_預估一次請領": "spouse_lump_sum",
    "預期年化報酬率": "expected_return_pct", "退休後每月總支出": "post_retire_expense",
    "基本生活通膨率": "basic_inflation_pct", "特殊專案通膨率": "special_inflation_pct",
    "支出1名稱": "exp1_name", "支出1幾年後": "exp1_year", "支出1總額": "exp1_amount",
    "支出2名稱": "exp2_name", "支出2幾年後": "exp2_year", "支出2總額": "exp2_amount",
    "支出3名稱": "exp3_name", "支出3幾年後": "exp3_year", "支出3總額": "exp3_amount"
}
for i in range(1, 6):
    key_mapping[f"第{i}位子女年齡"] = f"child_{i}_age"

# 若資料庫無該數值，則先寫入預設值
for key, val in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ==========================================
# 3. 側邊欄：匯入設定與強制綁定 Key 的輸入區塊
# ==========================================
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
                    if state_key in ["planning_mode", "user_pension_strategy", "spouse_pension_strategy", "exp1_name", "exp2_name", "exp3_name"]: 
                        st.session_state[state_key] = str(val) if pd.notna(val) else ""
                    elif "pct" in state_key or state_key == "loan_interest_rate":
                        st.session_state[state_key] = float(val) if pd.notna(val) else 0.0
                    else:
                        st.session_state[state_key] = int(val) if pd.notna(val) else 0
            st.success("設定檔匯入成功！")
        except Exception as e:
            st.error("檔案格式錯誤或讀取失敗。")
            
    st.divider()
    st.header("⚙️ 財務參數輸入")
    
    st.radio("選擇財務規劃模式", ["雙人/家庭", "單人"], horizontal=True, key="planning_mode")
    prefix = "家庭" if st.session_state.get("planning_mode", "雙人/家庭") == "雙人/家庭" else "個人"
    st.write("")

    with st.expander(f"👥 扶養與收支現況", expanded=False):
        st.number_input("扶養子女數 (人)", min_value=0, max_value=5, step=1, key="dependent_children")
        st.number_input("扶養長輩數 (人)", step=1, key="dependent_elders")
        st.divider()
        st.number_input(f"{prefix}年總收入 (元)", step=50000, key="annual_income")
        st.number_input(f"{prefix}年總基礎支出 (元)", step=50000, help="不含貸款還款之基本生活開銷", key="annual_expense")
        st.divider()
        st.number_input("高流動現金存款 (元)", step=50000, key="cash_assets")
        st.number_input("不動產現值 (元)", step=500000, key="real_estate_value")

    with st.expander("🏦 負債與攤還設定 (本金平均攤還)", expanded=True):
        st.number_input("剩餘貸款本金 (元)", step=100000, key="loan_principal")
        st.number_input("貸款年利率 (%)", step=0.1, key="loan_interest_rate")
        st.number_input("剩餘攤還年限 (年)", step=1, key="loan_years_remaining")

    with st.expander("🎓 子女高等教育經費", expanded=True):
        dep_child = st.session_state.get("dependent_children", 1)
        if dep_child > 0:
            st.caption("請輸入每一位子女的目前年齡：")
            cols = st.columns(min(dep_child, 3))
            for i in range(dep_child):
                col_idx = i % 3
                cols[col_idx].number_input(f"第 {i+1} 位年齡", step=1, key=f"child_{i+1}_age")
            st.divider()
        else:
            st.info("目前設定無扶養子女。")
            
        st.number_input("預計就讀大學年齡 (歲)", step=1, key="college_start_age")
        st.number_input("預計就讀年數 (年)", step=1, key="college_years")
        st.number_input("『每人』每年大學總花費 (元/年)", step=10000, key="annual_college_cost")

    with st.expander("📌 自訂階段性重大支出", expanded=True):
        for i in range(1, 4):
            c1, c2, c3 = st.columns([2, 1, 1.5], gap="small")
            c1.text_input(f"支出 {i} 名稱", key=f"exp{i}_name")
            c2.number_input("幾年後", step=1, key=f"exp{i}_year")
            c3.number_input("現值總額", step=50000, key=f"exp{i}_amount")
            if i < 3: st.write("")

    with st.expander("👨 參與者 A：法定年金與資產模擬", expanded=True):
        st.number_input("初始本金 (元)", step=50000, key="user_principal")
        st.number_input("每年投入金額 (元)", step=10000, key="user_annual_contribution")
        st.slider("距離原定退休尚有幾年？", 0, 40, key="user_years_to_retire")
        
        st.divider()
        st.selectbox("法定退休金請領策略", ["正常請領", "提早 5 年 (-20%)", "延後 5 年 (+20%)", "一次請領"], key="user_pension_strategy")
        if st.session_state.get("user_pension_strategy", "正常請領") == "一次請領":
            st.number_input("預估一次請領總額 (元)", step=100000, key="user_lump_sum")
        else:
            st.number_input("預估基準月退俸 (元)", step=5000, key="user_monthly_pension")

    if st.session_state.get("planning_mode", "雙人/家庭") == "雙人/家庭":
        with st.expander("👩 參與者 B：法定年金與資產模擬", expanded=True):
            st.number_input("參與者B_初始本金 (元)", step=50000, key="spouse_principal")
            st.number_input("參與者B_每年投入金額 (元)", step=10000, key="spouse_annual_contribution")
            st.slider("參與者B_距離原定退休尚有幾年？", 0, 40, key="spouse_years_to_retire")
            
            st.divider()
            st.selectbox("參與者B_法定退休金請領策略", ["正常請領", "提早 5 年 (-20%)", "延後 5 年 (+20%)", "一次請領"], key="spouse_pension_strategy")
            if st.session_state.get("spouse_pension_strategy", "正常請領") == "一次請領":
                st.number_input("參與者B_預估一次請領總額 (元)", step=100000, key="spouse_lump_sum")
            else:
                st.number_input("參與者B_預估基準月退俸 (元)", step=5000, key="spouse_monthly_pension")
        
    with st.expander("📈 總體經濟參數 (雙軌通膨)", expanded=True):
        st.slider("預期年化報酬率 (%)", 0.0, 20.0, step=0.1, key="expected_return_pct")
        st.number_input("預估退休後『每月』總支出 (元)", step=5000, key="post_retire_expense")
        st.divider()
        st.slider("基本生活通膨率 (%)", 0.0, 10.0, step=0.1, help="套用於日常支出，並作為年金抗通膨的調升依據。", key="basic_inflation_pct")
        st.slider("特殊專案通膨率 (%)", 0.0, 15.0, step=0.1, help="套用於自訂階段性重大支出與大學教育經費。", key="special_inflation_pct")

    st.divider()
    st.download_button(
        label="📥 匯出個人設定檔 (CSV)",
        data=pd.DataFrame({"參數名稱": list(key_mapping.keys()), "設定值": [st.session_state.get(k, 0) for k in key_mapping.values()]}).to_csv(index=False).encode('utf-8-sig'),
        file_name=f"{prefix}財務設定檔_{datetime.date.today().strftime('%Y%m%d')}.csv", mime="text/csv"
    )

# ==========================================
# 4. 核心運算：後台狀態全面安全提取 (防崩潰機制)
# ==========================================
# 透過 .get() 防禦 Streamlit 的元件銷毀機制
annual_income = st.session_state.get("annual_income", 1100000)
annual_expense = st.session_state.get("annual_expense", 850000)
cash_assets = st.session_state.get("cash_assets", 500000)
real_estate_value = st.session_state.get("real_estate_value", 10000000)
loan_principal = st.session_state.get("loan_principal", 5000000)
loan_interest_rate = st.session_state.get("loan_interest_rate", 2.1)
loan_years_remaining = st.session_state.get("loan_years_remaining", 20)
dependent_children = st.session_state.get("dependent_children", 1)

college_start_age = st.session_state.get("college_start_age", 18)
college_years = st.session_state.get("college_years", 4)
annual_college_cost = st.session_state.get("annual_college_cost", 250000)

user_principal = st.session_state.get("user_principal", 1500000)
user_annual_contribution = st.session_state.get("user_annual_contribution", 150000)
user_years_to_retire = st.session_state.get("user_years_to_retire", 15)

user_pension_strategy = st.session_state.get("user_pension_strategy", "正常請領")
user_monthly_pension = st.session_state.get("user_monthly_pension", 25000)
user_lump_sum = st.session_state.get("user_lump_sum", 2000000)

# 單人模式下強勢覆蓋配偶參數為 0，且即使元件隱藏也能安全讀取
is_double = (st.session_state.get("planning_mode", "雙人/家庭") == "雙人/家庭")
spouse_principal = st.session_state.get("spouse_principal", 1000000) if is_double else 0
spouse_annual_contribution = st.session_state.get("spouse_annual_contribution", 100000) if is_double else 0
spouse_years_to_retire = st.session_state.get("spouse_years_to_retire", 15) if is_double else 0
spouse_pension_strategy = st.session_state.get("spouse_pension_strategy", "正常請領")
spouse_monthly_pension = st.session_state.get("spouse_monthly_pension", 25000)
spouse_lump_sum = st.session_state.get("spouse_lump_sum", 2000000)

expected_return = st.session_state.get("expected_return_pct", 6.0) / 100
post_retire_expense = st.session_state.get("post_retire_expense", 60000)
basic_inflation = st.session_state.get("basic_inflation_pct", 2.0) / 100
special_inflation = st.session_state.get("special_inflation_pct", 3.5) / 100

def calculate_annual_debt_payment(principal, annual_rate, years, current_year_index):
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
monthly_expense_now = (annual_expense + first_year_debt_pay) / 12 if (annual_expense + first_year_debt_pay) > 0 else 1
total_financial_assets = user_principal + spouse_principal
emergency_months = cash_assets / monthly_expense_now if monthly_expense_now > 0 else 0
savings_rate = ((annual_income - annual_expense - first_year_debt_pay) / annual_income) * 100 if annual_income > 0 else 0
total_assets_value = cash_assets + total_financial_assets + real_estate_value
debt_ratio = (loan_principal / total_assets_value) * 100 if total_assets_value > 0 else 0
current_passive_income = (total_financial_assets * expected_return) / 12
pre_retire_fi_rate = (current_passive_income / monthly_expense_now) * 100 if monthly_expense_now > 0 else 0
safe_em_months = 6 if is_double else 9
warn_em_months = 3 if is_double else 6

# ----------------------------------------------------
# 執行 50 年長期壓力測試，確保第一階段數據能精準對接
# ----------------------------------------------------
current_year = datetime.date.today().year
asset_u, asset_s = user_principal, spouse_principal
current_annual_expense = post_retire_expense * 12
sim_rows = []
bankrupt_year = None

u_retire_trigger = user_years_to_retire
u_base_pension = user_monthly_pension
if user_pension_strategy == "提早 5 年 (-20%)":
    u_retire_trigger = max(0, user_years_to_retire - 5)
    u_base_pension = user_monthly_pension * 0.8
elif user_pension_strategy == "延後 5 年 (+20%)":
    u_retire_trigger = user_years_to_retire + 5
    u_base_pension = user_monthly_pension * 1.2

s_retire_trigger = spouse_years_to_retire
s_base_pension = spouse_monthly_pension
if is_double:
    if spouse_pension_strategy == "提早 5 年 (-20%)":
        s_retire_trigger = max(0, spouse_years_to_retire - 5)
        s_base_pension = spouse_monthly_pension * 0.8
    elif spouse_pension_strategy == "延後 5 年 (+20%)":
        s_retire_trigger = spouse_years_to_retire + 5
        s_base_pension = spouse_monthly_pension * 1.2

for i in range(1, 51):
    year_label = current_year + i
    user_retired = i > user_years_to_retire
    spouse_retired = (i > spouse_years_to_retire) if is_double else False
    u_is_receiving = i > u_retire_trigger
    s_is_receiving = (i > s_retire_trigger) if is_double else False
    
    inv_income_u = int(asset_u * expected_return) if asset_u > 0 else 0
    inv_income_s = int(asset_s * expected_return) if asset_s > 0 else 0
    cont_u = user_annual_contribution if not user_retired else 0
    cont_s = spouse_annual_contribution if not spouse_retired else 0
    
    # 執行一次請領資金匯入
    if user_pension_strategy == "一次請領" and i == user_years_to_retire:
        asset_u += user_lump_sum
    if is_double and spouse_pension_strategy == "一次請領" and i == spouse_years_to_retire:
        asset_s += spouse_lump_sum
        
    pension_u = 0
    if u_is_receiving and user_pension_strategy != "一次請領":
        years_receiving_u = i - u_retire_trigger
        pension_u = int(u_base_pension * 12 * ((1 + basic_inflation) ** years_receiving_u))
        
    pension_s = 0
    if s_is_receiving and spouse_pension_strategy != "一次請領" and is_double:
        years_receiving_s = i - s_retire_trigger
        pension_s = int(s_base_pension * 12 * ((1 + basic_inflation) ** years_receiving_s))
        
    total_pension_received = pension_u + pension_s
    debt_expense_this_year = calculate_annual_debt_payment(loan_principal, loan_interest_rate, loan_years_remaining, i-1)
    if i > 1: current_annual_expense = int(current_annual_expense * (1 + basic_inflation))
        
    edu_expense_this_year = 0
    for child_idx in range(1, int(dependent_children) + 1):
        current_child_age = st.session_state.get(f"child_{child_idx}_age", 0) + i
        if college_start_age <= current_child_age < college_start_age + college_years:
            edu_expense_this_year += int(annual_college_cost * ((1 + special_inflation) ** i))

    special_expense_this_year = 0
    for j in range(1, 4):
        if st.session_state.get(f"exp{j}_name", "") != "" and st.session_state.get(f"exp{j}_year", 0) == i:
            special_expense_this_year += int(st.session_state.get(f"exp{j}_amount", 0) * ((1 + special_inflation) ** i))
        
    # 房貸雙重扣除修正：一旦進入退休階段，停止主動薪水扣除，轉由資產池負責承擔
    is_retired_phase = user_retired or spouse_retired
    active_debt_expense = debt_expense_this_year if is_retired_phase else 0
    base_shortfall = max(0, current_annual_expense - total_pension_received) if is_retired_phase else 0
    
    total_shortfall_needed = base_shortfall + special_expense_this_year + active_debt_expense + edu_expense_this_year
    
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
    if total_family_asset <= 0 and bankrupt_year is None and (is_retired_phase or special_expense_this_year > 0 or edu_expense_this_year > 0):
        bankrupt_year = year_label
        
    row_data = {
        "觀測年度": year_label,
        "參與者A資金池": int(asset_u),
        "總流動資產": int(total_family_asset),
        "抗通膨年金收入": int(total_pension_received),
        "通膨後基礎支出": int(current_annual_expense) if is_retired_phase else 0,
        "多名子女教育總額": int(edu_expense_this_year),
        "重大專案支出": int(special_expense_this_year),
        "貸款攤還流出": int(active_debt_expense),
        "從資產提領總額": int(total_shortfall_needed)
    }
    if is_double: row_data["參與者B資金池"] = int(asset_s)
    sim_rows.append(row_data)

df_sim = pd.DataFrame(sim_rows)

# 同步提取邁入主退休年份的那一年真實資產水位，傳遞給第一階段
retire_target_year = current_year + user_years_to_retire
if user_years_to_retire > 0 and retire_target_year <= current_year + 50:
    total_future_assets = df_sim[df_sim['觀測年度'] == retire_target_year]['總流動資產'].values[0]
else:
    total_future_assets = total_financial_assets

total_future_pension = (user_monthly_pension if user_pension_strategy != "一次請領" else 0) + (spouse_monthly_pension if is_double and spouse_pension_strategy != "一次請領" else 0)
future_passive_income = (total_future_assets * expected_return) / 12
post_retire_fi_rate = ((total_future_pension + future_passive_income) / post_retire_expense) * 100 if post_retire_expense > 0 else 0

# ==========================================
# 5. 主畫面：分頁架構
# ==========================================
st.title(f"🏦 通用版{prefix}財務戰情中心")
st.write("")

tab1, tab2 = st.tabs(["🏥 第一階段：財務體質檢驗", "🚀 第二階段：年金策略與資產壓力測試"])

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
    st.markdown("### 🧭 現有資產戰略診斷")
    
    if pre_retire_fi_rate >= 100: pre_strat = "<b>完全財務獨立：</b>當下的資產孳息已超越目前開銷。現階段的工作純屬個人選擇，無需急於將閒置資金全部投入，可將目標設定為觀察名單，耐心等待優質資產來到<b>甜甜價</b>時再進行長線佈局，同時開始提高生活品質。"
    elif pre_retire_fi_rate >= 50: pre_strat = "<b>具備半退休底氣：</b>資產已具備強大防禦力。請保持年度投入紀律，避免盲目擴張消費，耐心等待資產複利增長。"
    else: pre_strat = "<b>高度依賴主動收入：</b>目前資產孳息不足以支撐現有生活。首要任務是保住本業收入，透過提高「淨儲蓄率」加大投入力道。"

    st.markdown(f"""
    <div class="strategy-box" style="border-left-color: #e9c46a;">
        <div class="strategy-title">🏃‍♂️ 累積期操作策略</div>
        <div class="strategy-text">{pre_strat}</div>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------
# Tab 2: 長期退休資產壓力測試
# ------------------------------------------
with tab2:
    st.write("")
    if bankrupt_year:
        st.markdown(f"""
        <div class="strategy-box alert-box">
            <div class="alert-title">🚨 資金枯竭危機 (系統預估於 {bankrupt_year} 年破產)</div>
            <div class="strategy-text">
                系統偵測到未來的現金流缺口將吃光所有本金。建議調整請領策略（如改為提早/正常請領以獲取穩定現金流底座），或檢視是否需延後退休年份。
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"### 📈 {prefix}資產長期軌跡與請領策略實測")
    fig = go.Figure()
    
    if is_double:
        fig.add_trace(go.Scatter(x=df_sim['觀測年度'], y=df_sim['參與者B資金池'], mode='lines', line=dict(width=0.5, color='#457b9d'), stackgroup='one', name='參與者B資金池'))
    
    fig.add_trace(go.Scatter(x=df_sim['觀測年度'], y=df_sim['參與者A資金池'], mode='lines', line=dict(width=0.5, color='#8CB35A'), stackgroup='one', name='參與者A資金池'))
    
    if bankrupt_year: fig.add_vline(x=bankrupt_year, line_dash="dot", line_color="#e63946", annotation_text=f"{bankrupt_year}年歸零")
        
    if user_years_to_retire > 0: fig.add_vline(x=current_year + user_years_to_retire, line_dash="dash", line_color="#e9c46a", annotation_text="A原定退休", annotation_position="top left")

    fig.update_layout(
        yaxis_title="金融資產結餘 (TWD)", 
        xaxis_title="觀測年度", 
        hovermode="x unified", 
        template="plotly_white",
        margin=dict(t=50, b=50)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("")
    with st.expander("📊 查看完整流水帳 (含抗通膨年金與各項現金流)", expanded=False):
        df_formatted = df_sim.copy()
        for col in df_formatted.columns:
            if col != '觀測年度': df_formatted[col] = df_formatted[col].map(lambda x: f"{x:,}")
        st.dataframe(df_formatted, use_container_width=True, hide_index=True)