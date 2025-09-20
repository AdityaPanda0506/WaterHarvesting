import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from geopy.geocoders import Nominatim
import json

# System efficiency (accounts for first flush, evaporation, etc.)
EFFICIENCY = 0.80

# Basic water needs (liters per person per day)
DRINKING_NEED = 5
DOMESTIC_NEED = 100
GARDEN_NEED = 5  # liters per m² per day (during dry months)

# Recharge structure parameters
RECHARGE_FACTOR = 0.7  # Percentage of water suitable for recharge
SOIL_PERMEABILITY = {
    "Sandy": {"factor": 1.2, "infiltration_rate": 30},       # mm/hr
    "Sandy Loam": {"factor": 1.0, "infiltration_rate": 20},  
    "Loam": {"factor": 0.8, "infiltration_rate": 12},        
    "Clay Loam": {"factor": 0.6, "infiltration_rate": 6},    
    "Clay": {"factor": 0.4, "infiltration_rate": 2},
    "Silt": {"factor": 0.5, "infiltration_rate": 4},
    "Unknown": {"factor": 0.8, "infiltration_rate": 12}      # Default values
}

# Cost parameters (in USD)
SYSTEM_COSTS = {
    "basic": {
        "tank_cost_per_m3": 200,
        "piping_cost": 500,
        "gutters_cost_per_m": 25,
        "first_flush_diverter": 150,
        "basic_filter": 100,
        "installation": 800,
        "maintenance_annual": 50
    },
    "intermediate": {
        "tank_cost_per_m3": 300,
        "piping_cost": 800,
        "gutters_cost_per_m": 35,
        "first_flush_diverter": 200,
        "sediment_filter": 250,
        "carbon_filter": 180,
        "installation": 1200,
        "maintenance_annual": 80
    },
    "advanced": {
        "tank_cost_per_m3": 450,
        "piping_cost": 1200,
        "gutters_cost_per_m": 50,
        "first_flush_diverter": 300,
        "multi_stage_filter": 500,
        "uv_sterilizer": 400,
        "pump_system": 600,
        "installation": 2000,
        "maintenance_annual": 150
    }
}

def get_location(address):
    """Get latitude and longitude from address"""
    try:
        geolocator = Nominatim(user_agent="rainwater_app_v1")
        location = geolocator.geocode(address, timeout=10)
        if not location:
            raise ValueError("Could not find this address")
        return location
    except Exception as e:
        print(f"Geocoding failed: {e}")
        return None

def get_soil_type(lat, lon):
    """Get soil type from coordinates using SoilGrids API"""
    try:
        # SoilGrids API for soil texture class
        url = f"https://rest.isric.org/soilgrids/v2.0/classification/query"
        params = {
            'lon': lon,
            'lat': lat,
            'number_classes': 5
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract soil texture information
            if 'wrb_class_name' in data:
                soil_class = data['wrb_class_name']
                
                # Map WRB soil classes to our simplified categories
                soil_mapping = {
                    'Arenosols': 'Sandy',
                    'Fluvisols': 'Sandy Loam',
                    'Cambisols': 'Loam',
                    'Luvisols': 'Clay Loam',
                    'Vertisols': 'Clay',
                    'Gleysols': 'Clay',
                    'Histosols': 'Loam',
                    'Leptosols': 'Sandy Loam',
                    'Regosols': 'Sandy',
                    'Solonchaks': 'Clay Loam',
                    'Solonetz': 'Clay Loam'
                }
                
                # Get the first classification
                primary_class = soil_class.split()[0] if isinstance(soil_class, str) else 'Unknown'
                mapped_soil = soil_mapping.get(primary_class, 'Loam')
                
                return {
                    'type': mapped_soil,
                    'source': 'SoilGrids API',
                    'raw_classification': soil_class,
                    'confidence': 'High'
                }
        
        # Fallback: try alternative soil data
        return get_soil_fallback(lat, lon)
        
    except Exception as e:
        print(f"Soil API Error: {e}")
        return get_soil_fallback(lat, lon)

def get_soil_fallback(lat, lon):
    """Fallback soil type estimation based on climate and geography"""
    try:
        # Simple heuristic based on latitude and climate
        if abs(lat) > 60:  # Arctic regions
            return {'type': 'Clay Loam', 'source': 'Climate heuristic', 'confidence': 'Low'}
        elif abs(lat) < 23.5:  # Tropical regions
            if lat > 0:  # Northern tropics
                return {'type': 'Sandy Loam', 'source': 'Climate heuristic', 'confidence': 'Low'}
            else:  # Southern tropics
                return {'type': 'Loam', 'source': 'Climate heuristic', 'confidence': 'Low'}
        else:  # Temperate regions
            return {'type': 'Loam', 'source': 'Climate heuristic', 'confidence': 'Low'}
    except:
        return {'type': 'Loam', 'source': 'Default', 'confidence': 'Very Low'}

def fetch_rainfall_data(lat, lon):
    """Fetch rainfall data from NASA POWER API"""
    url = "https://power.larc.nasa.gov/api/temporal/monthly/point"
    params = {
        "parameters": "PRECTOTCORR",
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": 2020,
        "end": 2023,
        "format": "JSON"
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        raw_data = data["properties"]["parameter"]["PRECTOTCORR"]
        
        # Process data for the most recent complete year
        year_data = {}
        for key, value in raw_data.items():
            if len(key) == 6 and key.startswith('2023'):  # Get most recent year
                month = int(key[4:6])
                if 1 <= month <= 12:
                    year_data[month] = value
        
        # Create DataFrame
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        
        df = pd.DataFrame({
            'Month': month_names,
            'Month_Num': range(1, 13),
            'Rainfall_mm': [year_data.get(i, 0) for i in range(1, 13)]
        })
        
        return df

    except Exception as e:
        print(f"NASA API Error: {e}")
        return None

def calculate_system_costs(roof_area, storage_capacity, system_type="intermediate"):
    """Calculate detailed system costs"""
    costs = SYSTEM_COSTS[system_type].copy()
    
    # Calculate component costs
    tank_cost = storage_capacity * costs["tank_cost_per_m3"]
    gutter_length = 2 * (roof_area ** 0.5) * 2  # Approximate gutter length
    gutter_cost = gutter_length * costs["gutters_cost_per_m"]
    
    # Total initial costs
    initial_costs = {
        "storage_tank": tank_cost,
        "gutters_downspouts": gutter_cost,
        "piping": costs["piping_cost"],
        "first_flush_diverter": costs["first_flush_diverter"],
        "filtration": costs.get("basic_filter", 0) + costs.get("sediment_filter", 0) + 
                     costs.get("carbon_filter", 0) + costs.get("multi_stage_filter", 0),
        "uv_sterilizer": costs.get("uv_sterilizer", 0),
        "pump_system": costs.get("pump_system", 0),
        "installation": costs["installation"]
    }
    
    total_initial = sum(initial_costs.values())
    
    # Annual operating costs
    annual_costs = {
        "maintenance": costs["maintenance_annual"],
        "filter_replacement": costs["maintenance_annual"] * 0.3,
        "electricity": 50 if "pump_system" in costs else 0,
        "water_testing": 100 if system_type == "advanced" else 0
    }
    
    total_annual = sum(annual_costs.values())
    
    return {
        "initial_costs": initial_costs,
        "total_initial": total_initial,
        "annual_costs": annual_costs,
        "total_annual": total_annual,
        "system_type": system_type
    }

def calculate_financial_metrics(cost_data, annual_savings, water_cost_increase=0.03, discount_rate=0.05, analysis_period=20):
    """Calculate comprehensive financial metrics"""
    
    # Cash flow analysis
    cash_flows = [-cost_data["total_initial"]]  # Initial investment
    
    for year in range(1, analysis_period + 1):
        # Annual savings with water cost inflation
        annual_benefit = annual_savings * (1 + water_cost_increase) ** year
        # Annual costs
        annual_cost = cost_data["total_annual"]
        # Net annual cash flow
        net_annual = annual_benefit - annual_cost
        cash_flows.append(net_annual)
    
    # Calculate NPV
    npv = sum([cf / (1 + discount_rate) ** i for i, cf in enumerate(cash_flows)])
    
    # Calculate IRR (simplified approximation)
    irr = calculate_irr_approximation(cash_flows)
    
    # Simple payback period
    cumulative_savings = 0
    payback_period = None
    for year in range(1, analysis_period + 1):
        annual_net = (annual_savings * (1 + water_cost_increase) ** year) - cost_data["total_annual"]
        cumulative_savings += annual_net
        if cumulative_savings >= cost_data["total_initial"] and payback_period is None:
            payback_period = year
    
    # Discounted payback period
    discounted_cumulative = 0
    discounted_payback = None
    for year in range(1, analysis_period + 1):
        annual_net = (annual_savings * (1 + water_cost_increase) ** year) - cost_data["total_annual"]
        discounted_annual = annual_net / (1 + discount_rate) ** year
        discounted_cumulative += discounted_annual
        if discounted_cumulative >= cost_data["total_initial"] and discounted_payback is None:
            discounted_payback = year
    
    # Cost-benefit ratio
    total_benefits_pv = sum([(annual_savings * (1 + water_cost_increase) ** year) / 
                            (1 + discount_rate) ** year for year in range(1, analysis_period + 1)])
    total_costs_pv = cost_data["total_initial"] + sum([cost_data["total_annual"] / 
                                                      (1 + discount_rate) ** year for year in range(1, analysis_period + 1)])
    
    benefit_cost_ratio = total_benefits_pv / total_costs_pv if total_costs_pv > 0 else 0
    
    return {
        "npv": npv,
        "irr": irr,
        "payback_period": payback_period,
        "discounted_payback": discounted_payback,
        "benefit_cost_ratio": benefit_cost_ratio,
        "total_benefits_pv": total_benefits_pv,
        "total_costs_pv": total_costs_pv,
        "analysis_period": analysis_period
    }

def calculate_irr_approximation(cash_flows):
    """Simple IRR approximation using iterative method"""
    try:
        def npv_at_rate(rate, cfs):
            return sum([cf / (1 + rate) ** i for i, cf in enumerate(cfs)])
        
        # Binary search for IRR
        low, high = -0.99, 1.0
        for _ in range(100):  # Max iterations
            mid = (low + high) / 2
            npv = npv_at_rate(mid, cash_flows)
            if abs(npv) < 0.01:  # Close enough
                return mid
            elif npv > 0:
                low = mid
            else:
                high = mid
        return mid
    except:
        return 0.0  # Return 0% if calculation fails

def calculate_environmental_impact(annual_harvest, roof_area):
    """Calculate environmental benefits"""
    
    # Water conservation
    water_saved_liters = annual_harvest * 1000
    
    # Energy savings (approximate)
    # Municipal water treatment and distribution: ~3.5 kWh per m³
    energy_saved_kwh = annual_harvest * 3.5
    co2_reduction_kg = energy_saved_kwh * 0.4  # ~0.4 kg CO2 per kWh
    
    # Stormwater runoff reduction
    runoff_coefficient = 0.9  # For typical roof
    total_annual_rainfall_volume = sum([month_rain * roof_area / 1000 for month_rain in [50, 45, 60, 40, 30, 25, 30, 35, 45, 55, 65, 60]])  # Example
    runoff_reduced_m3 = total_annual_rainfall_volume * runoff_coefficient * 0.8  # 80% collection efficiency
    
    return {
        "water_saved_liters": water_saved_liters,
        "energy_saved_kwh": energy_saved_kwh,
        "co2_reduction_kg": co2_reduction_kg,
        "runoff_reduced_m3": runoff_reduced_m3,
        "equivalent_trees": co2_reduction_kg / 22,  # Average tree absorbs ~22kg CO2/year
        "equivalent_car_miles": co2_reduction_kg / 0.4  # ~0.4 kg CO2 per mile
    }

def calculate_water_metrics(df_rain, roof_area, household_size, garden_area, water_cost):
    """Calculate all water metrics and create visualizations"""
    # Calculate harvested water
    df_rain["Harvested_Liters"] = df_rain["Rainfall_mm"] * roof_area * EFFICIENCY
    df_rain["Harvested_m3"] = df_rain["Harvested_Liters"] / 1000

    annual_rainfall = df_rain["Rainfall_mm"].sum()
    annual_harvest = df_rain["Harvested_m3"].sum()

    # Calculate annual demand
    drinking_demand = household_size * DRINKING_NEED * 365 / 1000  # m³/year
    domestic_demand = household_size * DOMESTIC_NEED * 365 / 1000  # m³/year

    # Garden demand (assuming 6 dry months)
    garden_demand = garden_area * GARDEN_NEED * 180 / 1000  # m³/year

    total_demand = drinking_demand + domestic_demand + garden_demand
    potential_coverage = min(100, (annual_harvest / total_demand * 100)) if total_demand > 0 else 0

    # Check for dry months
    dry_months = len(df_rain[df_rain["Rainfall_mm"] < 30])
    
    # Economic viability
    annual_savings = annual_harvest * water_cost
    
    # Storage recommendation (based on dry months)
    monthly_demand = total_demand / 12
    recommended_storage = max(monthly_demand * 2, annual_harvest * 0.15)  # At least 15% of annual harvest
    
    # Determine appropriate system type
    if annual_harvest < 20:
        system_type = "basic"
    elif annual_harvest < 50:
        system_type = "intermediate"
    else:
        system_type = "advanced"
    
    # Calculate costs and financial metrics
    cost_data = calculate_system_costs(roof_area, recommended_storage, system_type)
    financial_metrics = calculate_financial_metrics(cost_data, annual_savings)
    environmental_impact = calculate_environmental_impact(annual_harvest, roof_area)
    
    # Create visualizations
    rainfall_chart = create_rainfall_chart(df_rain)
    water_balance_chart = create_water_balance_chart(df_rain, total_demand/12)
    cost_analysis_chart = create_cost_analysis_chart(cost_data, financial_metrics)
    
    return {
        'annual_rainfall': annual_rainfall,
        'annual_harvest': annual_harvest,
        'drinking_demand': drinking_demand,
        'domestic_demand': domestic_demand,
        'garden_demand': garden_demand,
        'total_demand': total_demand,
        'potential_coverage': potential_coverage,
        'dry_months': dry_months,
        'annual_savings': annual_savings,
        'recommended_storage': recommended_storage,
        'system_type': system_type,
        'cost_data': cost_data,
        'financial_metrics': financial_metrics,
        'environmental_impact': environmental_impact,
        'rainfall_chart': rainfall_chart,
        'water_balance_chart': water_balance_chart,
        'cost_analysis_chart': cost_analysis_chart
    }

def create_rainfall_chart(df_rain):
    """Create rainfall distribution chart"""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(df_rain["Month"], df_rain["Rainfall_mm"], color="skyblue", edgecolor="navy", alpha=0.7)
    ax.axhline(y=30, color="red", linestyle="--", label="Dry Threshold (30mm)")
    ax.set_title("Monthly Rainfall Distribution", fontweight="bold")
    ax.set_ylabel("Rainfall (mm)")
    ax.tick_params(axis='x', rotation=45)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    return fig

def create_water_balance_chart(df_rain, monthly_demand):
    """Create water balance chart"""
    fig, ax = plt.subplots(figsize=(10, 5))
    x = range(len(df_rain))
    width = 0.35
    
    ax.bar(x, df_rain["Harvested_m3"], width, label='Harvested Supply', color='lightblue')
    ax.bar([i + width for i in x], [monthly_demand] * 12, width, label='Monthly Demand', color='salmon')
    
    ax.set_xlabel('Month')
    ax.set_ylabel('Water (m³)')
    ax.set_title('Monthly Water Supply vs Demand')
    ax.set_xticks([i + width/2 for i in x])
    ax.set_xticklabels(df_rain["Month"], rotation=45)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    
    return fig

def create_cost_analysis_chart(cost_data, financial_metrics):
    """Create cost-benefit analysis chart"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
    
    # Initial costs breakdown
    costs = cost_data["initial_costs"]
    ax1.pie(costs.values(), labels=costs.keys(), autopct='%1.1f%%', startangle=90)
    ax1.set_title("Initial Cost Breakdown")
    
    # Cash flow over time
    years = range(0, 21)
    cash_flow = [-cost_data["total_initial"]] + [200] * 20  # Simplified
    cumulative = np.cumsum(cash_flow)
    ax2.plot(years, cumulative, 'b-', linewidth=2)
    ax2.axhline(y=0, color='r', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Years')
    ax2.set_ylabel('Cumulative Cash Flow ($)')
    ax2.set_title('Cumulative Cash Flow Analysis')
    ax2.grid(True, alpha=0.3)
    
    # Financial metrics
    metrics = ['NPV', 'IRR (%)', 'Payback (yrs)', 'B/C Ratio']
    values = [
        financial_metrics['npv'],
        financial_metrics['irr'] * 100,
        financial_metrics['payback_period'] or 0,
        financial_metrics['benefit_cost_ratio']
    ]
    colors = ['green' if v > 0 else 'red' for v in values[:2]] + ['blue', 'orange']
    ax3.bar(metrics, values, color=colors, alpha=0.7)
    ax3.set_title('Key Financial Metrics')
    ax3.tick_params(axis='x', rotation=45)
    
    # Annual costs vs savings
    categories = ['Initial Cost', 'Annual Savings', 'Annual Costs']
    amounts = [cost_data["total_initial"], 300, cost_data["total_annual"]]  # Simplified values
    ax4.bar(categories, amounts, color=['red', 'green', 'orange'], alpha=0.7)
    ax4.set_title('Cost vs Savings Comparison')
    ax4.set_ylabel('Amount ($)')
    
    plt.tight_layout()
    return fig

def assess_feasibility(results):
    """Calculate enhanced feasibility score"""
    score = 0
    weights = {
        'rainfall': 20,
        'harvest': 20,
        'coverage': 15,
        'economic': 25,
        'payback': 20
    }
    
    # Rainfall adequacy
    if results['annual_rainfall'] >= 600:
        score += weights['rainfall']
    elif results['annual_rainfall'] >= 400:
        score += weights['rainfall'] * 0.7
    elif results['annual_rainfall'] >= 200:
        score += weights['rainfall'] * 0.4
    
    # Harvest potential
    if results['annual_harvest'] >= 30:
        score += weights['harvest']
    elif results['annual_harvest'] >= 15:
        score += weights['harvest'] * 0.7
    elif results['annual_harvest'] >= 5:
        score += weights['harvest'] * 0.4
    
    # Coverage potential
    if results['potential_coverage'] >= 50:
        score += weights['coverage']
    elif results['potential_coverage'] >= 30:
        score += weights['coverage'] * 0.7
    elif results['potential_coverage'] >= 15:
        score += weights['coverage'] * 0.4
    
    # Economic viability
    bcr = results['financial_metrics']['benefit_cost_ratio']
    if bcr >= 1.5:
        score += weights['economic']
    elif bcr >= 1.0:
        score += weights['economic'] * 0.7
    elif bcr >= 0.7:
        score += weights['economic'] * 0.4
    
    # Payback period
    payback = results['financial_metrics']['payback_period']
    if payback and payback <= 7:
        score += weights['payback']
    elif payback and payback <= 12:
        score += weights['payback'] * 0.7
    elif payback and payback <= 20:
        score += weights['payback'] * 0.4
    
    return min(100, score)

def calculate_recharge_structures(annual_harvest, soil_type, soil_data=None):
    """Calculate dimensions for various recharge structures with soil-specific design"""
    # Get soil properties
    soil_props = SOIL_PERMEABILITY.get(soil_type, SOIL_PERMEABILITY["Unknown"])
    recharge_volume = annual_harvest * RECHARGE_FACTOR
    effective_volume = recharge_volume * soil_props["factor"]
    
    # Adjust design based on infiltration rate
    infiltration_rate = soil_props["infiltration_rate"]  # mm/hr
    
    # Recharge Pit calculations (cylindrical) - optimized for soil type
    if infiltration_rate < 5:  # Low permeability
        pit_depth = 4.0  # Deeper for better infiltration
        pit_diameter = (effective_volume * 4 / (3.14 * pit_depth)) ** 0.5
    else:  # Higher permeability
        pit_depth = 3.0
        pit_diameter = (effective_volume * 4 / (3.14 * pit_depth)) ** 0.5
    
    pit_volume = 3.14 * (pit_diameter/2) ** 2 * pit_depth
    
    # Recharge Trench calculations - adjusted for soil
    trench_depth = 2.5 if infiltration_rate < 10 else 2.0
    trench_width = 2.0 if infiltration_rate < 5 else 1.5
    trench_length = effective_volume / (trench_depth * trench_width)
    trench_volume = trench_length * trench_width * trench_depth
    
    # Recharge Shaft calculations - better for clay soils
    shaft_depth = 8.0 if infiltration_rate < 5 else 5.0
    shaft_diameter = (effective_volume * 4 / (3.14 * shaft_depth)) ** 0.5
    shaft_volume = 3.14 * (shaft_diameter/2) ** 2 * shaft_depth
    
    # Determine recommended structure
    if effective_volume < 5:
        recommended = "Small Recharge Pit"
        recommended_cost_multiplier = 1.0
    elif soil_type in ["Clay", "Clay Loam"] and effective_volume > 15:
        recommended = "Recharge Shaft with Sand Filter"
        recommended_cost_multiplier = 1.3
    elif effective_volume > 25:
        recommended = "Recharge Trench System"
        recommended_cost_multiplier = 0.9
    else:
        recommended = "Recharge Pit with Filter Media"
        recommended_cost_multiplier = 1.1
    
    # Enhanced cost calculation
    base_cost = effective_volume * 180  # Base cost per m³
    soil_adjustment = 1.2 if soil_type in ["Clay", "Clay Loam"] else 1.0
    estimated_cost = base_cost * soil_adjustment * recommended_cost_multiplier
    
    # Calculate maintenance costs
    annual_maintenance_cost = estimated_cost * 0.05  # 5% of initial cost
    
    return {
        "pit": {
            "volume": pit_volume,
            "diameter": pit_diameter,
            "depth": pit_depth,
            "cost": pit_volume * 150 * soil_adjustment
        },
        "trench": {
            "volume": trench_volume,
            "length": trench_length,
            "width": trench_width,
            "depth": trench_depth,
            "cost": trench_volume * 130 * soil_adjustment
        },
        "shaft": {
            "volume": shaft_volume,
            "diameter": shaft_diameter,
            "depth": shaft_depth,
            "cost": shaft_volume * 200 * soil_adjustment
        },
        "recommended_structure": recommended,
        "estimated_cost": estimated_cost,
        "annual_maintenance_cost": annual_maintenance_cost,
        "annual_recharge": effective_volume,
        "soil_infiltration_rate": infiltration_rate,
        "soil_suitability": "High" if infiltration_rate > 15 else "Medium" if infiltration_rate > 5 else "Low"
    }