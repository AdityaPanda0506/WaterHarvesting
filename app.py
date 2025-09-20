import streamlit as st
from rainwater_utils import (
    get_location, fetch_rainfall_data, calculate_water_metrics, 
    assess_feasibility, calculate_recharge_structures, get_soil_type
)

# --------------------------
# 🎯 Enhanced Rainwater Harvesting Feasibility Assessment
# --------------------------

st.set_page_config(page_title="🌧️ Rainwater Harvesting Pro", page_icon="🌧️", layout="wide")
st.title("🌧️ Professional Rainwater Harvesting Feasibility Assessment")
st.markdown("**Comprehensive analysis with cost-benefit evaluation, ROI analysis, and automated soil detection**")

# --------------------------
# 📍 Address Input
# --------------------------

col1, col2 = st.columns([2, 1])

with col1:
    address = st.text_input("📍 Enter your full address (e.g., 'Eiffel Tower, Paris')", "")

with col2:
    water_cost = st.number_input(
        "💵 Current water cost (per m³)",
        min_value=0.1,
        value=2.5,
        step=0.1,
        help="Local water price per cubic meter"
    )

if not address:
    st.info("👆 Please enter an address to begin the comprehensive analysis.")
    st.stop()

# Get location
with st.spinner("📍 Locating address..."):
    location = get_location(address)
if not location:
    st.stop()

lat, lon = location.latitude, location.longitude
st.success(f"✅ Located: {location.address}")
st.write(f"**Coordinates**: {lat:.4f}, {lon:.4f}")

# --------------------------
# 🌍 Automated Soil Detection
# --------------------------

st.subheader("🌍 Soil Analysis")

with st.spinner("🌱 Detecting soil type from coordinates..."):
    soil_data = get_soil_type(lat, lon)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Detected Soil Type", soil_data['type'])
with col2:
    st.metric("Data Source", soil_data['source'])
with col3:
    confidence_color = {"High": "🟢", "Medium": "🟡", "Low": "🟠", "Very Low": "🔴"}
    st.metric("Confidence", f"{confidence_color.get(soil_data['confidence'], '⚪')} {soil_data['confidence']}")

if soil_data['confidence'] in ['Low', 'Very Low']:
    st.warning("⚠️ Low confidence in soil detection. You may want to verify with local soil testing.")

# Allow manual override
with st.expander("🔧 Override Soil Type (Optional)"):
    manual_override = st.checkbox("Use manual soil type selection")
    if manual_override:
        soil_type = st.selectbox(
            "Select Soil Type",
            options=["Sandy", "Sandy Loam", "Loam", "Clay Loam", "Clay", "Silt"],
            index=2,
            help="Choose based on local knowledge or soil testing"
        )
    else:
        soil_type = soil_data['type']

# --------------------------
# 🏠 Property Details
# --------------------------

st.subheader("🏠 Property Details")

col1, col2, col3, col4 = st.columns(4)

with col1:
    roof_area = st.number_input(
        "Roof Area (m²)",
        min_value=1.0,
        value=100.0,
        step=1.0,
        help="Total catchment area available"
    )

with col2:
    household_size = st.number_input(
        "Household Size (people)",
        min_value=1,
        value=4,
        step=1,
        help="Number of people in the household"
    )

with col3:
    garden_area = st.number_input(
        "Garden/Irrigation Area (m²)",
        min_value=0.0,
        value=50.0,
        step=1.0,
        help="Area requiring irrigation (if any)"
    )

with col4:
    water_cost_increase = st.number_input(
        "Annual Water Cost Increase (%)",
        min_value=0.0,
        value=3.0,
        step=0.5,
        help="Expected annual increase in water prices"
    ) / 100

# --------------------------
# 🌧️ Fetch and Process Data
# --------------------------

with st.spinner("🌧️ Fetching rainfall data and performing analysis..."):
    df_rain = fetch_rainfall_data(lat, lon)
    if df_rain is None:
        st.stop()

    # Calculate comprehensive water metrics
    results = calculate_water_metrics(df_rain, roof_area, household_size, garden_area, water_cost)

# --------------------------
# 📊 Executive Summary
# --------------------------

st.subheader("📊 Executive Summary")

# Key metrics in cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Annual Rainfall", f"{results['annual_rainfall']:.0f} mm")
    if results['annual_rainfall'] >= 500:
        st.success("✅ Adequate rainfall")
    else:
        st.warning("⚠️ Limited rainfall")

with col2:
    st.metric("Harvest Potential", f"{results['annual_harvest']:.1f} m³")
    st.caption(f"${results['annual_savings']:.0f}/year potential savings")

with col3:
    bcr = results['financial_metrics']['benefit_cost_ratio']
    st.metric("Benefit/Cost Ratio", f"{bcr:.2f}")
    if bcr >= 1.0:
        st.success("✅ Economically viable")
    else:
        st.warning("⚠️ Review economics")

with col4:
    payback = results['financial_metrics']['payback_period']
    if payback:
        st.metric("Payback Period", f"{payback:.1f} years")
        if payback <= 10:
            st.success("✅ Good payback")
        else:
            st.info("ℹ️ Long-term investment")
    else:
        st.metric("Payback Period", "Not viable")
        st.error("❌ No payback")

# Overall feasibility score
feasibility_score = assess_feasibility(results)
st.progress(feasibility_score / 100)
st.subheader(f"Overall Feasibility Score: {feasibility_score:.0f}/100")

if feasibility_score >= 80:
    st.success("🎉 **HIGHLY RECOMMENDED** - Excellent investment opportunity!")
elif feasibility_score >= 60:
    st.success("💧 **RECOMMENDED** - Good potential for rainwater harvesting")
elif feasibility_score >= 40:
    st.info("🤔 **CONSIDER** - Moderate benefits, evaluate carefully")
else:
    st.warning("⚠️ **LIMITED BENEFIT** - May not be cost-effective")

# --------------------------
# 💰 Detailed Financial Analysis
# --------------------------

st.subheader("💰 Comprehensive Financial Analysis")

tab1, tab2, tab3 = st.columns(3)

with tab1:
    st.markdown("**📋 System Recommendation**")
    st.info(f"**System Type**: {results['system_type'].title()}")
    st.info(f"**Storage Capacity**: {results['recommended_storage']:.1f} m³")

with tab2:
    st.markdown("**💵 Investment Summary**")
    st.metric("Initial Investment", f"${results['cost_data']['total_initial']:,.0f}")
    st.metric("Annual Operating Cost", f"${results['cost_data']['total_annual']:,.0f}")

with tab3:
    st.markdown("**📈 Returns**")
    st.metric("NPV (20 years)", f"${results['financial_metrics']['npv']:,.0f}")
    irr = results['financial_metrics']['irr'] * 100
    st.metric("Internal Rate of Return", f"{irr:.1f}%")

# --------------------------
# 🌍 Environmental Impact
# --------------------------

st.subheader("🌍 Environmental Impact Assessment")

env_impact = results['environmental_impact']

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Annual Water Saved", f"{env_impact['water_saved_liters']:,.0f} L")

with col2:
    st.metric("Energy Saved", f"{env_impact['energy_saved_kwh']:.0f} kWh/year")

with col3:
    st.metric("CO₂ Reduction", f"{env_impact['co2_reduction_kg']:.0f} kg/year")

with col4:
    st.metric("Equivalent Trees", f"{env_impact['equivalent_trees']:.1f} trees")

st.info(f"🚗 **Carbon Impact**: Equivalent to driving {env_impact['equivalent_car_miles']:,.0f} fewer miles per year")

# --------------------------
# 📈 Detailed Analysis Tabs
# --------------------------

st.subheader("📈 Detailed Analysis")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["💧 Water Analysis", "💰 Cost Breakdown", "🌊 Recharge Structures", "📊 Financial Projections", "🎯 Recommendations"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.pyplot(results['rainfall_chart'])
    
    with col2:
        st.pyplot(results['water_balance_chart'])
    
    # Water demand breakdown
    st.subheader("Water Demand Analysis")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Drinking Water", f"{results['drinking_demand']:.1f} m³/year")
    with col2:
        st.metric("Domestic Use", f"{results['domestic_demand']:.1f} m³/year")
    with col3:
        st.metric("Garden Irrigation", f"{results['garden_demand']:.1f} m³/year")
    with col4:
        st.metric("Demand Coverage", f"{results['potential_coverage']:.1f}%")

with tab2:
    st.pyplot(results['cost_analysis_chart'])
    
    # Detailed cost breakdown
    st.subheader("Cost Breakdown Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Initial Costs**")
        costs = results['cost_data']['initial_costs']
        for component, cost in costs.items():
            st.write(f"• {component.replace('_', ' ').title()}: ${cost:,.0f}")
        st.markdown(f"**Total Initial: ${results['cost_data']['total_initial']:,.0f}**")
    
    with col2:
        st.markdown("**Annual Operating Costs**")
        annual_costs = results['cost_data']['annual_costs']
        for component, cost in annual_costs.items():
            st.write(f"• {component.replace('_', ' ').title()}: ${cost:,.0f}")
        st.markdown(f"**Total Annual: ${results['cost_data']['total_annual']:,.0f}**")

with tab3:
    st.subheader("🌊 Groundwater Recharge Structures")
    
    # Calculate recharge structures with detected soil type
    recharge_results = calculate_recharge_structures(results['annual_harvest'], soil_type, soil_data)
    
    # Soil suitability assessment
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Soil Type", soil_type)
    with col2:
        st.metric("Infiltration Rate", f"{recharge_results['soil_infiltration_rate']} mm/hr")
    with col3:
        suitability = recharge_results['soil_suitability']
        color_map = {"High": "success", "Medium": "info", "Low": "warning"}
        st.metric("Recharge Suitability", suitability)
        if suitability == "High":
            st.success("✅ Excellent for recharge")
        elif suitability == "Medium":
            st.info("ℹ️ Moderate recharge potential")
        else:
            st.warning("⚠️ Limited recharge capability")
    
    st.info(f"**Annual Recharge Potential**: {recharge_results['annual_recharge']:.1f} m³")
    
    # Structure comparison
    st.subheader("Recharge Structure Options")
    
    col1, col2, col3 = st.columns(3)
    
    structures = ['pit', 'trench', 'shaft']
    structure_names = ['Recharge Pit', 'Recharge Trench', 'Recharge Shaft']
    
    for i, (struct, name) in enumerate(zip(structures, structure_names)):
        with [col1, col2, col3][i]:
            st.markdown(f"**{name}**")
            data = recharge_results[struct]
            st.write(f"Volume: {data['volume']:.1f} m³")
            st.write(f"Cost: ${data['cost']:,.0f}")
            
            if struct == 'pit':
                st.write(f"Diameter: {data['diameter']:.1f}m")
                st.write(f"Depth: {data['depth']:.1f}m")
            elif struct == 'trench':
                st.write(f"Length: {data['length']:.1f}m")
                st.write(f"Width: {data['width']:.1f}m")
                st.write(f"Depth: {data['depth']:.1f}m")
            else:  # shaft
                st.write(f"Diameter: {data['diameter']:.1f}m")
                st.write(f"Depth: {data['depth']:.1f}m")
    
    st.success(f"**Recommended**: {recharge_results['recommended_structure']}")
    st.info(f"**Estimated Cost**: ${recharge_results['estimated_cost']:,.0f}")
    st.caption(f"**Annual Maintenance**: ${recharge_results['annual_maintenance_cost']:,.0f}")
    
    st.warning("⚠️ Consult with a hydrogeologist and check local regulations before construction")

with tab4:
    st.subheader("📊 20-Year Financial Projection")
    
    # Create financial projection table
    years = list(range(1, 21))
    annual_savings = [results['annual_savings'] * (1 + water_cost_increase) ** year for year in years]
    annual_costs = [results['cost_data']['total_annual']] * 20
    net_annual = [savings - cost for savings, cost in zip(annual_savings, annual_costs)]
    cumulative = []
    cum_sum = -results['cost_data']['total_initial']  # Start with negative initial investment
    
    for net in net_annual:
        cum_sum += net
        cumulative.append(cum_sum)
    
    # Display key financial metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Net Present Value", f"${results['financial_metrics']['npv']:,.0f}")
        if results['financial_metrics']['npv'] > 0:
            st.success("✅ Positive NPV")
        else:
            st.error("❌ Negative NPV")
    
    with col2:
        irr = results['financial_metrics']['irr']
        st.metric("Internal Rate of Return", f"{irr*100:.1f}%")
        if irr > 0.05:  # 5% threshold
            st.success("✅ Good return")
        else:
            st.warning("⚠️ Low return")
    
    with col3:
        discounted_payback = results['financial_metrics']['discounted_payback']
        if discounted_payback:
            st.metric("Discounted Payback", f"{discounted_payback:.1f} years")
        else:
            st.metric("Discounted Payback", "No payback")
    
    # Create projection chart
    import pandas as pd
    import matplotlib.pyplot as plt
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Annual cash flow
    ax1.bar(years, annual_savings, alpha=0.7, label='Annual Savings', color='green')
    ax1.bar(years, [-cost for cost in annual_costs], alpha=0.7, label='Annual Costs', color='red')
    ax1.plot(years, net_annual, 'b-', linewidth=2, label='Net Annual Cash Flow')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Cash Flow ($)')
    ax1.set_title('Annual Cash Flow Projection')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Cumulative cash flow
    ax2.plot(years, cumulative, 'g-', linewidth=3, label='Cumulative Cash Flow')
    ax2.axhline(y=0, color='r', linestyle='--', alpha=0.5, label='Break-even')
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Cumulative Cash Flow ($)')
    ax2.set_title('Cumulative Cash Flow Analysis')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig)

with tab5:
    st.subheader("🎯 Implementation Recommendations")
    
    # Customized recommendations based on results
    if feasibility_score >= 70:
        st.success("**Strong Recommendation: Proceed with Implementation**")
        st.markdown("""
        **Phase 1 (Immediate):**
        - Obtain necessary permits and approvals
        - Get detailed quotes from certified installers
        - Consider starting with basic system and upgrading later
        
        **Phase 2 (3-6 months):**
        - Install recommended system with proper filtration
        - Set up monitoring and maintenance schedule
        - Consider adding recharge structures
        """)
    elif feasibility_score >= 40:
        st.info("**Conditional Recommendation: Evaluate Options**")
        st.markdown("""
        **Consider These Alternatives:**
        - Start with a smaller, basic system for garden irrigation
        - Focus on high-efficiency fixtures to reduce water demand
        - Monitor water costs and reassess if prices increase
        - Consider community-scale systems with neighbors
        """)
    else:
        st.warning("**Limited Recommendation: Alternative Strategies**")
        st.markdown("""
        **Alternative Water Conservation:**
        - Install low-flow fixtures and appliances
        - Implement greywater recycling systems
        - Consider drought-resistant landscaping
        - Monitor for future improvements in system costs
        """)
    
    # Technical recommendations
    st.subheader("Technical Recommendations")
    
    recommended_features = []
    if results['annual_harvest'] > 30:
        recommended_features.append("• Multi-stage filtration system")
        recommended_features.append("• UV sterilization for potable use")
    
    if results['dry_months'] >= 4:
        recommended_features.append("• Larger storage capacity (consider underground tanks)")
        recommended_features.append("• Backup connection to municipal supply")
    
    if soil_data['type'] in ['Sandy', 'Sandy Loam']:
        recommended_features.append("• Groundwater recharge structures")
        recommended_features.append("• Overflow management system")
    
    if results['garden_demand'] > 10:
        recommended_features.append("• Dedicated irrigation system")
        recommended_features.append("• Drip irrigation for efficiency")
    
    if recommended_features:
        st.markdown("**Recommended Features:**")
        for feature in recommended_features:
            st.markdown(feature)
    
    # Maintenance schedule
    st.subheader("Maintenance Schedule")
    st.markdown("""
    **Monthly:**
    - Check gutters and downspouts for debris
    - Inspect first-flush diverters
    - Monitor water quality (visual inspection)
    
    **Quarterly:**
    - Clean storage tank and check for algae
    - Replace/clean filters
    - Test water quality if used for drinking
    
    **Annually:**
    - Professional system inspection
    - Pump and motor maintenance
    - Roof and gutter deep cleaning
    """)

# --------------------------
# 💡 Additional Considerations
# --------------------------

with st.expander("💡 Additional Considerations & Insights"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🏛️ Regulatory Considerations:**")
        st.markdown("""
        - Check local building codes and permits
        - Verify health department requirements for potable systems
        - Consider rainwater rights and regulations
        - Look for government incentives or rebates
        """)
        
        st.markdown("**⚡ Technology Considerations:**")
        st.markdown("""
        - Smart monitoring systems for optimization
        - Automated switching between sources
        - Integration with home automation
        - Future expansion capabilities
        """)
    
    with col2:
        st.markdown("**🌍 Climate Adaptation:**")
        st.markdown("""
        - Consider climate change impacts on rainfall
        - Plan for extreme weather events
        - Design for seasonal variations
        - Include drought contingency planning
        """)
        
        st.markdown("**💰 Financing Options:**")
        st.markdown("""
        - Green building loans or credits
        - Utility rebate programs
        - Tax incentives for water conservation
        - Phased implementation to spread costs
        """)

# --------------------------
# 📊 Data Sources & Methodology
# --------------------------

st.divider()
st.subheader("📊 Data Sources & Methodology")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📡 Data Sources:**")
    st.caption("• Rainfall: NASA POWER API (PRECTOTCORR)")
    st.caption("• Soil: SoilGrids Global Database")
    st.caption("• Costs: Industry averages & regional data")

with col2:
    st.markdown("**🧮 Analysis Methods:**")
    st.caption("• NPV with 5% discount rate")
    st.caption("• 20-year lifecycle analysis")
    st.caption("• Monte Carlo uncertainty analysis")

with col3:
    st.markdown("**⚠️ Limitations:**")
    st.caption("• Historical weather patterns")
    st.caption("• Generalized cost estimates")
    st.caption("• Local regulations not included")

st.caption("🔬 **Disclaimer**: This analysis provides estimates based on available data. Consult with local professionals for detailed design and implementation.")