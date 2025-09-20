import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from geopy.geocoders import Nominatim
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

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

# Cost parameters (in INR) - Updated for Indian market
SYSTEM_COSTS = {
    "basic": {
        "tank_cost_per_m3": 15000,      # ₹15,000 per m³
        "piping_cost": 35000,           # ₹35,000
        "gutters_cost_per_m": 1500,     # ₹1,500 per meter
        "first_flush_diverter": 8000,   # ₹8,000
        "basic_filter": 6000,           # ₹6,000
        "installation": 45000,          # ₹45,000
        "maintenance_annual": 3000      # ₹3,000 per year
    },
    "intermediate": {
        "tank_cost_per_m3": 22000,      # ₹22,000 per m³
        "piping_cost": 55000,           # ₹55,000
        "gutters_cost_per_m": 2200,     # ₹2,200 per meter
        "first_flush_diverter": 12000,  # ₹12,000
        "sediment_filter": 15000,       # ₹15,000
        "carbon_filter": 12000,         # ₹12,000
        "installation": 75000,          # ₹75,000
        "maintenance_annual": 5500      # ₹5,500 per year
    },
    "advanced": {
        "tank_cost_per_m3": 35000,      # ₹35,000 per m³
        "piping_cost": 85000,           # ₹85,000
        "gutters_cost_per_m": 3000,     # ₹3,000 per meter
        "first_flush_diverter": 18000,  # ₹18,000
        "multi_stage_filter": 35000,    # ₹35,000
        "uv_sterilizer": 25000,         # ₹25,000
        "pump_system": 40000,           # ₹40,000
        "installation": 120000,         # ₹1,20,000
        "maintenance_annual": 10000     # ₹10,000 per year
    }
}

# Indian water cost parameters (INR per m³)
INDIAN_WATER_COSTS = {
    "municipal": 15,     # Average municipal water cost in India
    "tanker": 45,        # Water tanker cost
    "borewell": 8        # Borewell water cost (electricity + maintenance)
}

def get_location(address):
    """Get latitude and longitude from address"""
    try:
        geolocator = Nominatim(user_agent="rainwater_app_india_v2")
        location = geolocator.geocode(address + ", India", timeout=10)
        if not location:
            raise ValueError("Could not find this address in India")
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
        
        response = requests.get(url, params=params, timeout=15)
        
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
    """Fallback soil type estimation based on climate and geography for India"""
    try:
        # India-specific heuristic based on regions
        if 8 <= lat <= 37 and 68 <= lon <= 97:  # Within India bounds
            if lat > 30:  # Northern India (Punjab, Haryana, UP)
                return {'type': 'Loam', 'source': 'India regional heuristic', 'confidence': 'Medium'}
            elif lat > 23:  # Central India (Maharashtra, MP, Rajasthan)
                return {'type': 'Clay Loam', 'source': 'India regional heuristic', 'confidence': 'Medium'}
            elif lat > 15:  # South Central (Karnataka, Telangana, AP)
                return {'type': 'Sandy Loam', 'source': 'India regional heuristic', 'confidence': 'Medium'}
            else:  # Southern India (Tamil Nadu, Kerala)
                return {'type': 'Clay', 'source': 'India regional heuristic', 'confidence': 'Medium'}
        else:
            return {'type': 'Loam', 'source': 'Default', 'confidence': 'Low'}
    except:
        return {'type': 'Loam', 'source': 'Default', 'confidence': 'Very Low'}

def fetch_historical_rainfall_data(lat, lon):
    """Fetch historical rainfall data from NASA POWER API"""
    url = "https://power.larc.nasa.gov/api/temporal/monthly/point"
    params = {
        "parameters": "PRECTOTCORR",
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": 2019,
        "end": 2023,
        "format": "JSON"
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        raw_data = data["properties"]["parameter"]["PRECTOTCORR"]
        
        # Process data for multiple years to get averages
        yearly_data = {}
        for key, value in raw_data.items():
            if len(key) == 6:  # Format: YYYYMM
                year = int(key[:4])
                month = int(key[4:6])
                if year not in yearly_data:
                    yearly_data[year] = {}
                if 1 <= month <= 12:
                    yearly_data[year][month] = value
        
        # Calculate monthly averages across years
        monthly_avg = {}
        for month in range(1, 13):
            values = []
            for year_data in yearly_data.values():
                if month in year_data:
                    values.append(year_data[month])
            monthly_avg[month] = np.mean(values) if values else 0
        
        # Create DataFrame
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        
        df = pd.DataFrame({
            'Month': month_names,
            'Month_Num': range(1, 13),
            'Historical_Rainfall_mm': [monthly_avg.get(i, 0) for i in range(1, 13)]
        })
        
        return df, yearly_data

    except Exception as e:
        print(f"NASA API Error: {e}")
        return None, None

def fetch_weather_forecast_data(lat, lon):
    """Fetch weather forecast data using OpenWeatherMap API"""
    # This would require an API key, so we'll simulate with climate models
    try:
        # Using NASA POWER for climate projections (simplified approach)
        # In production, you'd use weather APIs like OpenWeatherMap, AccuWeather, etc.
        
        # For demonstration, we'll create a forecast based on historical trends
        historical_df, yearly_data = fetch_historical_rainfall_data(lat, lon)
        if historical_df is None:
            return None
        
        # Simple trend analysis and projection
        future_months = []
        current_date = datetime.now()
        
        for i in range(12):  # Next 12 months
            future_date = current_date + timedelta(days=30*i)
            month_num = future_date.month
            
            # Get historical average for this month
            historical_avg = historical_df[historical_df['Month_Num'] == month_num]['Historical_Rainfall_mm'].iloc[0]
            
            # Apply climate trend (simplified - in reality would use climate models)
            # Assuming slight increase due to climate change (varies by region)
            climate_factor = 1.05 if month_num in [6, 7, 8, 9] else 0.98  # Monsoon vs non-monsoon
            
            # Add some seasonal variation
            seasonal_variation = np.random.normal(1.0, 0.15)  # 15% standard deviation
            
            predicted_rainfall = historical_avg * climate_factor * seasonal_variation
            predicted_rainfall = max(0, predicted_rainfall)  # Ensure non-negative
            
            future_months.append({
                'Month': future_date.strftime('%B %Y'),
                'Month_Num': month_num,
                'Predicted_Rainfall_mm': predicted_rainfall,
                'Confidence': 'Medium' if i < 6 else 'Low'  # Confidence decreases with time
            })
        
        return pd.DataFrame(future_months)
        
    except Exception as e:
        print(f"Weather forecast error: {e}")
        return None

def fetch_imd_monsoon_forecast(lat, lon):
    """Fetch IMD (India Meteorological Department) style seasonal forecast"""
    try:
        # This simulates IMD seasonal forecasts
        # In production, you'd integrate with IMD APIs or other meteorological services
        
        current_year = datetime.now().year
        
        # Simulate seasonal forecast based on region
        if 10 <= lat <= 30:  # Northern/Central India
            monsoon_forecast = {
                'seasonal_rainfall_percent': np.random.normal(102, 15),  # % of normal
                'monsoon_onset_date': f"June {np.random.randint(1, 15)}, {current_year}",
                'monsoon_withdrawal_date': f"October {np.random.randint(1, 15)}, {current_year}",
                'heavy_rainfall_days': np.random.randint(15, 25),
                'drought_risk': 'Low' if np.random.random() > 0.3 else 'Medium',
                'flood_risk': 'Medium' if np.random.random() > 0.7 else 'Low'
            }
        else:  # Southern India
            monsoon_forecast = {
                'seasonal_rainfall_percent': np.random.normal(98, 12),
                'monsoon_onset_date': f"June {np.random.randint(1, 10)}, {current_year}",
                'monsoon_withdrawal_date': f"November {np.random.randint(15, 30)}, {current_year}",
                'heavy_rainfall_days': np.random.randint(20, 30),
                'drought_risk': 'Low',
                'flood_risk': 'Medium' if np.random.random() > 0.6 else 'Low'
            }
        
        return monsoon_forecast
        
    except Exception as e:
        print(f"IMD forecast simulation error: {e}")
        return None

def calculate_system_costs(roof_area, storage_capacity, system_type="intermediate"):
    """Calculate detailed system costs in INR"""
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
        "filter_replacement": costs["maintenance_annual"] * 0.4,
        "electricity": 3500 if "pump_system" in costs else 0,  # ₹3,500 for pump operation
        "water_testing": 2500 if system_type == "advanced" else 0  # ₹2,500 for testing
    }
    
    total_annual = sum(annual_costs.values())
    
    return {
        "initial_costs": initial_costs,
        "total_initial": total_initial,
        "annual_costs": annual_costs,
        "total_annual": total_annual,
        "system_type": system_type
    }

def calculate_financial_metrics(cost_data, annual_savings, water_cost_increase=0.08, discount_rate=0.07, analysis_period=20):
    """Calculate comprehensive financial metrics (adjusted for Indian market)"""
    
    # Cash flow analysis with detailed yearly breakdown
    cash_flows = [-cost_data["total_initial"]]  # Initial investment
    yearly_analysis = []
    cumulative = -cost_data["total_initial"]
    
    for year in range(1, analysis_period + 1):
        # Annual savings with water cost inflation (higher in India)
        annual_benefit = annual_savings * (1 + water_cost_increase) ** year
        # Annual costs
        annual_cost = cost_data["total_annual"]
        # Net annual cash flow
        net_annual = annual_benefit - annual_cost
        cash_flows.append(net_annual)
        
        # Update cumulative
        cumulative += net_annual
        
        # Store yearly details
        yearly_analysis.append({
            'year': year,
            'benefits': annual_benefit,
            'costs': annual_cost,
            'net_annual': net_annual,
            'cumulative': cumulative,
            'discounted_net': net_annual / (1 + discount_rate) ** year
        })
    
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
        "analysis_period": analysis_period,
        "yearly_analysis": yearly_analysis
    }

def calculate_irr_approximation(cash_flows):
    """Simple IRR approximation using iterative method"""
    try:
        def npv_at_rate(rate, cfs):
            return sum([cf / (1 + rate) ** i for i, cf in enumerate(cfs)])
        
        # Binary search for IRR
        low, high = -0.99, 2.0
        for _ in range(100):  # Max iterations
            mid = (low + high) / 2
            npv = npv_at_rate(mid, cash_flows)
            if abs(npv) < 100:  # Close enough (in INR)
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
    
    # Energy savings (approximate for India)
    # Municipal water treatment and distribution: ~4.5 kWh per m³ (higher due to pumping)
    energy_saved_kwh = annual_harvest * 4.5
    co2_reduction_kg = energy_saved_kwh * 0.82  # India's grid emission factor ~0.82 kg CO2 per kWh
    
    # Stormwater runoff reduction
    runoff_coefficient = 0.9  # For typical roof
    runoff_reduced_m3 = annual_harvest * 0.8  # Simplified calculation
    
    return {
        "water_saved_liters": water_saved_liters,
        "energy_saved_kwh": energy_saved_kwh,
        "co2_reduction_kg": co2_reduction_kg,
        "runoff_reduced_m3": runoff_reduced_m3,
        "equivalent_trees": co2_reduction_kg / 22,  # Average tree absorbs ~22kg CO2/year
        "equivalent_car_km": co2_reduction_kg * 4.2  # ~0.24 kg CO2 per km (converted to km saved)
    }

def calculate_water_metrics(historical_df, forecast_df, roof_area, household_size, garden_area, water_source="municipal"):
    """Calculate all water metrics including future predictions"""
    
    # Select appropriate water cost
    water_cost = INDIAN_WATER_COSTS[water_source]
    
    # Historical calculations
    historical_df["Harvested_Liters"] = historical_df["Historical_Rainfall_mm"] * roof_area * EFFICIENCY
    historical_df["Harvested_m3"] = historical_df["Harvested_Liters"] / 1000
    
    annual_rainfall_historical = historical_df["Historical_Rainfall_mm"].sum()
    annual_harvest_historical = historical_df["Harvested_m3"].sum()
    
    # Future predictions
    future_harvest = 0
    future_rainfall = 0
    if forecast_df is not None:
        forecast_df["Predicted_Harvested_Liters"] = forecast_df["Predicted_Rainfall_mm"] * roof_area * EFFICIENCY
        forecast_df["Predicted_Harvested_m3"] = forecast_df["Predicted_Harvested_Liters"] / 1000
        
        future_rainfall = forecast_df["Predicted_Rainfall_mm"].sum()
        future_harvest = forecast_df["Predicted_Harvested_m3"].sum()

    # Calculate annual demand
    drinking_demand = household_size * DRINKING_NEED * 365 / 1000  # m³/year
    domestic_demand = household_size * DOMESTIC_NEED * 365 / 1000  # m³/year
    garden_demand = garden_area * GARDEN_NEED * 180 / 1000  # m³/year (6 dry months)

    total_demand = drinking_demand + domestic_demand + garden_demand
    
    # Coverage calculations
    historical_coverage = min(100, (annual_harvest_historical / total_demand * 100)) if total_demand > 0 else 0
    future_coverage = min(100, (future_harvest / total_demand * 100)) if total_demand > 0 and future_harvest > 0 else 0

    # Check for dry months
    dry_months_historical = len(historical_df[historical_df["Historical_Rainfall_mm"] < 30])
    dry_months_future = len(forecast_df[forecast_df["Predicted_Rainfall_mm"] < 30]) if forecast_df is not None else 0
    
    # Economic analysis
    annual_savings_historical = annual_harvest_historical * water_cost
    annual_savings_future = future_harvest * water_cost if future_harvest > 0 else annual_savings_historical
    
    # Storage recommendation
    monthly_demand = total_demand / 12
    recommended_storage = max(monthly_demand * 2.5, annual_harvest_historical * 0.2)  # Increased for India
    
    # System type determination
    avg_harvest = (annual_harvest_historical + future_harvest) / 2 if future_harvest > 0 else annual_harvest_historical
    if avg_harvest < 15:
        system_type = "basic"
    elif avg_harvest < 40:
        system_type = "intermediate"
    else:
        system_type = "advanced"
    
    # Calculate costs and financial metrics
    cost_data = calculate_system_costs(roof_area, recommended_storage, system_type)
    financial_metrics = calculate_financial_metrics(cost_data, annual_savings_future)
    environmental_impact = calculate_environmental_impact(annual_harvest_historical, roof_area)
    
    return {
        'annual_rainfall_historical': annual_rainfall_historical,
        'annual_harvest_historical': annual_harvest_historical,
        'annual_rainfall_future': future_rainfall,
        'annual_harvest_future': future_harvest,
        'drinking_demand': drinking_demand,
        'domestic_demand': domestic_demand,
        'garden_demand': garden_demand,
        'total_demand': total_demand,
        'historical_coverage': historical_coverage,
        'future_coverage': future_coverage,
        'dry_months_historical': dry_months_historical,
        'dry_months_future': dry_months_future,
        'annual_savings_historical': annual_savings_historical,
        'annual_savings_future': annual_savings_future,
        'recommended_storage': recommended_storage,
        'system_type': system_type,
        'cost_data': cost_data,
        'financial_metrics': financial_metrics,
        'environmental_impact': environmental_impact,
        'water_source': water_source,
        'water_cost_per_m3': water_cost
    }

def create_comprehensive_charts(historical_df, forecast_df, results):
    """Create comprehensive visualization charts"""
    
    # Create a figure with multiple subplots
    fig = plt.figure(figsize=(16, 12))
    
    # 1. Historical vs Future Rainfall Comparison
    ax1 = plt.subplot(2, 3, 1)
    months = historical_df["Month"]
    
    ax1.bar(np.arange(len(months)) - 0.2, historical_df["Historical_Rainfall_mm"], 
            width=0.4, label='Historical (Avg)', color='skyblue', alpha=0.7)
    
    if forecast_df is not None:
        # Group forecast data by month for comparison
        forecast_monthly = forecast_df.groupby('Month_Num')['Predicted_Rainfall_mm'].mean()
        future_values = [forecast_monthly.get(i, 0) for i in range(1, 13)]
        
        ax1.bar(np.arange(len(months)) + 0.2, future_values, 
                width=0.4, label='Future Prediction', color='orange', alpha=0.7)
    
    ax1.axhline(y=30, color="red", linestyle="--", alpha=0.5, label="Dry Threshold")
    ax1.set_title("Historical vs Future Rainfall Prediction", fontweight="bold", fontsize=12)
    ax1.set_ylabel("Rainfall (mm)")
    ax1.set_xticks(range(len(months)))
    ax1.set_xticklabels([m[:3] for m in months], rotation=45)
    ax1.legend(fontsize=9)
    ax1.grid(axis="y", alpha=0.3)
    
    # 2. Water Harvest Potential
    ax2 = plt.subplot(2, 3, 2)
    harvest_historical = historical_df["Harvested_m3"]
    monthly_demand = results['total_demand'] / 12
    
    ax2.bar(range(len(months)), harvest_historical, 
            label='Historical Harvest', color='lightblue', alpha=0.7)
    ax2.axhline(y=monthly_demand, color="red", linestyle="-", 
                label=f"Monthly Demand ({monthly_demand:.1f} m³)")
    
    ax2.set_title("Monthly Water Harvest vs Demand", fontweight="bold", fontsize=12)
    ax2.set_ylabel("Water (m³)")
    ax2.set_xticks(range(len(months)))
    ax2.set_xticklabels([m[:3] for m in months], rotation=45)
    ax2.legend(fontsize=9)
    ax2.grid(axis="y", alpha=0.3)
    
    # 3. Cost Breakdown
    ax3 = plt.subplot(2, 3, 3)
    costs = results['cost_data']['initial_costs']
    # Simplify cost categories for better visualization
    simplified_costs = {
        'Storage Tank': costs['storage_tank'],
        'Piping & Gutters': costs['piping'] + costs['gutters_downspouts'],
        'Filtration System': costs['filtration'] + costs.get('uv_sterilizer', 0),
        'Installation': costs['installation'],
        'Other': costs.get('first_flush_diverter', 0) + costs.get('pump_system', 0)
    }
    
    # Remove zero values
    simplified_costs = {k: v for k, v in simplified_costs.items() if v > 0}
    
    wedges, texts, autotexts = ax3.pie(simplified_costs.values(), labels=simplified_costs.keys(), 
                                      autopct='%1.1f%%', startangle=90)
    ax3.set_title(f"Initial Cost Breakdown\n(Total: ₹{results['cost_data']['total_initial']:,.0f})", 
                  fontweight="bold", fontsize=12)
    
    # 4. Financial Analysis Over Time
    ax4 = plt.subplot(2, 3, 4)
    years = range(0, 21)
    
    # Simplified cash flow calculation
    initial_cost = results['cost_data']['total_initial']
    annual_net_benefit = results['annual_savings_future'] - results['cost_data']['total_annual']
    
    cash_flows = [-initial_cost] + [annual_net_benefit * (1.08 ** year) for year in range(1, 21)]
    cumulative = np.cumsum(cash_flows)
    
    ax4.plot(years, cumulative, 'g-', linewidth=2, label='Cumulative Cash Flow')
    ax4.axhline(y=0, color='r', linestyle='--', alpha=0.5, label='Break-even')
    ax4.fill_between(years, cumulative, 0, where=(np.array(cumulative) > 0), 
                     color='green', alpha=0.2, label='Profit Zone')
    ax4.fill_between(years, cumulative, 0, where=(np.array(cumulative) < 0), 
                     color='red', alpha=0.2, label='Investment Zone')
    
    ax4.set_xlabel('Years')
    ax4.set_ylabel('Amount (₹)')
    ax4.set_title('Financial Performance Over Time', fontweight="bold", fontsize=12)
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3)
    
    # Format y-axis labels in lakhs for better readability
    ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x/100000:.1f}L' if abs(x) >= 100000 else f'₹{x/1000:.0f}K'))
    
    # 5. Environmental Impact
    ax5 = plt.subplot(2, 3, 5)
    env_impact = results['environmental_impact']
    
    impact_metrics = {
        'Water Saved\n(Thousands L)': env_impact['water_saved_liters'] / 1000,
        'Energy Saved\n(kWh)': env_impact['energy_saved_kwh'],
        'CO₂ Reduced\n(kg)': env_impact['co2_reduction_kg'],
        'Trees Equivalent': env_impact['equivalent_trees']
    }
    
    bars = ax5.bar(range(len(impact_metrics)), impact_metrics.values(), 
                   color=['blue', 'green', 'brown', 'darkgreen'], alpha=0.7)
    ax5.set_title('Annual Environmental Benefits', fontweight="bold", fontsize=12)
    ax5.set_xticks(range(len(impact_metrics)))
    ax5.set_xticklabels(impact_metrics.keys(), fontsize=9, rotation=45, ha='right')
    
    # Add value labels on bars
    for bar, value in zip(bars, impact_metrics.values()):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.1f}', ha='center', va='bottom', fontsize=9)
    
    # 6. Future Rainfall Trend
    ax6 = plt.subplot(2, 3, 6)
    if forecast_df is not None:
        months_future = forecast_df['Month'][:12]  # Next 12 months
        rainfall_future = forecast_df['Predicted_Rainfall_mm'][:12]
        confidence = forecast_df['Confidence'][:12]
        
        # Color bars based on confidence
        colors = ['darkblue' if c == 'High' else 'blue' if c == 'Medium' else 'lightblue' 
                  for c in confidence]
        
        ax6.bar(range(len(months_future)), rainfall_future, color=colors, alpha=0.7)
        ax6.set_title('Next 12 Months Rainfall Forecast', fontweight="bold", fontsize=12)
        ax6.set_ylabel('Predicted Rainfall (mm)')
        ax6.set_xticks(range(len(months_future)))
        ax6.set_xticklabels([m.split()[0][:3] for m in months_future], rotation=45)
        
        # Add confidence legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor='darkblue', alpha=0.7, label='High Confidence'),
                          Patch(facecolor='blue', alpha=0.7, label='Medium Confidence'),
                          Patch(facecolor='lightblue', alpha=0.7, label='Low Confidence')]
        ax6.legend(handles=legend_elements, fontsize=8)
        ax6.grid(axis="y", alpha=0.3)
    else:
        ax6.text(0.5, 0.5, 'Weather forecast\ndata unavailable', 
                ha='center', va='center', transform=ax6.transAxes, fontsize=12)
        ax6.set_title('Future Rainfall Forecast', fontweight="bold", fontsize=12)
    
    plt.tight_layout()
    return fig

def assess_feasibility(results):
    """Calculate enhanced feasibility score with future predictions"""
    score = 0
    weights = {
        'rainfall': 15,
        'harvest': 15,
        'coverage': 15,
        'economic': 25,
        'payback': 15,
        'future_trend': 15
    }
    
    # Historical rainfall adequacy
    historical_rainfall = results['annual_rainfall_historical']
    if historical_rainfall >= 800:  # Good for Indian conditions
        score += weights['rainfall']
    elif historical_rainfall >= 500:
        score += weights['rainfall'] * 0.7
    elif historical_rainfall >= 300:
        score += weights['rainfall'] * 0.4
    
    # Harvest potential
    historical_harvest = results['annual_harvest_historical']
    if historical_harvest >= 25:
        score += weights['harvest']
    elif historical_harvest >= 15:
        score += weights['harvest'] * 0.7
    elif historical_harvest >= 8:
        score += weights['harvest'] * 0.4
    
    # Coverage potential (use better of historical or future)
    coverage = max(results['historical_coverage'], results.get('future_coverage', 0))
    if coverage >= 60:
        score += weights['coverage']
    elif coverage >= 40:
        score += weights['coverage'] * 0.7
    elif coverage >= 20:
        score += weights['coverage'] * 0.4
    
    # Economic viability
    bcr = results['financial_metrics']['benefit_cost_ratio']
    if bcr >= 1.3:
        score += weights['economic']
    elif bcr >= 1.0:
        score += weights['economic'] * 0.7
    elif bcr >= 0.8:
        score += weights['economic'] * 0.4
    
    # Payback period
    payback = results['financial_metrics']['payback_period']
    if payback and payback <= 8:  # Adjusted for Indian market
        score += weights['payback']
    elif payback and payback <= 12:
        score += weights['payback'] * 0.7
    elif payback and payback <= 18:
        score += weights['payback'] * 0.4
    
    # Future trend assessment
    future_harvest = results.get('annual_harvest_future', 0)
    if future_harvest > historical_harvest * 1.1:  # 10% improvement
        score += weights['future_trend']
    elif future_harvest > historical_harvest * 0.95:  # Stable
        score += weights['future_trend'] * 0.7
    elif future_harvest > historical_harvest * 0.8:  # Slight decline
        score += weights['future_trend'] * 0.4
    
    return min(100, score)

def calculate_recharge_structures_enhanced(annual_harvest, soil_type, rainfall_pattern=None):
    """Enhanced recharge structure calculations for Indian conditions"""
    # Get soil properties
    soil_props = SOIL_PERMEABILITY.get(soil_type, SOIL_PERMEABILITY["Unknown"])
    recharge_volume = annual_harvest * RECHARGE_FACTOR
    effective_volume = recharge_volume * soil_props["factor"]
    
    # Adjust design based on infiltration rate and Indian conditions
    infiltration_rate = soil_props["infiltration_rate"]  # mm/hr
    
    # Enhanced calculations for Indian monsoon patterns
    if rainfall_pattern and rainfall_pattern.get('monsoon_intensity', 'normal') == 'high':
        sizing_factor = 1.3  # Larger structures for intense monsoons
    else:
        sizing_factor = 1.0
    
    # Recharge Pit calculations (optimized for Indian conditions)
    if infiltration_rate < 5:  # Low permeability (common in Deccan plateau)
        pit_depth = 4.5 * sizing_factor
        pit_diameter = (effective_volume * 4 / (3.14 * pit_depth)) ** 0.5
        filter_layers = ["Coarse sand", "Fine gravel", "Coarse gravel"]
    elif infiltration_rate > 20:  # High permeability (coastal areas)
        pit_depth = 3.0 * sizing_factor
        pit_diameter = (effective_volume * 4 / (3.14 * pit_depth)) ** 0.5
        filter_layers = ["Fine sand", "Coarse sand"]
    else:  # Medium permeability
        pit_depth = 3.5 * sizing_factor
        pit_diameter = (effective_volume * 4 / (3.14 * pit_depth)) ** 0.5
        filter_layers = ["Fine sand", "Coarse sand", "Fine gravel"]
    
    pit_volume = 3.14 * (pit_diameter/2) ** 2 * pit_depth
    
    # Recharge Trench calculations (popular in urban India)
    trench_depth = 2.5 * sizing_factor if infiltration_rate < 10 else 2.0 * sizing_factor
    trench_width = 2.0 if infiltration_rate < 5 else 1.5
    trench_length = effective_volume / (trench_depth * trench_width)
    trench_volume = trench_length * trench_width * trench_depth
    
    # Percolation Tank calculations (common in Maharashtra, Karnataka)
    tank_depth = 3.0 * sizing_factor
    tank_area = effective_volume / tank_depth
    tank_diameter = (tank_area * 4 / 3.14) ** 0.5
    tank_volume = tank_area * tank_depth
    
    # Injection Well calculations (for urban areas with space constraints)
    well_depth = 15.0 if infiltration_rate < 5 else 10.0  # Deeper for clay soils
    well_diameter = 0.3  # Standard 300mm diameter
    well_volume = 3.14 * (well_diameter/2) ** 2 * well_depth
    
    # Cost calculations in INR (updated for Indian market)
    base_cost_per_m3 = {
        'pit': 12000,        # ₹12,000 per m³
        'trench': 8000,      # ₹8,000 per m³
        'tank': 15000,       # ₹15,000 per m³
        'well': 25000       # ₹25,000 per m³
    }
    
    # Soil-specific cost adjustments
    soil_cost_multiplier = {
        'Sandy': 0.9,
        'Sandy Loam': 1.0,
        'Loam': 1.1,
        'Clay Loam': 1.3,
        'Clay': 1.5,
        'Silt': 1.2
    }.get(soil_type, 1.0)
    
    # Calculate costs for each structure
    structures = {
        "recharge_pit": {
            "volume": pit_volume,
            "diameter": pit_diameter,
            "depth": pit_depth,
            "filter_layers": filter_layers,
            "cost": pit_volume * base_cost_per_m3['pit'] * soil_cost_multiplier,
            "maintenance_annual": pit_volume * base_cost_per_m3['pit'] * soil_cost_multiplier * 0.03
        },
        "recharge_trench": {
            "volume": trench_volume,
            "length": trench_length,
            "width": trench_width,
            "depth": trench_depth,
            "cost": trench_volume * base_cost_per_m3['trench'] * soil_cost_multiplier,
            "maintenance_annual": trench_volume * base_cost_per_m3['trench'] * soil_cost_multiplier * 0.02
        },
        "percolation_tank": {
            "volume": tank_volume,
            "diameter": tank_diameter,
            "depth": tank_depth,
            "area": tank_area,
            "cost": tank_volume * base_cost_per_m3['tank'] * soil_cost_multiplier,
            "maintenance_annual": tank_volume * base_cost_per_m3['tank'] * soil_cost_multiplier * 0.04
        },
        "injection_well": {
            "volume": well_volume,
            "diameter": well_diameter,
            "depth": well_depth,
            "cost": well_depth * base_cost_per_m3['well'] * soil_cost_multiplier,
            "maintenance_annual": well_depth * base_cost_per_m3['well'] * soil_cost_multiplier * 0.05
        }
    }
    
    # Determine recommended structure based on conditions
    if effective_volume < 8:
        recommended = "recharge_pit"
        recommendation_reason = "Small volume, cost-effective solution"
    elif soil_type in ["Clay", "Clay Loam"] and effective_volume > 20:
        recommended = "injection_well"
        recommendation_reason = "Clay soil requires deep injection for effective recharge"
    elif effective_volume > 40:
        recommended = "percolation_tank"
        recommendation_reason = "Large volume best handled by percolation tank"
    elif infiltration_rate > 15:
        recommended = "recharge_trench"
        recommendation_reason = "Good infiltration rate suitable for trench system"
    else:
        recommended = "recharge_pit"
        recommendation_reason = "Standard solution for moderate volumes"
    
    return {
        "structures": structures,
        "recommended_structure": recommended,
        "recommendation_reason": recommendation_reason,
        "annual_recharge_potential": effective_volume,
        "soil_infiltration_rate": infiltration_rate,
        "soil_suitability": "High" if infiltration_rate > 15 else "Medium" if infiltration_rate > 5 else "Low",
        "total_estimated_cost": structures[recommended]["cost"],
        "annual_maintenance_cost": structures[recommended]["maintenance_annual"],
        "groundwater_recharge_benefit": effective_volume * 0.8  # 80% reaches groundwater
    }

def generate_comprehensive_report(location, results, soil_data, monsoon_forecast, recharge_data):
    """Generate comprehensive analysis report"""
    
    report = f"""
# COMPREHENSIVE RAINWATER HARVESTING FEASIBILITY REPORT
**Location:** {location.address if location else 'Unknown'}
**Analysis Date:** {datetime.now().strftime('%B %d, %Y')}
**Coordinates:** {location.latitude:.4f}°N, {location.longitude:.4f}°E

## EXECUTIVE SUMMARY
**Feasibility Score:** {assess_feasibility(results):.0f}/100
**System Type Recommended:** {results['system_type'].title()}
**Investment Required:** ₹{results['cost_data']['total_initial']:,.0f}
**Annual Savings Potential:** ₹{results['annual_savings_future']:,.0f}
**Payback Period:** {results['financial_metrics']['payback_period'] or 'N/A'} years

## RAINFALL ANALYSIS
### Historical Data (2019-2023 Average)
- **Annual Rainfall:** {results['annual_rainfall_historical']:.0f} mm
- **Water Harvest Potential:** {results['annual_harvest_historical']:.1f} m³/year
- **Dry Months:** {results['dry_months_historical']} months (rainfall < 30mm)

### Future Predictions (Next 12 Months)
- **Predicted Annual Rainfall:** {results['annual_rainfall_future']:.0f} mm
- **Predicted Water Harvest:** {results['annual_harvest_future']:.1f} m³/year
- **Expected Dry Months:** {results['dry_months_future']} months
"""

    if monsoon_forecast:
        report += f"""
### Monsoon Forecast (IMD Style)
- **Seasonal Rainfall:** {monsoon_forecast['seasonal_rainfall_percent']:.0f}% of normal
- **Monsoon Onset:** {monsoon_forecast['monsoon_onset_date']}
- **Monsoon Withdrawal:** {monsoon_forecast['monsoon_withdrawal_date']}
- **Heavy Rainfall Days:** {monsoon_forecast['heavy_rainfall_days']} days expected
- **Drought Risk:** {monsoon_forecast['drought_risk']}
- **Flood Risk:** {monsoon_forecast['flood_risk']}
"""

    report += f"""
## WATER DEMAND ANALYSIS
- **Drinking Water Need:** {results['drinking_demand']:.1f} m³/year
- **Domestic Use Need:** {results['domestic_demand']:.1f} m³/year
- **Garden Irrigation Need:** {results['garden_demand']:.1f} m³/year
- **Total Annual Demand:** {results['total_demand']:.1f} m³/year

## SYSTEM COVERAGE
- **Historical Coverage:** {results['historical_coverage']:.1f}% of total demand
- **Future Predicted Coverage:** {results.get('future_coverage', 0):.1f}% of total demand
- **Recommended Storage Capacity:** {results['recommended_storage']:.1f} m³

## FINANCIAL ANALYSIS
### Investment Details
- **Total Initial Investment:** ₹{results['cost_data']['total_initial']:,.0f}
- **Annual Operating Cost:** ₹{results['cost_data']['total_annual']:,.0f}
- **Water Source Cost:** ₹{results['water_cost_per_m3']}/m³ ({results['water_source']} supply)

### Financial Returns
- **Net Present Value (20 years):** ₹{results['financial_metrics']['npv']:,.0f}
- **Internal Rate of Return:** {results['financial_metrics']['irr']*100:.1f}% per annum
- **Benefit-Cost Ratio:** {results['financial_metrics']['benefit_cost_ratio']:.2f}
- **Simple Payback Period:** {results['financial_metrics']['payback_period'] or 'N/A'} years
- **Discounted Payback Period:** {results['financial_metrics']['discounted_payback'] or 'N/A'} years

## SOIL ANALYSIS
**Soil Type:** {soil_data['type']} ({soil_data['confidence']} confidence)
**Source:** {soil_data['source']}
**Infiltration Rate:** {recharge_data['soil_infiltration_rate']} mm/hour
**Groundwater Recharge Suitability:** {recharge_data['soil_suitability']}
"""

    if soil_data.get('raw_classification'):
        report += f"**Detailed Classification:** {soil_data['raw_classification']}\n"

    report += f"""
## GROUNDWATER RECHARGE POTENTIAL
**Annual Recharge Volume:** {recharge_data['annual_recharge_potential']:.1f} m³
**Recommended Structure:** {recharge_data['recommended_structure'].replace('_', ' ').title()}
**Reason:** {recharge_data['recommendation_reason']}
**Estimated Cost:** ₹{recharge_data['total_estimated_cost']:,.0f}
**Annual Maintenance:** ₹{recharge_data['annual_maintenance_cost']:,.0f}

### Recharge Structure Options:
"""

    for structure_name, details in recharge_data['structures'].items():
        structure_title = structure_name.replace('_', ' ').title()
        report += f"""
**{structure_title}:**
- Volume: {details['volume']:.1f} m³
- Cost: ₹{details['cost']:,.0f}
- Annual Maintenance: ₹{details['maintenance_annual']:,.0f}
"""
        
        if 'diameter' in details:
            report += f"- Diameter: {details['diameter']:.1f} m, Depth: {details['depth']:.1f} m\n"
        elif 'length' in details:
            report += f"- Length: {details['length']:.1f} m, Width: {details['width']:.1f} m, Depth: {details['depth']:.1f} m\n"

    report += f"""
## ENVIRONMENTAL IMPACT
**Annual Benefits:**
- Water Conservation: {results['environmental_impact']['water_saved_liters']:,.0f} liters
- Energy Savings: {results['environmental_impact']['energy_saved_kwh']:.0f} kWh
- CO₂ Reduction: {results['environmental_impact']['co2_reduction_kg']:.0f} kg
- Equivalent to: {results['environmental_impact']['equivalent_trees']:.0f} trees planted
- Vehicle Emissions Saved: {results['environmental_impact']['equivalent_car_km']:,.0f} km of car travel

## RECOMMENDATIONS

### Primary Recommendation
"""

    feasibility_score = assess_feasibility(results)
    if feasibility_score >= 70:
        recommendation = "**HIGHLY RECOMMENDED** - Excellent feasibility with strong financial returns"
    elif feasibility_score >= 50:
        recommendation = "**RECOMMENDED** - Good feasibility with reasonable returns"
    elif feasibility_score >= 30:
        recommendation = "**CONDITIONALLY RECOMMENDED** - Moderate feasibility, consider optimization"
    else:
        recommendation = "**NOT RECOMMENDED** - Poor feasibility under current conditions"

    report += f"{recommendation}\n\n"

    # Add specific recommendations based on analysis
    report += "### Specific Recommendations:\n"
    
    if results['financial_metrics']['benefit_cost_ratio'] >= 1.2:
        report += "- Strong economic case - proceed with implementation\n"
    elif results['financial_metrics']['benefit_cost_ratio'] >= 1.0:
        report += "- Economically viable - consider government subsidies to improve returns\n"
    else:
        report += "- Consider smaller system or wait for water prices to increase\n"
    
    if results['historical_coverage'] < 30:
        report += "- System will supplement, not replace existing water supply\n"
        report += "- Focus on non-potable uses initially\n"
    
    if results['dry_months_historical'] > 6:
        report += f"- Large storage capacity essential due to {results['dry_months_historical']} dry months\n"
        report += "- Consider groundwater recharge to build reserves\n"
    
    if recharge_data['soil_suitability'] == 'Low':
        report += "- Soil conditions challenging - enhanced filtration required\n"
        report += "- Consider soil improvement or alternative recharge methods\n"
    
    report += f"""
### Implementation Timeline
**Phase 1 (Months 1-2):** Detailed site survey and permits
**Phase 2 (Months 2-4):** System installation
**Phase 3 (Month 4):** Testing and commissioning
**Phase 4 (Ongoing):** Monitoring and maintenance

### Government Incentives (Check Current Schemes)
- State/Central subsidies for rainwater harvesting
- Property tax rebates for RWH systems
- Building approval benefits
- CSR funding opportunities for community projects

## TECHNICAL SPECIFICATIONS
**System Type:** {results['system_type'].title()}
**Storage Capacity:** {results['recommended_storage']:.1f} m³
**Collection Area:** Roof area considered
**Collection Efficiency:** {EFFICIENCY*100:.0f}%

### Cost Breakdown:
"""

    for component, cost in results['cost_data']['initial_costs'].items():
        if cost > 0:
            report += f"- {component.replace('_', ' ').title()}: ₹{cost:,.0f}\n"

    report += f"""
**Total Initial Cost:** ₹{results['cost_data']['total_initial']:,.0f}
**Annual Operating Cost:** ₹{results['cost_data']['total_annual']:,.0f}

---
*This report is generated based on available meteorological data and standard design practices. 
Actual performance may vary based on local conditions, maintenance practices, and implementation quality.
For detailed engineering design, consult with certified water management professionals.*

**Generated by:** Enhanced Rainwater Harvesting Analysis System
**Report Version:** 2.0 - Indian Market Edition
"""

    return report

# Add these functions to your rainwater_utils.py file

def calculate_avoided_tanker_costs(annual_savings, intensity='medium'):
    """Calculate avoided water tanker costs based on regional patterns"""
    tanker_cost_factors = {
        'low': 0.1,      # Areas with good municipal supply
        'medium': 0.3,   # Areas with intermittent supply
        'high': 0.6      # Areas heavily dependent on tankers
    }
    return annual_savings * tanker_cost_factors.get(intensity, 0.3)

def calculate_gardening_benefits(annual_savings, household_size):
    """Calculate gardening and food security benefits"""
    base_benefit = household_size * 2000  # ₹2000 per person for homegrown vegetables
    return min(base_benefit, annual_savings * 0.4)  # Cap at 40% of water savings

def calculate_property_value_benefit(roof_area, location_type='medium'):
    """Calculate property value increase due to RWH system"""
    value_increase_factors = {
        'urban': 150,      # ₹150 per m² of roof area
        'medium': 100,     # ₹100 per m² 
        'rural': 50        # ₹50 per m²
    }
    annual_value = roof_area * value_increase_factors.get(location_type, 100)
    return annual_value * 0.05  # 5% annual benefit of increased value

def calculate_infrastructure_savings(area_type, roof_area):
    """Calculate community infrastructure savings"""
    if area_type == 'urban':
        return roof_area * 25  # ₹25 per m² annual infrastructure savings
    elif area_type == 'suburban':
        return roof_area * 15  # ₹15 per m²
    else:
        return roof_area * 10  # ₹10 per m²

def create_comprehensive_financial_chart(financial_metrics, results):
    """Create detailed financial performance chart with all benefits visualized"""
    import matplotlib.pyplot as plt
    import numpy as np
    
    years = list(range(0, financial_metrics['analysis_period'] + 1))
    # Handle case where yearly_analysis might not exist in older implementations
    if 'yearly_analysis' in financial_metrics:
        cumulative = [-financial_metrics.get('total_costs_pv', 0)] + [year_data['cumulative'] for year_data in financial_metrics['yearly_analysis']]
    else:
        # Fallback for simpler financial metrics
        initial_cost = results['cost_data']['total_initial']
        cumulative = [-initial_cost]
        running_total = -initial_cost
        for year in range(1, financial_metrics['analysis_period'] + 1):
            annual_net = results.get('annual_savings_historical', 0) * (1.08 ** year) - results['cost_data']['total_annual']
            running_total += annual_net
            cumulative.append(running_total)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Chart 1: Cumulative Cash Flow
    ax1.plot(years, cumulative, 'b-', linewidth=3, label='Cumulative Net Benefits')
    ax1.axhline(y=0, color='red', linestyle='-', alpha=0.7, label='Break-even Line')
    
    # Add payback period marker
    if financial_metrics.get('payback_period') is not None:
        payback_year = int(financial_metrics['payback_period'])
        if payback_year < len(cumulative):
            ax1.axvline(x=payback_year, color='green', linestyle='--', alpha=0.7, 
                       label=f'Payback: Year {payback_year}')
            ax1.plot(payback_year, cumulative[payback_year], 'go', markersize=8)
    
    # Color areas for investment vs return phases
    ax1.fill_between(years, cumulative, 0, where=np.array(cumulative) >= 0, 
                    color='green', alpha=0.2, label='Return Phase')
    ax1.fill_between(years, cumulative, 0, where=np.array(cumulative) < 0, 
                    color='orange', alpha=0.2, label='Investment Phase')
    
    ax1.set_xlabel('Years')
    ax1.set_ylabel('Cumulative Net Benefits (₹)')
    ax1.set_title('Comprehensive Financial Performance Over Time')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x/100000:.1f}L' if abs(x) >= 100000 else f'₹{x/1000:.0f}K'))
    
    # Chart 2: Benefit Breakdown (first year)
    annual_water_savings = results.get('annual_savings_future', results.get('annual_savings_historical', 0))
    roof_area = 100  # Default, should be passed as parameter
    household_size = 4  # Default, should be passed as parameter
    
    benefit_categories = {
        'Water Bill Savings': annual_water_savings,
        'Sewage Charge Savings': annual_water_savings * 0.7,
        'Avoided Tanker Costs': calculate_avoided_tanker_costs(annual_water_savings, 'medium'),
        'Gardening Benefits': calculate_gardening_benefits(annual_water_savings, household_size),
        'Property Value Increase': calculate_property_value_benefit(roof_area, 'medium'),
        'Infrastructure Savings': calculate_infrastructure_savings('urban', roof_area)
    }
    
    # Remove zero or very small benefits
    benefit_categories = {k: v for k, v in benefit_categories.items() if v > 1000}
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'][:len(benefit_categories)]
    
    if benefit_categories:
        wedges, texts, autotexts = ax2.pie(benefit_categories.values(), labels=benefit_categories.keys(), 
                                          autopct='%1.1f%%', colors=colors, startangle=90)
        
        # Enhance text readability
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
            
        ax2.set_title('First Year Benefit Breakdown', fontsize=14, fontweight='bold')
    else:
        ax2.text(0.5, 0.5, 'Insufficient benefit data\nfor visualization', 
                ha='center', va='center', transform=ax2.transAxes, fontsize=12)
        ax2.set_title('First Year Benefit Breakdown', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    return fig

# Main analysis function
def analyze_rainwater_harvesting(address, roof_area, household_size, garden_area=0, water_source="municipal"):
    """Main function to perform comprehensive rainwater harvesting analysis"""
    
    print(f"Analyzing rainwater harvesting feasibility for: {address}")
    
    # Get location
    location = get_location(address)
    if not location:
        return None, "Could not find location"
    
    print(f"Location found: {location.latitude:.4f}°N, {location.longitude:.4f}°E")
    
    # Get soil data
    soil_data = get_soil_type(location.latitude, location.longitude)
    print(f"Soil type: {soil_data['type']}")
    
    # Fetch rainfall data
    print("Fetching historical rainfall data...")
    historical_df, yearly_data = fetch_historical_rainfall_data(location.latitude, location.longitude)
    if historical_df is None:
        return None, "Could not fetch rainfall data"
    
    # Fetch weather forecast
    print("Generating weather forecast...")
    forecast_df = fetch_weather_forecast_data(location.latitude, location.longitude)
    
    # Get monsoon forecast
    print("Generating monsoon forecast...")
    monsoon_forecast = fetch_imd_monsoon_forecast(location.latitude, location.longitude)
    
    # Calculate water metrics
    print("Calculating water metrics...")
    results = calculate_water_metrics(historical_df, forecast_df, roof_area, 
                                    household_size, garden_area, water_source)
    
    # Calculate recharge structures
    print("Designing recharge structures...")
    recharge_data = calculate_recharge_structures_enhanced(
        results['annual_harvest_historical'], soil_data['type']
    )
    
    # Create visualizations
    print("Creating visualizations...")
    chart = create_comprehensive_charts(historical_df, forecast_df, results)
    
    # Generate report
    print("Generating comprehensive report...")
    report = generate_comprehensive_report(location, results, soil_data, 
                                         monsoon_forecast, recharge_data)
    
    return {
        'location': location,
        'historical_data': historical_df,
        'forecast_data': forecast_df,
        'monsoon_forecast': monsoon_forecast,
        'results': results,
        'soil_data': soil_data,
        'recharge_data': recharge_data,
        'chart': chart,
        'report': report,
        'feasibility_score': assess_feasibility(results)
    }, None

# Example usage
if __name__ == "__main__":
    # Example analysis
    analysis_data, error = analyze_rainwater_harvesting(
        address="Mumbai, Maharashtra, India",
        roof_area=150,  # m²
        household_size=4,
        garden_area=50,  # m²
        water_source="municipal"  # or "tanker" or "borewell"
    )
    
    if analysis_data:
        print("Analysis completed successfully!")
        print(f"Feasibility Score: {analysis_data['feasibility_score']:.0f}/100")
        print("\nReport Preview:")
        print(analysis_data['report'][:500] + "...")
        
        # Show the chart
        plt.show()
    else:
        print(f"Analysis failed: {error}")
