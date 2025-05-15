import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Investment Calculator",
    page_icon="💰",
    layout="wide"
)

st.title("Stock Market Investment Calculator")
st.markdown("Calculate potential returns based on your investment strategy.")

# Create tabs for investment and tax inputs
input_tab1, input_tab2 = st.tabs(["Investment Parameters", "Tax Settings"])

with input_tab1:
    # Create two columns for investment input form
    col1, col2 = st.columns(2)

with col1:
    # User inputs
    initial_investment = st.number_input(
        "Initial Investment Amount ($)",
        min_value=1.0,
        value=1000.0,
        step=100.0,
        format="%.2f"
    )
    
    percentage_gain = st.slider(
        "Target Percentage Gain per Trade (%)",
        min_value=0.1,
        max_value=10.0,
        value=2.0,
        step=0.1,
        format="%.1f"
    )

with col2:
    trading_days = st.slider(
        "Number of Trading Days per Month",
        min_value=1,
        max_value=22,  # Typical number of trading days in a month
        value=10,
        step=1
    )
    
    trades_per_day = st.slider(
        "Number of Trades per Day",
        min_value=1,
        max_value=10,
        value=1,
        step=1
    )
    
    reinvest = st.toggle("Reinvest Initial Investment Plus Gains Each Day", value=True)

    # Create a separator
    st.divider()

with input_tab2:
    # Tax settings
    st.subheader("Tax Settings")
    
    col_tax1, col_tax2 = st.columns(2)
    
    with col_tax1:
        # Tax rates
        federal_tax_rate = st.slider(
            "Federal Tax Rate (%)",
            min_value=0.0,
            max_value=50.0,
            value=22.0,
            step=0.5,
            format="%.1f"
        )
        
        state_tax_rate = st.slider(
            "State Tax Rate (%)",
            min_value=0.0,
            max_value=20.0,
            value=5.0,
            step=0.5,
            format="%.1f"
        )
    
    with col_tax2:
        # Deductions
        tax_deductions = st.number_input(
            "Total Tax Deductions ($)",
            min_value=0.0,
            value=0.0,
            step=100.0,
            format="%.2f",
            help="Enter total deductions like trading expenses, software subscriptions, home office, etc."
        )
        
        capital_gains = st.radio(
            "Tax Type",
            ["Short-term (Ordinary Income)", "Long-term Capital Gains"],
            index=0,
            help="Short-term gains (assets held <1 year) are taxed as ordinary income. Long-term gains (assets held >1 year) typically have lower tax rates."
        )
        
        if capital_gains == "Long-term Capital Gains":
            long_term_rate = st.slider(
                "Long-term Capital Gains Rate (%)",
                min_value=0.0,
                max_value=30.0,
                value=15.0,
                step=0.5,
                format="%.1f"
            )
    
    # Additional tax information
    with st.expander("Tax Information"):
        st.markdown("""
        ### Tax Considerations:
        - **Short-term capital gains** (assets held less than a year) are typically taxed as ordinary income
        - **Long-term capital gains** (assets held more than a year) are usually taxed at lower rates (0%, 15%, or 20% depending on income bracket)
        - **Deductions** may include trading expenses, software subscriptions, home office deductions, etc.
        - This calculator provides estimates only. Consult a tax professional for personalized advice.
        """)

# Calculate button
if st.button("Calculate Returns", type="primary", use_container_width=True):
    # Initialize data storage for results
    results_data = []
    current_amount = initial_investment
    
    # Perform calculations
    if reinvest:
        # Compound growth with reinvestment (reinvesting initial + gains each day)
        for day in range(1, trading_days + 1):
            daily_starting_amount = current_amount
            
            # Apply gains for each trade during the day
            for trade in range(trades_per_day):
                trade_gain = current_amount * (percentage_gain / 100)
                current_amount += trade_gain
            
            # Calculate total daily gain
            daily_gain = current_amount - daily_starting_amount
            
            # Store data for visualization
            results_data.append({
                "Day": day,
                "Amount": current_amount,
                "Daily Gain": daily_gain
            })
    else:
        # Without reinvestment (just accumulating profits)
        # Calculate gain per trade
        trade_gain = initial_investment * (percentage_gain / 100)
        
        # Calculate daily gain (trade gain × number of trades per day)
        daily_gain = trade_gain * trades_per_day
        
        for day in range(1, trading_days + 1):
            # Calculate amount (initial investment stays the same, gains accumulate)
            amount = initial_investment + (daily_gain * day)
            
            # Store data for visualization
            results_data.append({
                "Day": day,
                "Amount": amount,
                "Daily Gain": daily_gain
            })
    
    # Convert to DataFrame for easier manipulation
    results_df = pd.DataFrame(results_data)
    
    # Calculate summary statistics
    final_amount = results_df["Amount"].iloc[-1]
    total_profit = final_amount - initial_investment
    percentage_increase = (total_profit / initial_investment) * 100
    
    # Calculate taxes
    taxable_profit = max(0, total_profit - tax_deductions)
    
    if capital_gains == "Long-term Capital Gains":
        federal_tax = taxable_profit * (long_term_rate / 100)
    else:
        federal_tax = taxable_profit * (federal_tax_rate / 100)
        
    state_tax = taxable_profit * (state_tax_rate / 100)
    total_tax = federal_tax + state_tax
    net_profit = total_profit - total_tax
    
    # Display results
    results_col1, results_col2, results_col3, results_col4 = st.columns(4)
    
    with results_col1:
        st.metric("Initial Investment", f"${initial_investment:,.2f}")
    
    with results_col2:
        st.metric("Final Amount", f"${final_amount:,.2f}")
    
    with results_col3:
        st.metric("Total Profit", f"${total_profit:,.2f}")
    
    with results_col4:
        st.metric("Total Return", f"{percentage_increase:.2f}%")
    
    # Create visualization
    st.subheader("Growth Projection")
    
    # Create a tab-based interface for different views
    tab1, tab2 = st.tabs(["Chart", "Data Table"])
    
    with tab1:
        # Create a visually appealing chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=results_df["Day"],
            y=results_df["Amount"],
            mode='lines+markers',
            name='Portfolio Value',
            line=dict(color='green', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 255, 0, 0.1)'
        ))
        
        fig.update_layout(
            title="Portfolio Growth Over Trading Days",
            xaxis_title="Trading Day",
            yaxis_title="Amount ($)",
            height=500,
            hovermode="x unified"
        )
        
        fig.update_xaxes(tickmode='linear', dtick=1)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Display data table with formatted values
        display_df = results_df.copy()
        display_df["Amount"] = display_df["Amount"].map("${:,.2f}".format)
        display_df["Daily Gain"] = display_df["Daily Gain"].map("${:,.2f}".format)
        st.dataframe(display_df, use_container_width=True)
    
    # Tax breakdown
    st.subheader("Tax Breakdown")
    
    # Create columns for tax metrics
    tax_col1, tax_col2, tax_col3, tax_col4 = st.columns(4)
    
    with tax_col1:
        st.metric("Gross Profit", f"${total_profit:,.2f}")
    
    with tax_col2:
        st.metric("Taxable Profit", f"${taxable_profit:,.2f}")
        
    with tax_col3:
        st.metric("Total Tax", f"${total_tax:,.2f}")
        
    with tax_col4:
        st.metric("Net Profit", f"${net_profit:,.2f}")
    
    # Detailed tax breakdown
    with st.expander("Detailed Tax Breakdown"):
        tax_data = {
            "Category": ["Gross Profit", "Tax Deductions", "Taxable Profit", 
                        f"Federal Tax ({federal_tax_rate}%)" if capital_gains == "Short-term (Ordinary Income)" else f"Long-term Capital Gains Tax ({long_term_rate}%)", 
                        f"State Tax ({state_tax_rate}%)", "Total Tax", "Net Profit"],
            "Amount": [
                f"${total_profit:,.2f}",
                f"${tax_deductions:,.2f}",
                f"${taxable_profit:,.2f}",
                f"${federal_tax:,.2f}",
                f"${state_tax:,.2f}",
                f"${total_tax:,.2f}",
                f"${net_profit:,.2f}"
            ]
        }
        st.table(pd.DataFrame(tax_data))
    
    # Display investment strategy summary
    with st.expander("Investment Strategy Summary"):
        strategy_type = "Compounding (Reinvesting)" if reinvest else "Fixed Investment"
        st.markdown(f"""
        ### Strategy Details:
        - **Type**: {strategy_type}
        - **Initial Investment**: ${initial_investment:,.2f}
        - **Target Gain per Trade**: {percentage_gain}%
        - **Number of Trades per Day**: {trades_per_day}
        - **Trading Days per Month**: {trading_days}
        - **Total Trades per Month**: {trades_per_day * trading_days}
        
        With this strategy, you would turn **${initial_investment:,.2f}** into **${final_amount:,.2f}** in {trading_days} trading days,
        earning a gross profit of **${total_profit:,.2f}** ({percentage_increase:.2f}% return).
        
        After taxes and deductions, your net profit would be **${net_profit:,.2f}**.
        """)

# Add some helpful information at the bottom
with st.expander("How to Use This Calculator"):
    st.markdown("""
    1. Enter your initial investment amount
    2. Set your target percentage gain per trade
    3. Specify how many trading days per month you plan to trade
    4. Set the number of trades you expect to make per day
    5. Toggle whether you want to reinvest your gains each day
    6. Adjust tax settings and deductions in the Tax Settings tab
    7. Click "Calculate Returns" to see your potential returns
    
    **Note**: This calculator provides an estimate based on consistent returns.
    Actual market results may vary due to volatility, fees, taxes, and other factors.
    The tax calculations are estimates only and not a substitute for tax advice from a professional.
    """)
