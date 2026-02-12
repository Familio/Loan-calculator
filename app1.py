import streamlit as st
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(page_title="DE Loan & Mortgage Pro", layout="wide")

# Custom CSS for German Market feel
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🇩🇪 Finance Calculator")
mode = st.sidebar.radio("Select Category", ["🏠 House Mortgage", "🚗 Car Loan"])

# --- SHARED FUNCTIONS ---
def calculate_schedule(loan_amount, annual_interest, monthly_payment, annual_sondertilgung, max_years=40):
    balance = loan_amount
    data = []
    total_interest = 0
    
    for month in range(1, max_years * 12 + 1):
        if balance <= 0:
            break
            
        interest_charge = balance * (annual_interest / 100 / 12)
        principal_repayment = monthly_payment - interest_charge
        
        # Apply regular payment
        balance -= principal_repayment
        total_interest += interest_charge
        
        # Apply Sondertilgung (once a year in December)
        if month % 12 == 0 and balance > 0:
            balance -= annual_sondertilgung
            
        # Safety check for overpayment
        if balance < 0:
            balance = 0
            
        data.append({"Month": month, "Remaining_Debt": balance, "Total_Interest": total_interest})
        
    return pd.DataFrame(data)

# --- HOUSE MORTGAGE SECTION ---
if mode == "🏠 House Mortgage":
    st.title("Immobilienfinanzierung (Mortgage)")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("1. Object Costs")
        price = st.number_input("Purchase Price (€)", value=450000, step=5000)
        capital = st.number_input("Own Capital (Eigenkapital) (€)", value=90000, step=5000)
        
        st.subheader("2. Ancillary Costs (Nebenkosten)")
        state_tax = st.selectbox("Grunderwerbsteuer (%)", 
                               options=[3.5, 5.0, 5.5, 6.0, 6.5], index=4, 
                               help="NRW/Berlin: 6.5%, Bavaria: 3.5%")
        notar_rate = st.slider("Notar & Grundbuch (%)", 1.0, 2.5, 2.0)
        makler_rate = st.number_input("Makler Fee (%)", value=3.57)
        
        st.subheader("3. Loan Terms")
        interest = st.number_input("Annual Interest (%)", value=3.85, step=0.05)
        tilgung = st.number_input("Initial Repayment (Tilgung %) ", value=2.0, step=0.1)
        sondertilgung = st.number_input("Annual Extra Payment (€)", value=0, step=500)
        
        fixed_period = st.selectbox("Fixed Interest Period (Years)", [10, 15, 20, 25, 30, "Manual"])
        if fixed_period == "Manual":
            fixed_period = st.number_input("Enter years", value=12)

        st.subheader("4. Mieteinnahmen (Rent)")
        rent_1 = st.number_input("Apartment 1: Net Rent (€/mo)", value=0, step=50)
        rent_2 = st.number_input("Apartment 2: Net Rent (€/mo)", value=0, step=50)
        bank_recognition = st.slider("Income Recognition (%)", 50, 100, 90, help="Banks usually count 90% of rent for safety.")

    # Logic: Calculations
    nebunkosten_total = price * (state_tax + notar_rate + makler_rate) / 100
    total_investment = price + nebunkosten_total
    loan_needed = total_investment - capital
    
    # German Annuity Rate = (Interest + Tilgung) * Loan / 12
    monthly_rate = (loan_needed * (interest + tilgung) / 100) / 12
    
    # Rent Calculations
    total_rent = rent_1 + rent_2
    effective_rent = total_rent * (bank_recognition / 100)
    net_monthly_burden = monthly_rate - effective_rent
    
    df_mortgage = calculate_schedule(loan_needed, interest, monthly_rate, sondertilgung)
    
    with col2:
        st.subheader("Financial Overview")
        m1, m2, m3 = st.columns(3)
        m1.metric("Monthly Loan Rate", f"{monthly_rate:,.2f} €")
        m2.metric("Total Net Rent", f"{total_rent:,.2f} €")
        
        # Highlight the Net Monthly Burden
        st.metric("NET MONTHLY BURDEN", f"{net_monthly_burden:,.2f} €", 
                  delta="Out of pocket" if net_monthly_burden > 0 else "Cashflow Positive",
                  delta_color="inverse" if net_monthly_burden > 0 else "normal")
        
        st.write("---")
        st.write(f"**Total Required (incl. fees):** {total_investment:,.2f} €")
        st.write(f"**Loan Amount:** {loan_needed:,.2f} €")
        st.write(f"**Nebenkosten total:** {nebunkosten_total:,.2f} €")
        
        # Results after Fixed Period
        months_fixed = fixed_period * 12
        if not df_mortgage.empty and len(df_mortgage) >= months_fixed:
            restschuld = df_mortgage.iloc[months_fixed-1]['Remaining_Debt']
            paid_interest = df_mortgage.iloc[months_fixed-1]['Total_Interest']
        elif not df_mortgage.empty:
            restschuld = 0
            paid_interest = df_mortgage['Total_Interest'].max()
        else:
            restschuld = 0
            paid_interest = 0

        st.write("---")
        st.subheader(f"Status after {fixed_period} Years")
        r1, r2 = st.columns(2)
        r1.error(f"Remaining Debt: {restschuld:,.2f} €")
        r2.info(f"Total Interest Paid: {paid_interest:,.2f} €")
        
        # Timeline Chart
        if not df_mortgage.empty:
            st.line_chart(df_mortgage.set_index("Month")["Remaining_Debt"])
            years_total = len(df_mortgage) / 12
            st.success(f"⏱ Estimated total time to pay off: **{years_total:.1f} years**")

# --- CAR LOAN SECTION ---
else:
    st.title("Autokredit (Car Loan)")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        car_price = st.number_input("Car Price (€)", value=35000)
        car_down = st.number_input("Down Payment (€)", value=5000)
        
        term_type = st.selectbox("Term (Years)", [1, 2, 3, 4, 5, 6, 7, "Manual"])
        if term_type == "Manual":
            car_years = st.number_input("Enter Years", value=4)
        else:
            car_years = term_type
            
        car_interest = st.number_input("Interest Rate (%)", value=5.99)
        car_sondertilgung = st.number_input("Yearly Bonus Payment (€)", value=0)

    # Standard Amortization Formula
    car_loan = car_price - car_down
    months_car = car_years * 12
    r_car = (car_interest / 100) / 12
    
    if car_loan > 0:
        car_monthly = car_loan * (r_car * (1 + r_car)**months_car) / ((1 + r_car)**months_car - 1)
    else:
        car_monthly = 0
        
    df_car = calculate_schedule(car_loan, car_interest, car_monthly, car_sondertilgung, max_years=car_years+1)

    with col2:
        st.metric("Monthly Car Payment", f"{car_monthly:,.2f} €")
        st.write(f"**Net Loan Amount:** {car_loan:,.2f} €")
        
        st.subheader("Payment Schedule")
        if not df_car.empty:
            st.area_chart(df_car.set_index("Month")["Remaining_Debt"])
            total_interest_car = df_car['Total_Interest'].max()
            st.write(f"Total Interest Paid over {car_years}y: **{total_interest_car:,.2f} €**")
            
            if car_sondertilgung > 0:
                actual_months = len(df_car)
                saved_months = (car_years * 12) - actual_months
                st.success(f"Sondertilgung saves you **{saved_months} months** of debt!")
