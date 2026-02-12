import streamlit as st
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(page_title="DE Loan & Mortgage Pro", layout="wide")

# Custom CSS for German Market feel (Fixed the unsafe_allow_html=True error)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# --- SHARED FUNCTIONS ---
def calculate_schedule(loan_amount, annual_interest, monthly_payment, annual_sondertilgung, max_years=40):
    balance = loan_amount
    data = []
    total_interest = 0
    
    for month in range(1, max_years * 12 + 1):
        if balance <= 0: break
        interest_charge = balance * (annual_interest / 100 / 12)
        principal_repayment = monthly_payment - interest_charge
        balance -= principal_repayment
        total_interest += interest_charge
        if month % 12 == 0 and balance > 0: balance -= annual_sondertilgung
        if balance < 0: balance = 0
        data.append({"Month": month, "Remaining_Debt": balance, "Total_Interest": total_interest})
    return pd.DataFrame(data)

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🇩🇪 Finance Calculator")
mode = st.sidebar.radio("Select Category", ["🏠 House Mortgage", "🚗 Car Loan"])

# --- HOUSE MORTGAGE SECTION ---
if mode == "🏠 House Mortgage":
    st.title("Immobilienfinanzierung mit Mieteinnahmen")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("1. Purchase & Capital")
        price = st.number_input("Purchase Price (€)", value=450000, step=5000)
        capital = st.number_input("Own Capital (Eigenkapital) (€)", value=90000, step=5000)
        
        st.subheader("2. German Ancillary Costs")
        # German States 2026 Tax Rates
        tax_map = {"Bavaria": 3.5, "Berlin/Hesse/Meck-Pomm": 6.0, "NRW/BW/others": 6.5, "Hamburg/Saxony": 5.5}
        state = st.selectbox("Bundesland (Tax Rate)", list(tax_map.keys()))
        state_tax = tax_map[state]
        notar_rate = st.slider("Notar & Grundbuch (%)", 1.0, 2.5, 2.0)
        makler_rate = st.number_input("Makler Fee (%)", value=3.57)
        
        st.subheader("3. Loan & Repayment")
        interest = st.number_input("Annual Interest (%)", value=3.85, step=0.05)
        tilgung = st.number_input("Initial Repayment (Tilgung %)", value=2.0, step=0.1)
        sondertilgung = st.number_input("Annual Extra Payment (€)", value=0, step=500)
        fixed_period = st.number_input("Fixed Interest Years", value=10, min_value=1)

        st.subheader("4. Rental Income (Net Rent)")
        rent1 = st.number_input("Unit 1: Net Rent (€/mo)", value=800, step=50)
        rent2 = st.number_input("Unit 2: Net Rent (€/mo)", value=0, step=50)
        safety_factor = st.slider("Income Recognition (%)", 50, 100, 90, help="Banks often count only 90% of rent.")

    # Calculations
    nebunkosten_total = price * (state_tax + notar_rate + makler_rate) / 100
    total_investment = price + nebunkosten_total
    loan_needed = total_investment - capital
    monthly_loan_rate = (loan_needed * (interest + tilgung) / 100) / 12
    
    # Rental Logic
    total_gross_rent = rent1 + rent2
    effective_rent = total_gross_rent * (safety_factor / 100)
    net_monthly_burden = monthly_loan_rate - effective_rent
    
    df_mortgage = calculate_schedule(loan_needed, interest, monthly_loan_rate, sondertilgung)
    
    with col2:
        st.subheader("Financial Performance")
        m1, m2, m3 = st.columns(3)
        m1.metric("Monthly Loan Rate", f"{monthly_loan_rate:,.2f} €")
        m2.metric("Total Net Rent", f"{total_gross_rent:,.2f} €", delta=f"{effective_rent:,.2f} (Effective)")
        
        # Display the Net Burden
        color = "normal" if net_monthly_burden > 0 else "inverse"
        st.metric("YOUR NET BURDEN", f"{net_monthly_burden:,.2f} €/mo", 
                  help="This is your monthly loan rate minus recognized rental income.")

        st.write("---")
        st.write(f"**Total Required (incl. fees):** {total_investment:,.2f} €")
        st.write(f"**Loan Amount:** {loan_needed:,.2f} €")
        
        # Results after Fixed Period
        months_fixed = fixed_period * 12
        restschuld = df_mortgage.iloc[min(months_fixed-1, len(df_mortgage)-1)]['Remaining_Debt'] if not df_mortgage.empty else 0
        
        st.subheader(f"Status after {fixed_period} Years")
        r1, r2 = st.columns(2)
        r1.error(f"Remaining Debt: {restschuld:,.2f} €")
        r2.info(f"Time to 0: {len(df_mortgage)/12:.1f} years")
        
        st.line_chart(df_mortgage.set_index("Month")["Remaining_Debt"])

# --- CAR LOAN SECTION ---
else:
    st.title("Autokredit (Car Loan)")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        car_price = st.number_input("Car Price (€)", value=35000)
        car_down = st.number_input("Down Payment (€)", value=5000)
        car_years = st.number_input("Term (Years)", value=4, min_value=1)
        car_interest = st.number_input("Interest Rate (%)", value=5.99)
        car_sondertilgung = st.number_input("Yearly Bonus Payment (€)", value=0)

    car_loan = car_price - car_down
    months_car = car_years * 12
    r_car = (car_interest / 100) / 12
    car_monthly = car_loan * (r_car * (1 + r_car)**months_car) / ((1 + r_car)**months_car - 1) if car_loan > 0 else 0
        
    df_car = calculate_schedule(car_loan, car_interest, car_monthly, car_sondertilgung, max_years=car_years+1)

    with col2:
        st.metric("Monthly Payment", f"{car_monthly:,.2f} €")
        st.area_chart(df_car.set_index("Month")["Remaining_Debt"])
        st.write(f"Total Interest: {df_car['Total_Interest'].max():,.2f} €")
