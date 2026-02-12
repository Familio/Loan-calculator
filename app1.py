import streamlit as st

# Setup Page
st.set_page_config(page_title="DE Loan Calculator", layout="wide")

# Sidebar Navigation
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Select Calculator", ["🚗 Car Loan", "🏠 House Mortgage"])

# --- CAR LOAN SECTION ---
if app_mode == "🚗 Car Loan":
    st.title("Car Loan Calculator (German Market)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        vehicle_price = st.number_input("Vehicle Price (€)", min_value=0, value=30000)
        down_payment = st.number_input("Down Payment (€)", min_value=0, value=5000)
        
        # German Market Standards
        months = st.selectbox("Term (Months)", [24, 36, 48, 60, 72, 84, 96])
        
        interest_type = st.radio("Interest Rate", ["Market Average (4.99%)", "Manual Entry"])
        if interest_type == "Manual Entry":
            interest_rate = st.number_input("Annual Interest Rate (%)", value=5.0, step=0.1)
        else:
            interest_rate = 4.99

    loan_amount = vehicle_price - down_payment
    # Monthly interest rate
    r = (interest_rate / 100) / 12
    # Monthly payment formula (Amortization)
    if loan_amount > 0:
        monthly_payment = loan_amount * (r * (1 + r)**months) / ((1 + r)**months - 1)
    else:
        monthly_payment = 0

    with col2:
        st.metric("Monthly Payment", f"{monthly_payment:,.2f} €")
        st.write(f"**Total Loan Amount:** {loan_amount:,.2f} €")
        st.write(f"**Total Interest Paid:** {(monthly_payment * months) - loan_amount:,.2f} €")

# --- HOUSE MORTGAGE SECTION ---
elif app_mode == "🏠 House Mortgage":
    st.title("House Mortgage (Baufinanzierung)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Property Details")
        house_price = st.number_input("Purchase Price (€)", min_value=0, value=400000)
        own_capital = st.number_input("Own Capital (Eigenkapital) (€)", min_value=0, value=80000)
        
        st.subheader("Ancillary Costs (Nebenkosten)")
        notar_rate = st.slider("Notar & Grundbuch (%)", 1.0, 2.5, 2.0)
        makler_rate = st.number_input("Makler Fee (%)", value=3.57)
        tax_rate = st.selectbox("Grunderwerbsteuer (%)", [3.5, 5.0, 5.5, 6.0, 6.5], index=3)
        
        st.subheader("Financing Terms")
        interest_input = st.radio("Mortgage Interest", ["Market Estimate (3.8%)", "Manual Entry"])
        interest = st.number_input("Annual Interest (%)", value=3.8) if interest_input == "Manual Entry" else 3.8
        tilgung = st.number_input("Initial Repayment (Tilgung) (%)", value=2.0)

    # Calculations
    notar_cost = house_price * (notar_rate / 100)
    makler_cost = house_price * (makler_rate / 100)
    tax_cost = house_price * (tax_rate / 100)
    total_incidental = notar_cost + makler_cost + tax_cost
    
    total_cost = house_price + total_incidental
    loan_needed = total_cost - own_capital
    
    # German Annuity Formula: (Interest + Tilgung) * Loan / 12
    monthly_rate = (loan_needed * (interest + tilgung) / 100) / 12

    with col2:
        st.subheader("Calculation Summary")
        if loan_needed > 0:
            st.metric("Estimated Monthly Rate", f"{monthly_rate:,.2f} €")
        else:
            st.success("Your capital covers the whole cost!")

        st.write("---")
        st.write(f"**Purchase Price:** {house_price:,.2f} €")
        st.write(f"**Ancillary Costs:** {total_incidental:,.2f} €")
        st.write(f"**Total Required:** {total_cost:,.2f} €")
        st.write(f"**Loan Amount:** {max(0.0, loan_needed):,.2f} €")
        
        with st.expander("Breakdown of Fees"):
            st.write(f"Notary & Registry: {notar_cost:,.2f} €")
            st.write(f"Property Tax: {tax_cost:,.2f} €")
            st.write(f"Broker Fee: {makler_cost:,.2f} €")
