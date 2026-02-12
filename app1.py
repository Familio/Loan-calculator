import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="DE Mortgage Pro", layout="wide")

# Fix for the previous error
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# --- 🏠 HOUSE MORTGAGE SECTION ---
st.title("Hausfinanzierung & Mietrechner")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Kosten & Steuer")
    price = st.number_input("Purchase Price (€)", value=400000)
    capital = st.number_input("Own Capital (€)", value=80000)
    
    # German State Tax Logic
    tax_rates = {"Bayern": 3.5, "NRW": 6.5, "Berlin": 6.0, "Hessen": 6.0, "Hamburg": 5.5, "Sachsen": 5.5}
    state = st.selectbox("Bundesland", list(tax_rates.keys()))
    
    st.subheader("2. Finanzierung")
    interest = st.number_input("Interest Rate (%)", value=3.8)
    tilgung = st.number_input("Repayment (Tilgung %)", value=2.0)
    
    # NEW FIELDS: RENTAL INCOME
    st.subheader("3. Mieteinnahmen (Rental)")
    rent_apt_1 = st.number_input("Net Rent Apartment 1 (€)", value=0, help="Kaltmiete")
    rent_apt_2 = st.number_input("Net Rent Apartment 2 (€)", value=0, help="Kaltmiete")
    bank_haircut = st.slider("Bank Recognition (%)", 50, 100, 90, help="Banks usually count 90% of rent.")

# --- CALCULATIONS ---
# Nebenkosten: Notar (2%) + Makler (3.57%) + State Tax
total_fees_rate = 2.0 + 3.57 + tax_rates[state]
ancillary_costs = price * (total_fees_rate / 100)
total_needed = price + ancillary_costs
loan_amount = total_needed - capital

# Monthly Loan Rate
monthly_loan = (loan_amount * (interest + tilgung) / 100) / 12

# Rental Calculation
total_gross_rent = rent_apt_1 + rent_apt_2
effective_rent = total_gross_rent * (bank_haircut / 100)
net_monthly_burden = monthly_loan - effective_rent

# --- DISPLAY RESULTS ---
with col2:
    st.subheader("Ergebnis (Results)")
    
    r1, r2, r3 = st.columns(3)
    r1.metric("Monthly Loan", f"{monthly_loan:,.2f} €")
    r2.metric("Total Rent Income", f"{total_gross_rent:,.2f} €")
    
    # Net Burden with color coding
    if net_monthly_burden > 0:
        st.metric("YOUR NET BURDEN", f"{net_monthly_burden:,.2f} €", delta="Your Pay", delta_color="inverse")
    else:
        st.metric("SURPLUS (Profit)", f"{abs(net_monthly_burden):,.2f} €", delta="Passive Income", delta_color="normal")

    st.write("---")
    with st.expander("Detailed Cost Breakdown"):
        st.write(f"**Total Ancillary Costs (Fees):** {ancillary_costs:,.2f} €")
        st.write(f"**Final Loan Amount:** {loan_amount:,.2f} €")
        st.write(f"**Tax Rate ({state}):** {tax_rates[state]}%")
