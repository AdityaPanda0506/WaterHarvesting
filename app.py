import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import functions from the enhanced system
from rainwater_utils import (
    get_location, get_soil_type, fetch_historical_rainfall_data, 
    fetch_weather_forecast_data, fetch_imd_monsoon_forecast,
    calculate_water_metrics, assess_feasibility, 
    calculate_recharge_structures_enhanced, create_comprehensive_charts,
    generate_comprehensive_report, analyze_rainwater_harvesting,
    create_comprehensive_financial_chart, INDIAN_WATER_COSTS
)

# --------------------------
# Page Configuration
# --------------------------
st.set_page_config(
    page_title="💧 Rainwater Harvesting Pro - India Edition", 
    page_icon="💧", 
    layout="wide"
)

# Custom CSS for Indian theme
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .success-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .warning-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------
# Title and Header
# --------------------------
st.title("💧 Professional Rainwater Harvesting Feasibility Assessment - India Edition")
st.markdown("**Comprehensive analysis with future predictions, cost-benefit evaluation in ₹, and authentic Indian data**")

# Add Indian flag and regional focus
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("🇮🇳 **Designed for Indian Climate & Conditions** 🇮🇳")

# --------------------------
# Address Input Section
# --------------------------
st.header("📍 Location & Property Details")

col1, col2 = st.columns([3, 1])

with col1:
    address = st.text_input(
        "📍 Enter your address in India (e.g., 'Mumbai, Maharashtra' or 'Bengaluru, Karnataka')", 
        placeholder="Enter city, state, India"
    )

with col2:
    water_source = st.selectbox(
        "💧 Primary Water Source",
        options=list(INDIAN_WATER_COSTS.keys()),
        index=0,
        format_func=lambda x: {
            "municipal": "Municipal Supply (₹15/m³)",
            "tanker": "Water Tanker (₹45/m³)", 
            "borewell": "Borewell (₹8/m³)"
        }[x],
        help="Select your current water source for cost comparison"
    )

if not address:
    st.info("👆 Please enter your address in India to begin the comprehensive analysis.")
    st.stop()

# --------------------------
# Location Processing
# --------------------------
with st.spinner("📍 Locating address in India..."):
    location = get_location(address)

if not location:
    st.error("❌ Could not find this address. Please check and try again.")
    st.stop()

lat, lon = location.latitude, location.longitude

# Verify location is in India
if not (6 <= lat <= 37 and 68 <= lon <= 97):
    st.warning("⚠️ This address appears to be outside India. This system is optimized for Indian conditions.")

st.success(f"✅ Located: {location.address}")
st.info(f"**Coordinates**: {lat:.4f}°N, {lon:.4f}°E")

# --------------------------
# Property Details Input
# --------------------------
st.subheader("🏠 Property & Household Information")

col1, col2, col3, col4 = st.columns(4)

with col1:
    roof_area = st.number_input(
        "🏠 Roof Area (m²)",
        min_value=10.0,
        value=150.0,
        step=5.0,
        help="Total roof area available for rainwater collection"
    )

with col2:
    household_size = st.number_input(
        "👥 Household Size",
        min_value=1,
        value=4,
        step=1,
        help="Number of people in the household"
    )

with col3:
    garden_area = st.number_input(
        "🌱 Garden/Terrace Area (m²)",
        min_value=0.0,
        value=50.0,
        step=5.0,
        help="Area requiring irrigation (gardens, terrace farming)"
    )

with col4:
    analysis_type = st.selectbox(
        "📊 Analysis Type",
        ["Quick Analysis", "Comprehensive Analysis"],
        help="Quick: Basic calculations, Comprehensive: Full report with predictions"
    )

# --------------------------
# Soil Analysis Section
# --------------------------
st.subheader("🌍 Automated Soil Analysis")

with st.spinner("🌱 Detecting soil type from coordinates..."):
    soil_data = get_soil_type(lat, lon)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🌱 Detected Soil Type", soil_data['type'])
with col2:
    st.metric("📡 Data Source", soil_data['source'])
with col3:
    confidence_colors = {"High": "🟢", "Medium": "🟡", "Low": "🟠", "Very Low": "🔴"}
    st.metric("🎯 Confidence Level", f"{confidence_colors.get(soil_data['confidence'], '⚪')} {soil_data['confidence']}")
with col4:
    if 'raw_classification' in soil_data:
        st.metric("📋 Classification", soil_data['raw_classification'][:20] + "...")

# Manual override option
with st.expander("🔧 Manual Soil Type Override (Optional)"):
    manual_override = st.checkbox("Override automatic detection")
    if manual_override:
        soil_type = st.selectbox(
            "Select Soil Type",
            options=["Sandy", "Sandy Loam", "Loam", "Clay Loam", "Clay", "Silt"],
            help="Choose based on local soil testing or knowledge"
        )
        st.info("💡 Consider getting professional soil testing for accurate results")
    else:
        soil_type = soil_data['type']

# --------------------------
# Data Fetching and Analysis
# --------------------------
st.header("📊 Analysis Results")

# Progress tracking
progress_bar = st.progress(0)
status_text = st.empty()

try:
    # Step 1: Historical rainfall data
    status_text.text("🌧️ Fetching historical rainfall data (2019-2023)...")
    progress_bar.progress(20)
    
    historical_df, yearly_data = fetch_historical_rainfall_data(lat, lon)
    if historical_df is None:
        st.error("❌ Could not fetch rainfall data. Please try again later.")
        st.stop()
    
    # Step 2: Future predictions (only for comprehensive analysis)
    forecast_df = None
    monsoon_forecast = None
    
    if analysis_type == "Comprehensive Analysis":
        status_text.text("🔮 Generating weather forecasts and predictions...")
        progress_bar.progress(40)
        
        forecast_df = fetch_weather_forecast_data(lat, lon)
        monsoon_forecast = fetch_imd_monsoon_forecast(lat, lon)
    
    # Step 3: Calculate water metrics
    status_text.text("💧 Calculating water metrics and financial analysis...")
    progress_bar.progress(60)
    
    results = calculate_water_metrics(
        historical_df, forecast_df, roof_area, household_size, garden_area, water_source
    )
    
    # Step 4: Enhanced recharge structures
    status_text.text("🏗️ Designing groundwater recharge structures...")
    progress_bar.progress(80)
    
    recharge_data = calculate_recharge_structures_enhanced(
        results['annual_harvest_historical'], soil_type
    )
    
    # Step 5: Create visualizations
    if analysis_type == "Comprehensive Analysis":
        status_text.text("📈 Creating comprehensive visualizations...")
        progress_bar.progress(90)
        
        comprehensive_chart = create_comprehensive_charts(historical_df, forecast_df, results)
    
    progress_bar.progress(100)
    status_text.text("✅ Analysis completed successfully!")
    
except Exception as e:
    st.error(f"❌ Analysis failed: {str(e)}")
    st.stop()

# --------------------------
# Executive Dashboard
# --------------------------
st.subheader("📊 Executive Dashboard")

# Key Performance Indicators
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "🌧️ Annual Rainfall", 
        f"{results['annual_rainfall_historical']:.0f} mm",
        delta=f"+{results.get('annual_rainfall_future', 0) - results['annual_rainfall_historical']:.0f} mm (predicted)" if forecast_df is not None else None
    )

with col2:
    st.metric(
        "💧 Water Harvest", 
        f"{results['annual_harvest_historical']:.1f} m³/year",
        delta=f"+{results.get('annual_harvest_future', 0) - results['annual_harvest_historical']:.1f} m³" if forecast_df is not None else None
    )

with col3:
    coverage = results['historical_coverage']
    st.metric("📈 Demand Coverage", f"{coverage:.1f}%")
    if coverage >= 50:
        st.success("✅ High coverage")
    elif coverage >= 25:
        st.info("ℹ️ Moderate coverage") 
    else:
        st.warning("⚠️ Limited coverage")

with col4:
    total_investment = results['cost_data']['total_initial']
    st.metric("💰 Total Investment", f"₹{total_investment:,.0f}")
    
    # Investment per m³ of harvest
    cost_per_m3 = total_investment / results['annual_harvest_historical'] if results['annual_harvest_historical'] > 0 else 0
    st.caption(f"₹{cost_per_m3:,.0f} per m³/year")

with col5:
    annual_savings = results['annual_savings_future'] if forecast_df is not None and not forecast_df.empty else results['annual_savings_historical']
    st.metric("💵 Annual Savings", f"₹{annual_savings:,.0f}")
    
    payback = results['financial_metrics']['payback_period']
    if payback:
        st.caption(f"Payback: {payback:.1f} years")
    else:
        st.caption("No payback period")

# Overall Feasibility Assessment
feasibility_score = assess_feasibility(results)
st.subheader(f"🎯 Overall Feasibility Score: {feasibility_score:.0f}/100")

# Custom progress bar with color coding
if feasibility_score >= 80:
    progress_color = "#28a745"  # Green
    recommendation = "🎉 **HIGHLY RECOMMENDED** - Excellent investment opportunity!"
    st.success(recommendation)
elif feasibility_score >= 60:
    progress_color = "#17a2b8"  # Blue  
    recommendation = "💧 **RECOMMENDED** - Good potential for rainwater harvesting"
    st.success(recommendation)
elif feasibility_score >= 40:
    progress_color = "#ffc107"  # Yellow
    recommendation = "🤔 **MODERATE** - Consider with careful evaluation"
    st.warning(recommendation)
else:
    progress_color = "#dc3545"  # Red
    recommendation = "⚠️ **LIMITED BENEFIT** - May not be cost-effective"
    st.error(recommendation)

# Custom progress bar
st.markdown(f"""
<div style="background-color: #f0f0f0; border-radius: 10px; padding: 3px;">
    <div style="background-color: {progress_color}; width: {feasibility_score}%; height: 20px; border-radius: 8px; text-align: center; color: white; font-weight: bold;">
        {feasibility_score:.0f}%
    </div>
</div>
""", unsafe_allow_html=True)

# --------------------------
# Detailed Analysis Tabs
# --------------------------
st.header("📈 Detailed Analysis")

if analysis_type == "Comprehensive Analysis":
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🌧️ Rainfall Analysis", "💰 Financial Analysis", "🌊 Recharge Structures", 
        "🌍 Environmental Impact", "📋 Implementation Plan", "📊 Comprehensive Report"
    ])
else:
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌧️ Rainfall Analysis", "💰 Financial Analysis", 
        "🌊 Recharge Structures", "🌍 Environmental Impact"
    ])

# Tab 1: Rainfall Analysis
with tab1:
    if analysis_type == "Comprehensive Analysis" and forecast_df is not None:
        st.pyplot(comprehensive_chart, use_container_width=True)
        
        # Monsoon forecast details
        if monsoon_forecast:
            st.subheader("🌦️ Monsoon Forecast (IMD Style)")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Seasonal Rainfall", f"{monsoon_forecast['seasonal_rainfall_percent']:.0f}% of normal")
                st.metric("Monsoon Onset", monsoon_forecast['monsoon_onset_date'])
                
            with col2:
                st.metric("Heavy Rainfall Days", f"{monsoon_forecast['heavy_rainfall_days']} days")
                st.metric("Monsoon Withdrawal", monsoon_forecast['monsoon_withdrawal_date'])
                
            with col3:
                drought_risk = monsoon_forecast['drought_risk']
                flood_risk = monsoon_forecast['flood_risk']
                
                if drought_risk == 'Low':
                    st.success(f"🌵 Drought Risk: {drought_risk}")
                else:
                    st.warning(f"🌵 Drought Risk: {drought_risk}")
                    
                if flood_risk == 'Low':
                    st.success(f"🌊 Flood Risk: {flood_risk}")
                else:
                    st.warning(f"🌊 Flood Risk: {flood_risk}")
    
    else:
        # Basic rainfall chart for quick analysis
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Monthly rainfall
        ax1.bar(historical_df["Month"], historical_df["Historical_Rainfall_mm"], 
                color="skyblue", edgecolor="navy", alpha=0.7)
        ax1.axhline(y=30, color="red", linestyle="--", label="Dry Threshold (30mm)")
        ax1.set_title("Monthly Rainfall Distribution")
        ax1.set_ylabel("Rainfall (mm)")
        ax1.tick_params(axis='x', rotation=45)
        ax1.legend()
        ax1.grid(axis="y", alpha=0.3)
        
        # Water balance
        monthly_demand = results['total_demand'] / 12
        ax2.bar(range(len(historical_df)), historical_df["Harvested_m3"], 
                label='Harvested Supply', color='lightblue')
        ax2.axhline(y=monthly_demand, color="red", linestyle="-", 
                    label=f"Monthly Demand ({monthly_demand:.1f} m³)")
        ax2.set_title("Monthly Water Supply vs Demand")
        ax2.set_ylabel("Water (m³)")
        ax2.set_xticks(range(len(historical_df)))
        ax2.set_xticklabels([m[:3] for m in historical_df["Month"]], rotation=45)
        ax2.legend()
        ax2.grid(axis="y", alpha=0.3)
        
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
    
    # Water demand breakdown
    st.subheader("💧 Water Demand Analysis")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🚰 Drinking Water", f"{results['drinking_demand']:.1f} m³/year")
    with col2:
        st.metric("🏠 Domestic Use", f"{results['domestic_demand']:.1f} m³/year")
    with col3:
        st.metric("🌱 Garden Irrigation", f"{results['garden_demand']:.1f} m³/year")
    with col4:
        st.metric("📊 Total Demand", f"{results['total_demand']:.1f} m³/year")

# Tab 2: Financial Analysis
with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Investment Breakdown")
        
        # System recommendation
        st.info(f"**Recommended System**: {results['system_type'].title()}")
        st.info(f"**Storage Capacity**: {results['recommended_storage']:.1f} m³")
        
        # Cost breakdown
        st.write("**Initial Costs:**")
        costs = results['cost_data']['initial_costs']
        for component, cost in costs.items():
            if cost > 0:
                st.write(f"• {component.replace('_', ' ').title()}: ₹{cost:,.0f}")
        
        st.markdown(f"**Total Initial Investment: ₹{results['cost_data']['total_initial']:,.0f}**")
        
        st.write("**Annual Operating Costs:**")
        annual_costs = results['cost_data']['annual_costs']
        for component, cost in annual_costs.items():
            if cost > 0:
                st.write(f"• {component.replace('_', ' ').title()}: ₹{cost:,.0f}")
        
        st.markdown(f"**Total Annual Cost: ₹{results['cost_data']['total_annual']:,.0f}**")
    
    with col2:
        st.subheader("📈 Financial Returns")
        
        # Key financial metrics
        fm = results['financial_metrics']
        
        col2_1, col2_2 = st.columns(2)
        with col2_1:
            st.metric("NPV (20 years)", f"₹{fm['npv']:,.0f}")
            st.metric("IRR", f"{fm['irr']*100:.1f}% p.a.")
            
        with col2_2:
            if fm['payback_period']:
                st.metric("Payback Period", f"{fm['payback_period']:.1f} years")
            else:
                st.metric("Payback Period", "No payback")
                
            st.metric("Benefit-Cost Ratio", f"{fm['benefit_cost_ratio']:.2f}")
        
        # Financial viability assessment
        if fm['npv'] > 0 and fm['benefit_cost_ratio'] > 1.0:
            st.success("✅ **Financially Viable**: Positive returns expected")
        elif fm['benefit_cost_ratio'] > 0.8:
            st.warning("⚠️ **Marginal Viability**: Consider optimizations")
        else:
            st.error("❌ **Not Financially Viable**: Returns below investment")
    
    # 20-year projection with enhanced visualization
    st.subheader("📊 Enhanced 20-Year Financial Analysis")
    
    # Create enhanced financial chart
    enhanced_financial_chart = create_comprehensive_financial_chart(results['financial_metrics'], results)
    st.pyplot(enhanced_financial_chart, use_container_width=True)
    
    # Additional financial insights
    st.subheader("💡 Financial Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_benefits = results['financial_metrics']['total_benefits_pv']
        total_costs = results['financial_metrics']['total_costs_pv']
        st.metric("Total Benefits (PV)", f"₹{total_benefits:,.0f}")
        st.metric("Total Costs (PV)", f"₹{total_costs:,.0f}")
        
    with col2:
        roi_percentage = ((total_benefits - total_costs) / total_costs) * 100 if total_costs > 0 else 0
        st.metric("Return on Investment", f"{roi_percentage:.1f}%")
        
        break_even_year = results['financial_metrics']['payback_period']
        if break_even_year:
            st.metric("Break-even Point", f"Year {break_even_year}")
        else:
            st.metric("Break-even Point", "Not achieved")
            
    with col3:
        # Calculate monthly cash flow in final year
        if results['financial_metrics']['yearly_analysis']:
            final_year_net = results['financial_metrics']['yearly_analysis'][-1]['net_annual']
            monthly_cash_flow = final_year_net / 12
            st.metric("Final Year Monthly Cash Flow", f"₹{monthly_cash_flow:,.0f}")
        
        # Risk assessment
        if results['financial_metrics']['benefit_cost_ratio'] > 1.3:
            st.success("Low Risk Investment")
        elif results['financial_metrics']['benefit_cost_ratio'] > 1.0:
            st.info("Moderate Risk Investment")
        else:
            st.warning("High Risk Investment")
    
    # Detailed benefit breakdown table
    st.subheader("🎯 Detailed Annual Benefits Breakdown")
    
    from rainwater_utils import (
        calculate_avoided_tanker_costs, calculate_gardening_benefits,
        calculate_property_value_benefit, calculate_infrastructure_savings
    )
    
    annual_water_savings = results.get('annual_savings_future', results.get('annual_savings_historical', 0))
    
    benefits_data = {
        'Benefit Category': [
            'Direct Water Bill Savings',
            'Sewage/Drainage Charge Savings', 
            'Avoided Water Tanker Costs',
            'Home Gardening Benefits',
            'Property Value Appreciation',
            'Community Infrastructure Savings'
        ],
        'Annual Amount (₹)': [
            annual_water_savings,
            annual_water_savings * 0.7,
            calculate_avoided_tanker_costs(annual_water_savings, 'medium'),
            calculate_gardening_benefits(annual_water_savings, household_size),
            calculate_property_value_benefit(roof_area, 'medium'),
            calculate_infrastructure_savings('urban', roof_area)
        ],
        'Description': [
            'Direct reduction in municipal water bills',
            'Reduced sewage charges due to lower consumption',
            'Avoided emergency tanker purchases during shortages',
            'Value of homegrown vegetables and herbs',
            'Annual benefit from increased property value',
            'Community savings from reduced stormwater load'
        ]
    }
    
    benefits_df = pd.DataFrame(benefits_data)
    benefits_df['20-Year Total (₹)'] = benefits_df['Annual Amount (₹)'] * 20
    
    st.dataframe(
        benefits_df.style.format({
            'Annual Amount (₹)': '₹{:,.0f}',
            '20-Year Total (₹)': '₹{:,.0f}'
        }).background_gradient(subset=['Annual Amount (₹)'], cmap='Greens'),
        use_container_width=True
    )
    
    total_annual_benefits = benefits_df['Annual Amount (₹)'].sum()
    st.success(f"💰 **Total Annual Benefits**: ₹{total_annual_benefits:,.0f}")
    st.info(f"📈 **20-Year Benefit Total**: ₹{total_annual_benefits * 20:,.0f}")
    
    # Sensitivity analysis
    st.subheader("📊 Sensitivity Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Impact of Water Cost Changes**")
        water_cost_scenarios = {
            'Conservative (+5%/year)': 0.05,
            'Expected (+8%/year)': 0.08,
            'High inflation (+12%/year)': 0.12
        }
        
        for scenario, rate in water_cost_scenarios.items():
            # Recalculate NPV for different scenarios
            future_value = annual_water_savings * (1 + rate) ** 10  # 10-year projection
            st.write(f"• {scenario}: ₹{future_value:,.0f} (Year 10)")
            
    with col2:
        st.write("**Risk Factors**")
        risk_factors = [
            f"Rainfall variation: ±{results['dry_months_historical']/12*100:.0f}%",
            f"System maintenance: ₹{results['cost_data']['total_annual']:,.0f}/year",
            "Technology obsolescence: Low risk",
            "Regulatory changes: Medium risk"
        ]
        
        for risk in risk_factors:
            st.write(f"• {risk}")

# Tab 3: Recharge Structures
with tab3:
    st.subheader("🌊 Groundwater Recharge Analysis")
    
    # Soil suitability overview
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🌱 Soil Type", soil_type)
    with col2:
        st.metric("💧 Infiltration Rate", f"{recharge_data['soil_infiltration_rate']} mm/hr")
    with col3:
        suitability = recharge_data['soil_suitability']
        if suitability == "High":
            st.success(f"✅ {suitability} Suitability")
        elif suitability == "Medium":
            st.info(f"ℹ️ {suitability} Suitability")
        else:
            st.warning(f"⚠️ {suitability} Suitability")
    with col4:
        st.metric("🔄 Annual Recharge", f"{recharge_data['annual_recharge_potential']:.1f} m³")
    
    st.info(f"**💡 Recommended Structure**: {recharge_data['recommended_structure'].replace('_', ' ').title()}")
    st.caption(f"**Reason**: {recharge_data['recommendation_reason']}")
    
    # Structure comparison
    st.subheader("🏗️ Recharge Structure Options")
    
    structures_display = {
        "recharge_pit": "🕳️ Recharge Pit",
        "recharge_trench": "🚧 Recharge Trench", 
        "percolation_tank": "🏊 Percolation Tank",
        "injection_well": "🕳️ Injection Well"
    }
    
    cols = st.columns(len(recharge_data['structures']))
    
    for i, (struct_key, struct_data) in enumerate(recharge_data['structures'].items()):
        with cols[i]:
            st.markdown(f"**{structures_display[struct_key]}**")
            st.metric("Volume", f"{struct_data['volume']:.1f} m³")
            st.metric("Cost", f"₹{struct_data['cost']:,.0f}")
            st.metric("Annual Maintenance", f"₹{struct_data['maintenance_annual']:,.0f}")
            
            # Structure-specific dimensions
            if 'diameter' in struct_data and 'depth' in struct_data:
                st.write(f"📐 Ø{struct_data['diameter']:.1f}m × {struct_data['depth']:.1f}m deep")
            elif 'length' in struct_data:
                st.write(f"📐 {struct_data['length']:.1f}m × {struct_data['width']:.1f}m × {struct_data['depth']:.1f}m")
            elif 'area' in struct_data:
                st.write(f"📐 {struct_data['area']:.1f} m² area")
    
    # Cost summary for recommended structure
    recommended_cost = recharge_data['total_estimated_cost']
    recommended_maintenance = recharge_data['annual_maintenance_cost']
    
    st.success(f"💰 **Recommended Investment**: ₹{recommended_cost:,.0f} initial + ₹{recommended_maintenance:,.0f}/year maintenance")
    
    # Groundwater benefits
    st.subheader("🌍 Groundwater Benefits")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💧 Groundwater Recharge", f"{recharge_data['groundwater_recharge_benefit']:.1f} m³/year")
    with col2:
        # Calculate approximate groundwater value
        groundwater_value = recharge_data['groundwater_recharge_benefit'] * INDIAN_WATER_COSTS['borewell']
        st.metric("🏦 Groundwater Value", f"₹{groundwater_value:,.0f}/year")
    with col3:
        # Environmental benefit
        st.metric("🌱 Environmental Score", "High" if recharge_data['groundwater_recharge_benefit'] > 10 else "Medium")
    
    st.warning("⚠️ **Important**: Consult with hydrogeologist and check local regulations before implementing recharge structures")

# Tab 4: Environmental Impact
with tab4:
    st.subheader("🌍 Environmental Impact Assessment")
    
    env_impact = results['environmental_impact']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💧 Water Conservation", f"{env_impact['water_saved_liters']:,.0f} L/year")
        st.caption("Fresh water saved annually")
        
    with col2:
        st.metric("⚡ Energy Savings", f"{env_impact['energy_saved_kwh']:.0f} kWh/year")
        st.caption("Energy for water treatment/pumping")
        
    with col3:
        st.metric("🌿 CO₂ Reduction", f"{env_impact['co2_reduction_kg']:.0f} kg/year")
        st.caption("Carbon footprint reduction")
        
    with col4:
        st.metric("🌳 Tree Equivalent", f"{env_impact['equivalent_trees']:.1f} trees")
        st.caption("Environmental impact equivalence")
    
    # Additional environmental metrics
    st.subheader("🌱 Extended Environmental Benefits")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"🚗 **Transportation Impact**: Equivalent to {env_impact['equivalent_car_km']:,.0f} km less car travel per year")
        st.info(f"🌊 **Stormwater Management**: {env_impact['runoff_reduced_m3']:.1f} m³ reduced runoff")
        
    with col2:
        # Calculate additional benefits
        plastic_bottles_saved = env_impact['water_saved_liters'] / 1  # 1L bottles
        st.info(f"🍶 **Plastic Reduction**: ~{plastic_bottles_saved:,.0f} plastic bottles avoided")
        
        # Water security benefit
        security_score = min(100, (results['historical_coverage'] / 50) * 100)
        st.info(f"🔒 **Water Security Score**: {security_score:.0f}/100")

# Additional tabs for comprehensive analysis
if analysis_type == "Comprehensive Analysis":
    # Tab 5: Implementation Plan
    with tab5:
        st.subheader("📋 Implementation Roadmap")
        
        # Phase-wise implementation
        phases = [
            {
                "phase": "Phase 1: Planning & Permits",
                "duration": "Months 1-2", 
                "tasks": [
                    "Obtain building permits and approvals",
                    "Get detailed site survey and soil testing",
                    "Finalize system design and specifications",
                    "Get quotations from certified installers"
                ],
                "cost": "₹15,000 - ₹25,000"
            },
            {
                "phase": "Phase 2: System Installation", 
                "duration": "Months 2-4",
                "tasks": [
                    "Install storage tanks and piping",
                    "Set up filtration and treatment systems", 
                    "Install gutters and collection system",
                    "Commission and test the complete system"
                ],
                "cost": f"₹{results['cost_data']['total_initial']:,.0f}"
            },
            {
                "phase": "Phase 3: Recharge Structures",
                "duration": "Months 4-5", 
                "tasks": [
                    "Excavate and construct recharge structures",
                    "Install filter media and overflow systems",
                    "Connect overflow from storage to recharge",
                    "Test recharge efficiency"
                ],
                "cost": f"₹{recharge_data['total_estimated_cost']:,.0f}"
            },
            {
                "phase": "Phase 4: Monitoring & Optimization",
                "duration": "Months 5-6",
                "tasks": [
                    "Install monitoring equipment",
                    "Set up maintenance schedule",
                    "Train household members",
                    "Document system performance"
                ],
                "cost": "₹10,000 - ₹20,000"
            }
        ]
        
        for phase in phases:
            with st.expander(f"📅 {phase['phase']} ({phase['duration']})"):
                st.write(f"**Estimated Cost**: {phase['cost']}")
                st.write("**Key Activities**:")
                for task in phase['tasks']:
                    st.write(f"• {task}")
        
        # Timeline visualization
        st.subheader("📅 Implementation Timeline")
        
        timeline_data = {
            'Phase': ['Planning', 'Installation', 'Recharge', 'Monitoring'],
            'Start_Month': [1, 2, 4, 5],
            'Duration': [2, 2, 1, 1],
            'Investment': [20000, results['cost_data']['total_initial'], recharge_data['total_estimated_cost'], 15000]
        }
        
        timeline_df = pd.DataFrame(timeline_data)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Timeline chart
        for i, row in timeline_df.iterrows():
            ax1.barh(i, row['Duration'], left=row['Start_Month'], height=0.5, 
                    label=row['Phase'], alpha=0.7)
            ax1.text(row['Start_Month'] + row['Duration']/2, i, row['Phase'], 
                    ha='center', va='center', fontweight='bold')
        
        ax1.set_xlabel('Months')
        ax1.set_ylabel('Implementation Phases')
        ax1.set_title('Project Timeline')
        ax1.set_yticks(range(len(timeline_df)))
        ax1.set_yticklabels([])
        ax1.grid(axis='x', alpha=0.3)
        
        # Investment flow
        ax2.bar(timeline_df['Phase'], timeline_df['Investment'], alpha=0.7, color=['blue', 'green', 'orange', 'red'])
        ax2.set_ylabel('Investment (₹)')
        ax2.set_title('Phase-wise Investment')
        ax2.tick_params(axis='x', rotation=45)
        
        # Format y-axis
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x/100000:.1f}L' if x >= 100000 else f'₹{x/1000:.0f}K'))
        
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        
        # Government incentives and schemes
        st.subheader("🏛️ Government Incentives & Schemes")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Central Government Schemes:**")
            st.write("• Jal Shakti Abhiyan - Rainwater harvesting promotion")
            st.write("• MGNREGA - Funding for community RWH projects")
            st.write("• Smart Cities Mission - Urban water management")
            st.write("• Income tax benefits under Section 80C (some states)")
            
        with col2:
            st.markdown("**State-Level Benefits:**")
            st.write("• Property tax rebates (up to 10% in many cities)")
            st.write("• Building approval fast-track")
            st.write("• Subsidies for installation (varies by state)")
            st.write("• Mandatory RWH in new constructions")
        
        st.info("💡 **Tip**: Check with local municipal corporation for specific incentives in your area")
        
        # Maintenance schedule
        st.subheader("🔧 Maintenance Schedule")
        
        maintenance_schedule = {
            'Frequency': ['Monthly', 'Quarterly', 'Half-yearly', 'Annually'],
            'Tasks': [
                'Check gutters, clean debris, inspect first-flush diverter',
                'Clean storage tank, replace/clean filters, check pump',
                'Professional water quality testing, system inspection',
                'Deep cleaning, equipment servicing, roof maintenance'
            ],
            'Estimated_Cost': ['₹500', '₹2,000', '₹3,500', '₹8,000']
        }
        
        for i, freq in enumerate(maintenance_schedule['Frequency']):
            with st.expander(f"🔄 {freq} Maintenance"):
                st.write(f"**Tasks**: {maintenance_schedule['Tasks'][i]}")
                st.write(f"**Estimated Cost**: {maintenance_schedule['Estimated_Cost'][i]}")

    # Tab 6: Comprehensive Report
    with tab6:
        st.subheader("📊 Comprehensive Analysis Report")
        
        # Generate full report
        report = generate_comprehensive_report(
            location, results, soil_data, monsoon_forecast, recharge_data
        )
        
        # Report download
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.info("📄 Complete technical report with all analysis details")
            
        with col2:
            st.download_button(
                label="📥 Download Report",
                data=report,
                file_name=f"rainwater_harvesting_report_{address.replace(' ', '_').replace(',', '')}.txt",
                mime="text/plain"
            )
        
        # Display report in expandable section
        with st.expander("📖 View Full Report", expanded=False):
            st.text(report)
        
        # Key findings summary
        st.subheader("🔑 Key Findings & Recommendations")
        
        if feasibility_score >= 70:
            st.success("✅ **STRONG RECOMMENDATION**: Proceed with implementation")
            recommendations = [
                "System shows excellent financial viability",
                "High water harvest potential for your location",
                "Consider phased implementation starting with basic system",
                "Include groundwater recharge for maximum benefit"
            ]
        elif feasibility_score >= 50:
            st.info("ℹ️ **MODERATE RECOMMENDATION**: Proceed with optimizations")
            recommendations = [
                "System is economically viable with careful planning",
                "Consider starting with smaller system and expanding",
                "Focus on non-potable uses initially",
                "Monitor water costs - viability will improve over time"
            ]
        else:
            st.warning("⚠️ **LIMITED RECOMMENDATION**: Consider alternatives")
            recommendations = [
                "Current conditions show limited financial viability",
                "Consider water conservation measures first",
                "Monitor for changes in water costs or system costs",
                "Explore community-scale or shared systems"
            ]
        
        for recommendation in recommendations:
            st.write(f"• {recommendation}")

# --------------------------
# Additional Tools and Resources
# --------------------------
st.header("🛠️ Additional Tools & Resources")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🧮 Quick Calculator")
    with st.expander("💧 Monthly Savings Calculator"):
        monthly_consumption = st.number_input("Monthly water consumption (m³)", min_value=5.0, value=15.0)
        current_rate = INDIAN_WATER_COSTS[water_source]
        monthly_bill = monthly_consumption * current_rate
        
        potential_savings_percent = min(results['historical_coverage'], 80) / 100  # Cap at 80%
        potential_monthly_savings = monthly_bill * potential_savings_percent
        
        st.metric("Current Monthly Bill", f"₹{monthly_bill:,.0f}")
        st.metric("Potential Monthly Savings", f"₹{potential_monthly_savings:,.0f}")
        st.metric("Annual Savings", f"₹{potential_monthly_savings * 12:,.0f}")

with col2:
    st.subheader("📞 Expert Consultation")
    st.info("**Need Professional Help?**")
    st.write("• Certified water management engineers")
    st.write("• Soil testing laboratories")
    st.write("• RWH system installers")
    st.write("• Government subsidy consultants")
    
    if st.button("🔍 Find Local Experts"):
        st.info(f"Search for 'rainwater harvesting contractors near {address}'")

with col3:
    st.subheader("📚 Learning Resources")
    with st.expander("📖 Useful Links"):
        st.markdown("""
        **Government Resources:**
        • [Ministry of Jal Shakti](https://jalshakti.gov.in)
        • [Central Ground Water Board](https://cgwb.gov.in)
        • [Jal Shakti Abhiyan Guidelines](https://jalshakti.gov.in/jsa)
        
        **Technical Resources:**
        • Bureau of Indian Standards (BIS) codes
        • CPHEEO Manual on Water Supply
        • Rainwater Harvesting Guidelines
        """)

# --------------------------
# Comparison Tool
# --------------------------
st.header("⚖️ Comparison with Alternatives")

comparison_data = {
    'Water Source': ['Rainwater Harvesting', 'Municipal Supply', 'Water Tanker', 'Borewell'],
    'Initial Cost (₹)': [
        results['cost_data']['total_initial'],
        0,
        0, 
        150000  # Average borewell cost
    ],
    'Annual Cost (₹)': [
        results['cost_data']['total_annual'],
        results['total_demand'] * INDIAN_WATER_COSTS['municipal'],
        results['total_demand'] * INDIAN_WATER_COSTS['tanker'],
        results['total_demand'] * INDIAN_WATER_COSTS['borewell'] + 15000  # Electricity + maintenance
    ],
    'Reliability': ['High', 'Medium', 'Low', 'Medium'],
    'Environmental Impact': ['Very Low', 'Medium', 'High', 'Medium']
}

comparison_df = pd.DataFrame(comparison_data)

st.subheader("💰 20-Year Total Cost Comparison")

# Calculate 20-year costs
twenty_year_costs = []
for i in range(len(comparison_df)):
    total_cost = comparison_df.iloc[i]['Initial Cost (₹)'] + (comparison_df.iloc[i]['Annual Cost (₹)'] * 20)
    twenty_year_costs.append(total_cost)

comparison_df['20-Year Total Cost (₹)'] = twenty_year_costs

# Display comparison
st.dataframe(
    comparison_df.style.format({
        'Initial Cost (₹)': '₹{:,.0f}',
        'Annual Cost (₹)': '₹{:,.0f}',
        '20-Year Total Cost (₹)': '₹{:,.0f}'
    }).background_gradient(subset=['20-Year Total Cost (₹)'], cmap='RdYlGn_r'),
    use_container_width=True
)

# Find the most economical option
min_cost_idx = comparison_df['20-Year Total Cost (₹)'].idxmin()
most_economical = comparison_df.iloc[min_cost_idx]['Water Source']

if most_economical == 'Rainwater Harvesting':
    st.success(f"✅ Rainwater harvesting is the most economical option over 20 years!")
else:
    savings_compared_to_rwh = comparison_df.iloc[0]['20-Year Total Cost (₹)'] - comparison_df.iloc[min_cost_idx]['20-Year Total Cost (₹)']
    st.info(f"ℹ️ {most_economical} is more economical by ₹{savings_compared_to_rwh:,.0f} over 20 years")

# --------------------------
# Footer and Disclaimers  
# --------------------------
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📊 Data Sources")
    st.caption("• Rainfall: NASA POWER API")
    st.caption("• Soil: SoilGrids Global Database")
    st.caption("• Costs: Indian market averages")
    st.caption("• Weather: Climate models & trends")

with col2:
    st.subheader("🧮 Methodology")
    st.caption("• NPV with 7% discount rate")
    st.caption("• 20-year lifecycle analysis")
    st.caption("• 8% annual water cost increase")
    st.caption("• 80% system efficiency factor")

with col3:
    st.subheader("⚠️ Limitations")
    st.caption("• Based on historical patterns")
    st.caption("• Generalized cost estimates")
    st.caption("• Local regulations not included")
    st.caption("• Site-specific factors may vary")

st.markdown("---")
st.markdown("""
🔬 **Disclaimer**: This analysis provides estimates based on available meteorological and geographical data. 
For implementation, consult with certified water management professionals and comply with local building codes 
and regulations. Actual performance may vary based on site-specific conditions, maintenance practices, and 
implementation quality.

📧 **Feedback**: This tool is designed to promote sustainable water management in India. 
For technical support or suggestions, please consult local water management experts.
""")

st.markdown("**🌧️ Enhanced Rainwater Harvesting Analysis System v2.0 - Indian Edition**")
st.markdown("*Promoting water security and sustainability across India* 🇮🇳")
