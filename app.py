import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_fetcher import (DataFetcher, calculate_harvesting_potential, calculate_runoff_volume,
                         calculate_recharge_structure_size, calculate_cost_benefit, 
                         calculate_feasibility_score, calculate_detailed_cost_breakdown,
                         calculate_payback_analysis)
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Rainwater Harvesting Feasibility Analysis - Enhanced",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data fetcher
data_fetcher = DataFetcher()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feasibility-high {
        color: #4CAF50;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .feasibility-medium {
        color: #FF9800;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .feasibility-low {
        color: #F44336;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .card {
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        background: white;
    }
    .scheme-card {
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background: #f8fff8;
    }
    .cost-item {
        display: flex;
        justify-content: space-between;
        padding: 5px 0;
        border-bottom: 1px solid #eee;
    }
    .savings-highlight {
        background: #e8f5e8;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
    }
    .data-source {
        background: #e3f2fd;
        padding: 10px;
        border-radius: 5px;
        border-left: 3px solid #2196F3;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for user input
with st.sidebar:
    st.title("🏠 Rainwater Harvesting Input")
    
    # Location Details
    st.subheader("📍 Location Details")
    address = st.text_input("Enter your address in India:", "Chennai, Tamil Nadu")
    state_name = st.selectbox("Select State:", [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
        "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
        "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
        "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
        "Delhi", "Jammu and Kashmir", "Ladakh"
    ], index=22)  # Default to Tamil Nadu
    
    # System Configuration
    st.subheader("🏗️ System Configuration")
    roof_area = st.number_input("Roof Area (square meters):", min_value=10, max_value=1000, value=100)
    roof_type = st.selectbox("Roof Type:", ["Concrete", "Metal", "Tiled", "Thatched", "Asbestos", "Slate"])
    
    # Advanced Options
    with st.expander("⚙️ Advanced Options"):
        water_rate = st.slider("Water Cost (₹ per liter):", 0.01, 0.20, 0.05, 0.01)
        maintenance_rate = st.slider("Annual Maintenance (% of cost):", 1, 5, 2, 1) / 100
        system_efficiency = st.slider("System Efficiency (%):", 70, 95, 85, 5) / 100
    
    if st.button("🔍 Analyze Feasibility", type="primary"):
        with st.spinner("🔍 Fetching authentic data from government APIs..."):
            # Get latitude and longitude from address
            lat, lon = data_fetcher.get_lat_lon_from_address(address)
            
            if lat is None or lon is None:
                st.error("❌ Could not find the location. Please enter a valid Indian address.")
            else:
                # Fetch data from enhanced APIs
                rainfall_data = data_fetcher.get_rainfall_data(lat, lon, state_name)
                soil_data = data_fetcher.get_soil_type(lat, lon, state_name)
                groundwater_data = data_fetcher.get_groundwater_data(lat, lon)
                
                # Calculate runoff coefficient
                runoff_coeff = data_fetcher.calculate_runoff_coefficient(roof_type, soil_data["type"])
                
                # Get government schemes
                gov_schemes = data_fetcher.get_government_schemes(state_name)
                
                # Store data in session state
                st.session_state.update({
                    'lat': lat, 'lon': lon, 'rainfall_data': rainfall_data,
                    'soil_data': soil_data, 'groundwater_data': groundwater_data,
                    'roof_area': roof_area, 'roof_type': roof_type, 'runoff_coeff': runoff_coeff,
                    'water_rate': water_rate, 'maintenance_rate': maintenance_rate,
                    'system_efficiency': system_efficiency, 'state_name': state_name,
                    'gov_schemes': gov_schemes, 'address': address
                })
                
                st.success(f"✅ Data fetched successfully!")

# Main content
st.markdown('<h1 class="main-header">🌧️ Rainwater Harvesting Feasibility Analysis</h1>', unsafe_allow_html=True)

# Check if data is available
if 'rainfall_data' not in st.session_state:
    st.info("Please enter your address and roof details in the sidebar to get started.")
    
    # Display welcome information
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🎯 Enhanced Features:
        - **Authentic Government Data**: Real rainfall and soil data
        - **Detailed Cost Analysis**: Complete breakdown with subsidies
        - **Government Schemes**: Automatic eligibility checking
        """)
    
    with col2:
        st.markdown("""
        ### 📊 What You Get:
        - Live API integration with IMD and Soil Health data
        - 20-year financial projections
        - Government subsidy calculations
        """)
    
    with col3:
        st.markdown("""
        ### 🏆 Potential Benefits:
        - Save up to ₹50,000/year on water costs
        - Get up to 90% government subsidy
        - Contribute to groundwater conservation
        """)
    
    st.stop()

# Create enhanced tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🌧️ Rainfall Data", 
    "🏔️ Soil & Aquifer", 
    "💰 Cost Analysis", 
    "📈 Financial Projections",
    "🏛️ Government Schemes", 
    "📋 Complete Report"
])

# Tab 1: Enhanced Rainfall Analysis
with tab1:
    st.header("🌧️ Rainfall Analysis & Water Potential")
    
    # Data source information
    st.markdown(f'<div class="data-source">📡 <strong>Data Source:</strong> {st.session_state.rainfall_data["source"]}</div>', 
                unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📊 Monthly Rainfall Pattern")
        rainfall_df = pd.DataFrame.from_dict(
            st.session_state.rainfall_data["monthly"], 
            orient="index", 
            columns=["Rainfall (mm)"]
        )
        rainfall_df['Month'] = rainfall_df.index
        
        fig = px.bar(
            rainfall_df, 
            x='Month', 
            y="Rainfall (mm)",
            title="Monthly Rainfall Distribution",
            color="Rainfall (mm)",
            color_continuous_scale="Blues"
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Key rainfall metrics
        st.subheader("🌦️ Rainfall Characteristics")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Annual Rainfall", f"{st.session_state.rainfall_data['annual']:,} mm")
            st.metric("Wettest Month", f"{max(st.session_state.rainfall_data['monthly'], key=st.session_state.rainfall_data['monthly'].get)}")
        with col_m2:
            st.metric("Rainy Days/Year", f"{st.session_state.rainfall_data['rainy_days']} days")
            st.metric("Average Daily Rain", f"{st.session_state.rainfall_data['annual']/st.session_state.rainfall_data['rainy_days']:.1f} mm")
    
    with col2:
        st.subheader("💧 Water Harvesting Potential")
        
        # Calculate monthly harvesting potential
        monthly_potential = {}
        for month, rainfall in st.session_state.rainfall_data["monthly"].items():
            monthly_potential[month] = calculate_harvesting_potential(
                st.session_state.roof_area, 
                rainfall, 
                st.session_state.runoff_coeff,
                st.session_state.system_efficiency
            )
        
        annual_potential = sum(monthly_potential.values())
        
        # Key harvest metrics
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            st.metric("Annual Harvest", f"{annual_potential:,.0f} L")
            st.metric("Peak Month Harvest", f"{max(monthly_potential.values()):,.0f} L")
        with col_h2:
            st.metric("Daily Average", f"{annual_potential/365:.0f} L")
            st.metric("Per sq.m Harvest", f"{annual_potential/st.session_state.roof_area:.0f} L/m²")
        
        # Monthly harvest chart
        potential_df = pd.DataFrame.from_dict(
            monthly_potential, 
            orient="index", 
            columns=["Water (liters)"]
        )
        potential_df['Month'] = potential_df.index
        
        fig_line = px.line(
            potential_df, 
            x='Month', 
            y="Water (liters)",
            title="Monthly Water Harvest Potential",
            markers=True,
            line_shape="spline"
        )
        fig_line.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_line, use_container_width=True)
        
        # System efficiency display
        st.info(f"🔧 Runoff Coefficient: {st.session_state.runoff_coeff:.3f}")
        st.info(f"⚙️ System Efficiency: {st.session_state.system_efficiency*100:.0f}%")

# Tab 2: Enhanced Soil & Aquifer Analysis
with tab2:
    st.header("🏔️ Soil & Hydrogeological Analysis")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🌱 Soil Analysis")
        st.markdown(f'<div class="data-source">📡 <strong>Data Source:</strong> {st.session_state.soil_data["source"]}</div>', 
                    unsafe_allow_html=True)
        
        # Enhanced soil metrics
        soil_metrics_data = {
            'Property': ['Soil Type', 'Infiltration Rate', 'Suitability Score', 'pH Level', 'Organic Carbon'],
            'Value': [
                st.session_state.soil_data["type"],
                f"{st.session_state.soil_data['infiltration_rate']} mm/hr",
                f"{st.session_state.soil_data['suitability']}/10",
                f"{st.session_state.soil_data.get('ph', 'N/A')}",
                f"{st.session_state.soil_data.get('organic_carbon', 'N/A')}%"
            ]
        }
        
        soil_df = pd.DataFrame(soil_metrics_data)
        st.dataframe(soil_df, use_container_width=True, hide_index=True)
        
        # Soil suitability gauge
        suitability_score = st.session_state.soil_data['suitability']
        
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = suitability_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Soil Suitability Score"},
            gauge = {
                'axis': {'range': [None, 10]},
                'bar': {'color': "darkgreen" if suitability_score >= 7 else "orange" if suitability_score >= 4 else "red"},
                'steps': [
                    {'range': [0, 4], 'color': "lightgray"},
                    {'range': [4, 7], 'color': "lightyellow"},
                    {'range': [7, 10], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 8
                }
            }
        ))
        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)
        
    with col2:
        st.subheader("💧 Groundwater Analysis")
        st.markdown(f'<div class="data-source">📡 <strong>Data Source:</strong> {st.session_state.groundwater_data["source"]}</div>', 
                    unsafe_allow_html=True)
        
        # Enhanced groundwater metrics
        gw_metrics_data = {
            'Property': ['Water Table Depth', 'Water Quality', 'Natural Recharge Rate', 'Aquifer Type'],
            'Value': [
                f"{st.session_state.groundwater_data['depth']:.1f} meters",
                st.session_state.groundwater_data['quality'],
                f"{st.session_state.groundwater_data['recharge_rate']:.2f} mm/day",
                st.session_state.groundwater_data['aquifer_type']
            ]
        }
        
        gw_df = pd.DataFrame(gw_metrics_data)
        st.dataframe(gw_df, use_container_width=True, hide_index=True)
        
        # Water table depth assessment
        depth = st.session_state.groundwater_data['depth']
        if depth < 8:
            st.success("✅ Shallow water table - Excellent for recharge")
        elif depth < 20:
            st.warning("⚠️ Moderate depth - Good for recharge")
        else:
            st.error("❌ Deep water table - Requires careful design")
    
    # Infiltration Analysis
    st.subheader("📊 Infiltration vs Rainfall Analysis")
    
    avg_monthly_rainfall = st.session_state.rainfall_data["annual"] / 12
    soil_infiltration_monthly = st.session_state.soil_data["infiltration_rate"] * 24 * 30
    peak_rainfall = max(st.session_state.rainfall_data["monthly"].values())
    
    comparison_data = pd.DataFrame({
        'Parameter': ['Average Monthly Rainfall', 'Peak Monthly Rainfall', 'Soil Infiltration Capacity'],
        'Value (mm)': [avg_monthly_rainfall, peak_rainfall, soil_infiltration_monthly]
    })
    
    fig_comparison = px.bar(
        comparison_data, 
        x='Parameter', 
        y='Value (mm)',
        title="Rainfall vs Soil Infiltration Analysis",
        color='Value (mm)',
        color_continuous_scale='RdYlBu_r'
    )
    st.plotly_chart(fig_comparison, use_container_width=True)
    
    if soil_infiltration_monthly > peak_rainfall:
        st.success("✅ Soil can handle peak rainfall - Excellent infiltration capacity")
    elif soil_infiltration_monthly > avg_monthly_rainfall:
        st.warning("⚠️ Soil adequate for average rainfall - May need overflow management")
    else:
        st.error("❌ Limited soil infiltration - Surface storage strongly recommended")

# Tab 3: Detailed Cost Analysis
with tab3:
    st.header("💰 Detailed Cost Breakdown")
    
    # Calculate detailed costs
    cost_breakdown = calculate_detailed_cost_breakdown(
        st.session_state.roof_area, 
        st.session_state.soil_data["type"]
    )
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("🧾 Itemized Costs")
        
        # Create detailed cost table
        cost_items = []
        cost_categories = {
            "Collection System": ["gutters_downpipes", "first_flush_diverter", "leaf_screen", "collection_tank"],
            "Treatment System": ["sand_filter", "activated_carbon_filter", "uv_sterilizer"],
            "Recharge System": ["excavation", "gravel_sand", "pvc_pipes", "recharge_structure"],
            "Installation": ["labor", "electrical_work", "testing_commissioning", "permit_fees"]
        }
        
        item_names = {
            "gutters_downpipes": "Gutters & Downpipes",
            "first_flush_diverter": "First Flush Diverter",
            "leaf_screen": "Leaf Screens",
            "collection_tank": "Storage Tank",
            "sand_filter": "Sand Filter",
            "activated_carbon_filter": "Carbon Filter",
            "uv_sterilizer": "UV Sterilizer",
            "excavation": "Excavation Work",
            "gravel_sand": "Filter Media",
            "pvc_pipes": "Piping System",
            "recharge_structure": "Recharge Structure",
            "labor": "Labor Charges",
            "electrical_work": "Electrical Work",
            "testing_commissioning": "Testing & Setup",
            "permit_fees": "Permits & Approvals"
        }
        
        for category, items in cost_categories.items():
            category_total = 0
            for item in items:
                if item in cost_breakdown["itemwise_costs"]:
                    cost = cost_breakdown["itemwise_costs"][item]
                    cost_items.append({
                        'Category': category,
                        'Item': item_names.get(item, item.replace('_', ' ').title()),
                        'Cost (₹)': f"{cost:,.0f}"
                    })
                    category_total += cost
        
        # Add totals
        cost_items.append({'Category': 'SUBTOTAL', 'Item': '', 'Cost (₹)': f"{cost_breakdown['subtotal']:,.0f}"})
        cost_items.append({'Category': 'CONTINGENCY', 'Item': '10%', 'Cost (₹)': f"{cost_breakdown['contingency']:,.0f}"})
        cost_items.append({'Category': 'TOTAL', 'Item': '', 'Cost (₹)': f"{cost_breakdown['total_cost']:,.0f}"})
        
        cost_df = pd.DataFrame(cost_items)
        st.dataframe(cost_df, use_container_width=True, hide_index=True)
        
        # Key cost metrics
        st.subheader("💡 Cost Analysis")
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            st.metric("Total Project Cost", f"₹{cost_breakdown['total_cost']:,.0f}")
        with col_c2:
            st.metric("Cost per sq.m", f"₹{cost_breakdown['cost_per_sqm']:,.0f}")
        with col_c3:
            st.metric("Cost per Liter Capacity", f"₹{cost_breakdown['total_cost']/(st.session_state.roof_area*50):.1f}")
    
    with col2:
        st.subheader("📊 Cost Distribution")
        
        # Calculate category totals for pie chart
        category_totals = {}
        for category, items in cost_categories.items():
            total = sum(cost_breakdown["itemwise_costs"].get(item, 0) for item in items)
            category_totals[category] = total
        
        fig_pie = px.pie(
            values=list(category_totals.values()), 
            names=list(category_totals.keys()),
            title="Cost Distribution by System"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Cost vs Area Analysis
        st.subheader("📈 Economies of Scale")
        
        areas = [50, 100, 150, 200, 300, 500]
        costs = []
        cost_per_sqm = []
        
        for area in areas:
            temp_breakdown = calculate_detailed_cost_breakdown(area, st.session_state.soil_data["type"])
            costs.append(temp_breakdown["total_cost"])
            cost_per_sqm.append(temp_breakdown["cost_per_sqm"])
        
        scale_df = pd.DataFrame({
            'Roof Area (sq.m)': areas,
            'Total Cost (₹)': costs,
            'Cost per sq.m (₹)': cost_per_sqm
        })
        
        fig_scale = px.line(
            scale_df, 
            x='Roof Area (sq.m)', 
            y='Cost per sq.m (₹)',
            title="Cost Efficiency vs System Size",
            markers=True
        )
        st.plotly_chart(fig_scale, use_container_width=True)

# Tab 4: Enhanced Financial Projections
with tab4:
    st.header("📈 Comprehensive Financial Analysis")
    
    # Calculate financial metrics
    annual_harvest = calculate_harvesting_potential(
        st.session_state.roof_area, 
        st.session_state.rainfall_data["annual"], 
        st.session_state.runoff_coeff,
        st.session_state.system_efficiency
    )
    
    cost_breakdown = calculate_detailed_cost_breakdown(
        st.session_state.roof_area, 
        st.session_state.soil_data["type"]
    )
    
    payback_analysis = calculate_payback_analysis(
        cost_breakdown["total_cost"], 
        annual_harvest, 
        st.session_state.water_rate,
        st.session_state.maintenance_rate
    )
    
    # Key Financial Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Investment", f"₹{cost_breakdown['total_cost']:,.0f}")
        st.metric("Annual Harvest", f"{annual_harvest:,.0f} L")
    
    with col2:
        st.metric("Annual Savings", f"₹{payback_analysis['annual_water_savings']:,.0f}")
        st.metric("Annual Maintenance", f"₹{payback_analysis['annual_maintenance']:,.0f}")
    
    with col3:
        st.metric("Net Annual Benefit", f"₹{payback_analysis['net_annual_benefit']:,.0f}")
        roi = (payback_analysis['net_annual_benefit'] / cost_breakdown['total_cost']) * 100
        st.metric("Annual ROI", f"{roi:.1f}%")
    
    with col4:
        if payback_analysis['payback_period']:
            st.metric("Payback Period", f"{payback_analysis['payback_period']:.1f} years")
        else:
            st.metric("Payback Period", "N/A")
        st.metric("20-Year NPV", f"₹{payback_analysis['npv']:,.0f}")
    
    # 20-Year Financial Projection Chart
    st.subheader("📊 20-Year Financial Projection")
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Cumulative Cash Flow Analysis', 'Annual Cash Flow'),
        vertical_spacing=0.1
    )
    
    years = payback_analysis['years']
    cumulative_benefits = payback_analysis['cumulative_benefits']
    initial_investment = [cost_breakdown['total_cost']] * len(years)
    
    # Cumulative analysis
    fig.add_trace(
        go.Scatter(x=years, y=cumulative_benefits, name='Cumulative Benefits', 
                  line=dict(color='green', width=3)),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=years, y=initial_investment, name='Break-even Line', 
                  line=dict(color='red', dash='dash', width=2)),
        row=1, col=1
    )
    
    # Annual cash flow
    annual_net_benefits = [payback_analysis['net_annual_benefit']] * len(years)
    fig.add_trace(
        go.Bar(x=years, y=annual_net_benefits, name='Annual Net Benefit', 
               marker_color='lightblue', opacity=0.7),
        row=2, col=1
    )
    
    # Mark payback period
    if payback_analysis['payback_period'] and payback_analysis['payback_period'] <= 20:
        fig.add_vline(
            x=payback_analysis['payback_period'], 
            line_dash="dot", 
            line_color="orange",
            annotation_text=f"Payback: {payback_analysis['payback_period']:.1f} years",
            annotation_position="top"
        )
    
    fig.update_layout(height=600, showlegend=True)
    fig.update_xaxes(title_text="Years", row=2, col=1)
    fig.update_yaxes(title_text="Amount (₹)", row=1, col=1)
    fig.update_yaxes(title_text="Amount (₹)", row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Financial Assessment
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Investment Quality")
        
        if roi > 15:
            st.success(f"🌟 Excellent Investment: {roi:.1f}% annual return")
        elif roi > 8:
            st.warning(f"⚡ Good Investment: {roi:.1f}% annual return")
        else:
            st.info(f"💡 Moderate Investment: {roi:.1f}% annual return")
        
        # Investment comparison
        investment_comparison = pd.DataFrame({
            'Investment Type': ['Rainwater Harvesting', 'Fixed Deposit', 'Savings Account'],
            'Annual Return (%)': [roi, 6.5, 3.5],
            'Risk Level': ['Low', 'Very Low', 'Very Low']
        })
        
        st.dataframe(investment_comparison, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("🔍 Sensitivity Analysis")
        
        # Water rate sensitivity
        water_rates = np.linspace(0.02, 0.10, 5)
        payback_periods = []
        
        for rate in water_rates:
            temp_analysis = calculate_payback_analysis(
                cost_breakdown["total_cost"], 
                annual_harvest, 
                rate,
                st.session_state.maintenance_rate
            )
            payback_periods.append(temp_analysis['payback_period'] if temp_analysis['payback_period'] else 25)
        
        sensitivity_df = pd.DataFrame({
            'Water Rate (₹/L)': water_rates,
            'Payback Period (years)': payback_periods
        })
        
        fig_sensitivity = px.line(
            sensitivity_df,
            x='Water Rate (₹/L)',
            y='Payback Period (years)',
            title='Payback Sensitivity to Water Rates',
            markers=True
        )
        st.plotly_chart(fig_sensitivity, use_container_width=True)

# Tab 5: Government Schemes
with tab5:
    st.header("🏛️ Government Subsidies & Schemes")
    
    st.markdown(f"**Available schemes for {st.session_state.state_name}:**")
    
    # Calculate best available subsidy
    best_subsidy = 0
    best_scheme = None
    
    for scheme in st.session_state.gov_schemes:
        project_cost = cost_breakdown['total_cost']
        actual_subsidy = min(
            project_cost * (scheme['subsidy_percentage'] / 100),
            scheme['max_amount']
        )
        
        if actual_subsidy > best_subsidy:
            best_subsidy = actual_subsidy
            best_scheme = scheme
    
    # Display schemes
    for i, scheme in enumerate(st.session_state.gov_schemes):
        with st.container():
            st.markdown(f'<div class="scheme-card">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"### {scheme['name']}")
                st.write(scheme['description'])
            
            with col2:
                st.metric("Subsidy Rate", f"{scheme['subsidy_percentage']}%")
                st.metric("Max Amount", f"₹{scheme['max_amount']:,}")
            
            with col3:
                # Calculate actual subsidy for this project
                project_cost = cost_breakdown['total_cost']
                actual_subsidy = min(
                    project_cost * (scheme['subsidy_percentage'] / 100),
                    scheme['max_amount']
                )
                
                st.metric("Your Subsidy", f"₹{actual_subsidy:,.0f}")
                final_cost = project_cost - actual_subsidy
                st.metric("Net Cost", f"₹{final_cost:,.0f}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")
    
    # Best scheme recommendation
    if best_scheme:
        st.markdown('<div class="savings-highlight">', unsafe_allow_html=True)
        st.markdown(f"### 🎯 **Best Option: {best_scheme['name']}**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Original Cost", f"₹{cost_breakdown['total_cost']:,.0f}")
        
        with col2:
            st.metric("Subsidy", f"₹{best_subsidy:,.0f}")
        
        with col3:
            st.metric("Your Investment", f"₹{cost_breakdown['total_cost'] - best_subsidy:,.0f}")
        
        with col4:
            savings_percent = (best_subsidy / cost_breakdown['total_cost']) * 100
            st.metric("Savings", f"{savings_percent:.1f}%")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Impact of subsidy on financial returns
        subsidized_cost = cost_breakdown['total_cost'] - best_subsidy
        subsidized_payback = calculate_payback_analysis(
            subsidized_cost, 
            annual_harvest, 
            st.session_state.water_rate,
            st.session_state.maintenance_rate
        )
        
        st.subheader("📊 Financial Impact of Subsidies")
        
        # Before/after comparison
        comparison_data = pd.DataFrame({
            'Scenario': ['Without Subsidy', 'With Best Subsidy'],
            'Investment (₹)': [cost_breakdown['total_cost'], subsidized_cost],
            'Payback Period (years)': [
                payback_analysis['payback_period'] if payback_analysis['payback_period'] else 25, 
                subsidized_payback['payback_period'] if subsidized_payback['payback_period'] else 25
            ],
            'NPV 20-year (₹)': [payback_analysis['npv'], subsidized_payback['npv']]
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_investment = px.bar(
                comparison_data, 
                x='Scenario', 
                y='Investment (₹)',
                title='Investment Comparison',
                color='Investment (₹)',
                color_continuous_scale='RdYlGn_r'
            )
            st.plotly_chart(fig_investment, use_container_width=True)
        
        with col2:
            fig_payback = px.bar(
                comparison_data, 
                x='Scenario', 
                y='Payback Period (years)',
                title='Payback Period Comparison',
                color='Payback Period (years)',
                color_continuous_scale='RdYlGn_r'
            )
            st.plotly_chart(fig_payback, use_container_width=True)
    
    # Application process guidance
    st.subheader("📋 How to Apply")
    
    with st.expander("🚀 Complete Application Guide"):
        st.markdown("""
        ### Step 1: Document Preparation
        - Property documents (sale deed/lease)
        - Identity proof (Aadhar, PAN)
        - Address proof
        - Technical drawings and cost estimates
        
        ### Step 2: Technical Clearance
        - Soil percolation test report
        - Structural stability certificate
        - Local authority NOC
        
        ### Step 3: Online Application
        - Visit state water department portal
        - Fill application with required documents
        - Pay processing fee (₹500-₹2,000)
        
        ### Step 4: Site Inspection
        - Schedule inspection by officials
        - Ensure compliance with technical norms
        - Get approval certificate
        
        ### Step 5: Implementation
        - Use empaneled contractors (if mandatory)
        - Follow approved technical specifications
        - Maintain quality control
        
        ### Step 6: Subsidy Disbursement
        - Submit completion certificate
        - Provide bills and invoices
        - Receive subsidy (30-60 days)
        
        ### 📞 Important Contacts
        - **State Water Department**: Check your state portal
        - **District Collector**: For MGNREGA schemes  
        - **Agriculture Department**: For farm systems
        """)

# Tab 6: Complete Report
with tab6:
    st.header("📋 Comprehensive Feasibility Report")
    
    # Calculate final feasibility score
    feasibility_score = calculate_feasibility_score(
        st.session_state.soil_data["suitability"],
        st.session_state.rainfall_data["annual"],
        st.session_state.groundwater_data["depth"],
        st.session_state.roof_area,
        st.session_state.runoff_coeff
    )
    
    # Executive Summary
    st.subheader("🎯 Executive Summary")
    
    if feasibility_score >= 70:
        score_class = "feasibility-high"
        recommendation = "Highly Recommended"
        status_color = "#4CAF50"
    elif feasibility_score >= 50:
        score_class = "feasibility-medium"
        recommendation = "Recommended"
        status_color = "#FF9800"
    else:
        score_class = "feasibility-low"
        recommendation = "Requires Evaluation"
        status_color = "#F44336"
    
    # Enhanced feasibility display
    st.markdown(f'''
    <div style="background: linear-gradient(135deg, {status_color}22 0%, {status_color}11 100%); 
                border-left: 5px solid {status_color}; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <div style="text-align: center;">
            <h1 style="color: {status_color}; margin: 0;">Feasibility Score: {feasibility_score:.1f}/100</h1>
            <h2 style="color: {status_color}; margin: 10px 0;">Status: {recommendation}</h2>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Key findings
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Technical Summary")
        
        technical_data = {
            'Parameter': [
                'Location',
                'Annual Rainfall',
                'Rainy Days',
                'Soil Type',
                'Infiltration Rate', 
                'Water Table Depth',
                'Roof Area',
                'Annual Harvest Potential'
            ],
            'Value': [
                st.session_state.address,
                f"{st.session_state.rainfall_data['annual']:,} mm",
                f"{st.session_state.rainfall_data['rainy_days']} days",
                st.session_state.soil_data['type'],
                f"{st.session_state.soil_data['infiltration_rate']} mm/hr",
                f"{st.session_state.groundwater_data['depth']:.1f} m",
                f"{st.session_state.roof_area} sq.m",
                f"{annual_harvest:,.0f} liters"
            ]
        }
        
        tech_df = pd.DataFrame(technical_data)
        st.dataframe(tech_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("💰 Financial Summary")
        
        # Calculate payback period string with proper formatting
        payback_period_str = f"{payback_analysis['payback_period']:.1f} years" if payback_analysis['payback_period'] is not None else "N/A"
        
        financial_data = {
            'Parameter': [
                'Total Project Cost',
                'Best Available Subsidy',
                'Net Investment',
                'Annual Water Savings',
                'Annual Maintenance',
                'Net Annual Benefit',
                'Payback Period',
                '20-Year NPV'
            ],
            'Value': [
                f"₹{cost_breakdown['total_cost']:,}",
                f"₹{best_subsidy:,}",
                f"₹{cost_breakdown['total_cost'] - best_subsidy:,}",
                f"₹{payback_analysis['annual_water_savings']:,}",
                f"₹{payback_analysis['annual_maintenance']:,}",
                f"₹{payback_analysis['net_annual_benefit']:,}",
                payback_period_str,
                f"₹{payback_analysis['npv']:,}"
            ]
        }
        
        fin_df = pd.DataFrame(financial_data)
        st.dataframe(fin_df, use_container_width=True, hide_index=True)
    
    # Detailed recommendations
    st.subheader("🎯 Implementation Recommendations")
    
    if feasibility_score >= 70:
        st.success("✅ **PROCEED WITH IMPLEMENTATION**")
        st.markdown(f"""
        Your location shows excellent potential for rainwater harvesting:
        
        **Immediate Actions:**
        1. Apply for **{best_scheme['name'] if best_scheme else 'available subsidies'}** - potential savings of ₹{best_subsidy:,}
        2. Engage certified contractors from empaneled list
        3. Obtain building permissions and technical clearances
        
        **Expected Benefits:**
        - Annual water harvest: **{annual_harvest:,} liters**
        - Annual cost savings: **₹{payback_analysis['annual_water_savings']:,}**
        - Payback period: **{payback_period_str}**
        - Water self-sufficiency: **{min(100, (annual_harvest/(150*365*4))*100):.0f}%** for family of 4
        """)
        
    elif feasibility_score >= 50:
        st.warning("⚡ **RECOMMENDED WITH MODIFICATIONS**")
        st.markdown("""
        Your location has good potential with some considerations:
        
        **Recommended Modifications:**
        - Install larger storage capacity for seasonal variations
        - Consider soil improvement measures for better infiltration
        - Implement phased installation approach
        
        **Risk Mitigation:**
        - Regular maintenance schedule
        - Backup water source planning
        - Quality monitoring system
        """)
        
    else:
        st.error("🔍 **DETAILED EVALUATION REQUIRED**")
        st.markdown("""
        Your location may face challenges requiring careful assessment:
        
        **Before Implementation:**
        - Conduct detailed geological survey
        - Consult with local water management experts
        - Consider alternative water conservation methods
        
        **Potential Solutions:**
        - Community-scale implementation
        - Hybrid systems with groundwater recharge focus
        - Advanced soil treatment techniques
        """)
    
    # Implementation checklist
    st.subheader("✅ Implementation Checklist")
    
    checklist = [
        "Obtain building/construction permissions",
        "Apply for government subsidies and approvals", 
        "Select certified contractor from empaneled list",
        "Finalize technical drawings and specifications",
        "Conduct soil percolation test",
        "Arrange financing and insurance",
        "Schedule construction timeline",
        "Install monitoring and control systems",
        "Complete system testing and commissioning",
        "Set up maintenance and monitoring schedule"
    ]
    
    # Create interactive checklist
    for i, item in enumerate(checklist):
        st.checkbox(item, key=f"checklist_{i}")
    
    # Generate downloadable report
    st.subheader("📄 Download Report")
    
    # Create comprehensive report data
    report_summary = {
        "Project Details": {
            "Location": st.session_state.address,
            "State": st.session_state.state_name,
            "Analysis Date": pd.Timestamp.now().strftime('%Y-%m-%d'),
            "Roof Area": f"{st.session_state.roof_area} sq.m",
            "Roof Type": st.session_state.roof_type
        },
        "Technical Assessment": {
            "Feasibility Score": f"{feasibility_score:.1f}/100",
            "Recommendation": recommendation,
            "Annual Rainfall": f"{st.session_state.rainfall_data['annual']} mm",
            "Soil Type": st.session_state.soil_data['type'],
            "Water Table Depth": f"{st.session_state.groundwater_data['depth']:.1f} m",
            "Annual Harvest Potential": f"{annual_harvest:,} liters"
        },
        "Financial Analysis": {
            "Total Project Cost": f"₹{cost_breakdown['total_cost']:,}",
            "Available Subsidy": f"₹{best_subsidy:,}",
            "Net Investment": f"₹{cost_breakdown['total_cost'] - best_subsidy:,}",
            "Annual Savings": f"₹{payback_analysis['annual_water_savings']:,}",
            "Payback Period": payback_period_str,
            "20-Year NPV": f"₹{payback_analysis['npv']:,}"
        }
    }
    
    # Create downloadable CSV
    all_data = {}
    for category, data in report_summary.items():
        for key, value in data.items():
            all_data[f"{category} - {key}"] = value
    
    report_df = pd.DataFrame.from_dict(all_data, orient='index', columns=['Value'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📊 Download Summary (CSV)",
            data=report_df.to_csv(),
            file_name=f"rainwater_harvesting_report_{st.session_state.address.replace(' ', '_')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Generate detailed text report
        detailed_report = f"""
RAINWATER HARVESTING FEASIBILITY ANALYSIS
==========================================

EXECUTIVE SUMMARY
Project Location: {st.session_state.address}
Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
Feasibility Score: {feasibility_score:.1f}/100
Recommendation: {recommendation}

TECHNICAL ASSESSMENT
- Annual Rainfall: {st.session_state.rainfall_data['annual']:,} mm ({st.session_state.rainfall_data['rainy_days']} rainy days)
- Soil Type: {st.session_state.soil_data['type']} (Infiltration: {st.session_state.soil_data['infiltration_rate']} mm/hr)
- Water Table: {st.session_state.groundwater_data['depth']:.1f} meters ({st.session_state.groundwater_data['quality']} quality)
- Roof Configuration: {st.session_state.roof_area} sq.m {st.session_state.roof_type} roof
- System Efficiency: {st.session_state.system_efficiency*100:.0f}%

HARVEST POTENTIAL
- Annual Water Harvest: {annual_harvest:,} liters
- Daily Average: {annual_harvest/365:.0f} liters
- Peak Month Harvest: {max(monthly_potential.values()):,.0f} liters
- Water Self-Sufficiency: {min(100, (annual_harvest/(150*365*4))*100):.0f}% (family of 4)

FINANCIAL ANALYSIS
- Total Project Cost: ₹{cost_breakdown['total_cost']:,}
- Government Subsidy: ₹{best_subsidy:,} ({(best_subsidy/cost_breakdown['total_cost']*100):.1f}%)
- Net Investment: ₹{cost_breakdown['total_cost'] - best_subsidy:,}
- Annual Water Savings: ₹{payback_analysis['annual_water_savings']:,}
- Annual Maintenance: ₹{payback_analysis['annual_maintenance']:,}
- Net Annual Benefit: ₹{payback_analysis['net_annual_benefit']:,}
- Payback Period: {payback_period_str}
- 20-Year NPV: ₹{payback_analysis['npv']:,}
- Annual ROI: {(payback_analysis['net_annual_benefit']/cost_breakdown['total_cost']*100):.1f}%

GOVERNMENT SCHEMES AVAILABLE
- Best Option: {best_scheme['name'] if best_scheme else 'Not Available'}
- Subsidy Rate: {best_scheme['subsidy_percentage'] if best_scheme else 0}%
- Maximum Amount: ₹{best_scheme['max_amount'] if best_scheme else 0:,}

ENVIRONMENTAL IMPACT
- Annual Water Conservation: {annual_harvest:,} liters
- Equivalent Population Served: {annual_harvest/365/100:.0f} people
- Reduced Municipal Water Demand: {annual_harvest/1000:.1f} cubic meters
- Groundwater Recharge Contribution: Significant

RECOMMENDATION SUMMARY
{recommendation.upper()}: This analysis indicates {"excellent" if feasibility_score >= 70 else "good" if feasibility_score >= 50 else "challenging"} feasibility for rainwater harvesting at your location.

Generated using authentic Indian government data sources.
For implementation, consult certified rainwater harvesting professionals.

Report End
==========================================
        """
        
        st.download_button(
            label="📄 Download Detailed Report (TXT)",
            data=detailed_report,
            file_name=f"detailed_rainwater_report_{st.session_state.address.replace(' ', '_')}.txt",
            mime="text/plain"
        )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px; background: #f8f9fa; border-radius: 10px; margin-top: 30px;">
    <h4 style="color: #1E88E5; margin-bottom: 15px;">Smart Rainwater Harvesting Analyzer</h4>
    <p><strong>Powered by Authentic Government Data Sources:</strong></p>
    <p>Indian Meteorological Department (IMD) • Soil Health Card Database • Central Ground Water Board</p>
    <p style="margin-top: 15px; font-style: italic;">This comprehensive analysis provides a scientific foundation for your rainwater harvesting project decision.</p>
    <p><strong>Next Steps:</strong> Consult with certified professionals for detailed site assessment and implementation planning.</p>
</div>
""", unsafe_allow_html=True)
