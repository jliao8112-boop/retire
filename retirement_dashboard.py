import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

# ==========================================
# 1. 網頁應用程式框架：全局配置
# ==========================================
st.set_page_config(page_title="ETF資產與退休提領的財務自由模擬面板", layout="wide")
st.title("ETF資產與退休提領的財務自由模擬面板")

# 建立單一縱向流或區塊流配置
col_input, col_output = st.columns([1, 2])

# ==========================================
# 2. 輸入控制區
# ==========================================
with col_input:
    st.header("【核心輸入參數區】")
    
    with st.expander("📅 日期與年資設定 (動態連動)", expanded=True):
        # 需求 1：自動填入今天的日期
        today_date = st.date_input("今天日期", datetime.date.today())
        
        # 需求 2：出生日期的日曆限定由 1965 年到 2065 年
        birth_date = st.date_input(
            "出生日期", 
            datetime.date(1975, 8, 12),
            min_value=datetime.date(1965, 1, 1),
            max_value=datetime.date(2065, 12, 31)
        )
        
        start_work_date = st.date_input("開始工作日期", datetime.date(2006, 3, 17))
        military_months = st.number_input("當兵年資 (月)", value=23, min_value=0, step=1)
        
        # 需求 3：不計年資的減少聯動到退休年資
        exclude_months = st.number_input("不計年資 (月)", value=0, min_value=0, step=1)
        retire_age = st.number_input("退休年齡 (歲)", value=55, min_value=1, max_value=100, step=1)
        
        # 基礎日期推算與例外處理（如閏年）
        retire_year = birth_date.year + retire_age
        try:
            retire_date = datetime.date(retire_year, birth_date.month, birth_date.day)
        except ValueError:
            retire_date = datetime.date(retire_year, birth_date.month, birth_date.day - 1)
            
        years_to_retire = retire_year - today_date.year
        
        # 年資聯動核心計算：總月數 = 基礎工作月數 + 當兵月數 - 不計年資月數
        base_work_months = (retire_date.year - start_work_date.year) * 12 + (retire_date.month - start_work_date.month)
        total_net_months = base_work_months + military_months - exclude_months
        retire_tenure_years = max(0.0, total_net_months / 12)
        
        st.info(f" 推算退休日期：**{retire_date.strftime('%Y年%m月%d日')}**\n\n"
                f" 距離退休尚有：**{max(0, years_to_retire):02d} 年**\n\n"
                f" 連動退休年資：**{retire_tenure_years:.2f} 年** ({max(0, total_net_months)} 個月)")

    with st.expander("💰 資產累積期與提領設定", expanded=True):
        principal = st.number_input("初始本金 (元)", value=10000000, step=100000)
        annual_contribution = st.number_input("每年投入金額 (元)", value=200000, step=10000)
        
        # 需求 5：複利%可計算到 50%
        expected_return_rate = st.number_input(
            "預期年化報酬率 (%)", 
            value=7.0, 
            min_value=0.0, 
            max_value=50.0, 
            step=0.1
        ) / 100
        
        # 計算退休啟動時點的本金總額
        calc_periods = max(0, years_to_retire)
        accumulated_value = principal
        for _ in range(calc_periods):
            accumulated_value = accumulated_value * (1 + expected_return_rate) + annual_contribution
            
        retire_starting_principal = st.number_input("退休啟動本金 (元)", value=int(accumulated_value), step=50000)
        withdrawal_rate = st.number_input("初始年提領率 (%)", value=4.0, step=0.1) / 100
        inflation_rate = st.number_input("預估年通貨膨脹率 (%)", value=2.0, step=0.1) / 100

# ==========================================
# 3. 核心運算邏輯：需求 4（由退休日往後算50年）
# ==========================================
simulation_rows = []
current_balance = retire_starting_principal
initial_withdrawal = int(current_balance * withdrawal_rate)
current_withdrawal = initial_withdrawal
start_retire_calendar_year = retire_date.year

for i in range(1, 51):
    # 計算實際的西元年度
    calendar_year = start_retire_calendar_year + i - 1
    investment_income = int(current_balance * expected_return_rate)
    
    if i > 1:
        current_withdrawal = int(current_withdrawal * (1 + inflation_rate))
        
    ending_balance = current_balance + investment_income - current_withdrawal
    
    simulation_rows.append({
        "序號": i,
        "觀測年度 (西元)": calendar_year,
        "期初資產本金": current_balance,
        "預期投資收益": investment_income,
        "抗通膨提領金額": current_withdrawal,
        "期末資產結餘": ending_balance
    })
    current_balance = ending_balance

df_simulation = pd.DataFrame(simulation_rows)
final_asset_balance = df_simulation.iloc[-1]["期末資產結餘"]
monthly_payout = int(initial_withdrawal / 12)
sustainability_status = "資產持續增長 (永遠花不完)" if final_asset_balance > retire_starting_principal else "資產有枯竭風險，請調整參數"

# ==========================================
# 4. 右欄：數據可視化與摘要輸出
# ==========================================
with col_output:
    st.header("【動態模擬結果摘要】")
    
    # 資訊指標面板
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("退休可提領金額 (月均)", f"{monthly_payout:,} 元")
    m_col2.metric("第50年預估剩餘資產", f"{final_asset_balance:,} 元")
    m_col3.metric("資產續航狀態評估", sustainability_status)
    
    st.divider()
    
    # 建立趨勢圖表：橫軸完全對齊實際西元年度
    fig = px.line(
        df_simulation, 
        x="觀測年度 (西元)", 
        y="期末資產結餘", 
        title=f"50年資產水位長期變化趨勢 ({start_retire_calendar_year} 年 － {start_retire_calendar_year + 49} 年)",
        template="plotly_white"
    )
    
    # 圖表外觀微調 (採用溫和的綠色線條呈現長期資產水位)
    fig.update_traces(line=dict(color="#8CB35A", width=4))
    fig.update_layout(
        yaxis_title="資產結餘 (TWD)",
        xaxis_title="觀測年度 (西元)",
        xaxis=dict(dtick=5),  # 每 5 年顯示一個刻度
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 資料框架顯示格式化
    df_formatted = df_simulation.copy()
    for col in ["期初資產本金", "預期投資收益", "抗通膨提領金額", "期末資產結餘"]:
        df_formatted[col] = df_formatted[col].map(lambda x: f"{x:,}")
        
    st.subheader("年度資產流水動態模擬詳細數據")
    st.dataframe(df_formatted, use_container_width=True, hide_index=True)
    
    st.info(
        "💡 **操作備註**：\n"
        "當投資組合鎖定全市場大盤指數股票型基金（如：006208）時，若能利用技術指標的「價跌量縮」位階精準捕捉長期向上的**甜甜價**，"
        "將有機會拉高預期年化報酬率至雙位數。本面板支援最高 50% 的複利模擬，能協助您更極端地測試極致滾存的財務軌跡。"
    )