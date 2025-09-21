# Rainwater Harvesting Feasibility Analysis System

## Overview
A comprehensive Streamlit-based web application for analyzing the feasibility of rainwater harvesting systems in India. The application integrates multiple government APIs and performs detailed technical, financial, and environmental assessments to provide actionable insights for rainwater harvesting implementation.

## Features
- **Real-time Government Data Integration**: Fetches authentic data from Indian government sources
- **Comprehensive Feasibility Analysis**: Technical, financial, and environmental assessment
- **Government Scheme Integration**: Automatic subsidy calculation and eligibility checking
- **Interactive Visualizations**: Charts, graphs, and maps for data presentation
- **Detailed Reports**: Downloadable CSV and text reports
- **20-year Financial Projections**: Complete ROI and payback analysis

## APIs and Data Sources

### Primary APIs Used
- **Indian Meteorological Department (IMD) API**
  - Endpoint: `https://api.data.gov.in/resource/...`
  - Purpose: Historical rainfall data, precipitation patterns
  - Data: Monthly rainfall, annual totals, rainy days count

- **Soil Health Card Database API**
  - Endpoint: `https://soilhealth.dac.gov.in/api/...`
  - Purpose: Soil type classification and properties
  - Data: Soil infiltration rates, pH levels, organic carbon content

- **Central Ground Water Board (CGWB) API**
  - Endpoint: `https://cgwb.gov.in/webservice/...`
  - Purpose: Groundwater level and quality data
  - Data: Water table depth, aquifer characteristics, recharge rates

- **OpenStreetMap Nominatim API**
  - Endpoint: `https://nominatim.openstreetmap.org/search`
  - Purpose: Geocoding addresses to latitude/longitude
  - Data: Coordinate conversion for location-based queries

### Government Schemes Database
- **State-wise Subsidy Information**
  - Source: Manual compilation from official government portals
  - Coverage: All Indian states and union territories
  - Data: Subsidy percentages, maximum amounts, eligibility criteria

## Core Calculations and Formulas

### 1. Water Harvesting Potential
```
Annual Harvest (L) = Roof Area (m²) × Annual Rainfall (mm) × Runoff Coefficient × System Efficiency
Monthly Harvest (L) = Roof Area (m²) × Monthly Rainfall (mm) × Runoff Coefficient × System Efficiency
```

**Variables:**
- Roof Area: User input in square meters
- Rainfall: From IMD API in millimeters
- Runoff Coefficient: Calculated based on roof material and soil type
- System Efficiency: User configurable (70-95%), default 85%

### 2. Runoff Coefficient Calculation
```
Runoff Coefficient = Base Roof Coefficient × Soil Adjustment Factor
```

**Roof Material Coefficients:**
- Concrete: 0.85
- Metal: 0.90
- Tiled: 0.80
- Thatched: 0.60
- Asbestos: 0.85
- Slate: 0.88

**Soil Adjustment Factors:**
- Sandy: 0.95 (high infiltration)
- Clay: 1.05 (low infiltration)
- Loamy: 1.00 (moderate infiltration)
- Rocky: 1.10 (very low infiltration)

### 3. Financial Analysis Formulas

#### Cost Breakdown Calculation
```
Total Project Cost = Collection System + Treatment System + Recharge System + Installation + Contingency
```

**Component Calculations:**
- Collection System = (Roof Area × 150) + 15000 + 8000 + (Storage Capacity × 25)
- Treatment System = 12000 + 18000 + 25000
- Recharge System = Excavation + Filter Media + Piping + Structure
- Installation = Labor + Electrical + Testing + Permits
- Contingency = 10% of Subtotal

#### Payback Analysis
```
Annual Water Savings (₹) = Annual Harvest (L) × Water Rate (₹/L)
Annual Maintenance (₹) = Total Cost × Maintenance Rate
Net Annual Benefit (₹) = Annual Savings - Annual Maintenance
Payback Period (years) = Total Investment ÷ Net Annual Benefit
```

#### Net Present Value (NPV)
```
NPV = Σ(Net Annual Benefit ÷ (1 + Discount Rate)^year) - Initial Investment
```
- Discount Rate: 8% (standard for infrastructure projects)
- Analysis Period: 20 years

### 4. Feasibility Score Algorithm
```
Feasibility Score = (Soil Score × 0.25) + (Rainfall Score × 0.30) + (Depth Score × 0.20) + 
                   (Area Score × 0.15) + (Runoff Score × 0.10)
```

**Individual Score Calculations:**
- Soil Score: (Soil Suitability ÷ 10) × 100
- Rainfall Score: min(100, Annual Rainfall ÷ 15)
- Depth Score: max(0, 100 - (Water Table Depth × 3))
- Area Score: min(100, Roof Area ÷ 2)
- Runoff Score: Runoff Coefficient × 100

### 5. Recharge Structure Sizing
```
Structure Volume (m³) = (Peak Monthly Rainfall × Roof Area × Runoff Coefficient) ÷ 1000
Filter Bed Area (m²) = Structure Volume ÷ 2
Required Depth (m) = max(3, min(8, Water Table Depth × 0.6))
```

### 6. Subsidy Calculation
```
Actual Subsidy (₹) = min(Project Cost × (Subsidy % ÷ 100), Maximum Subsidy Amount)
Net Investment (₹) = Total Project Cost - Actual Subsidy
```

## Technical Methodologies

### Data Processing Pipeline
1. **Address Geocoding**: Convert user address to coordinates using Nominatim API
2. **Concurrent API Calls**: Fetch rainfall, soil, and groundwater data simultaneously
3. **Data Validation**: Check API responses for completeness and accuracy
4. **Fallback Mechanisms**: Use regional averages if specific location data unavailable
5. **Caching**: Store API responses in session state to avoid repeated calls

### Error Handling Strategies
- **API Timeout Management**: 30-second timeout with retry logic
- **Data Quality Checks**: Validate numerical ranges and data types
- **Graceful Degradation**: Provide estimates when APIs are unavailable
- **User Feedback**: Clear error messages and alternative suggestions

### Visualization Techniques
- **Interactive Charts**: Plotly for dynamic rainfall and cost visualizations
- **Gauge Charts**: Soil suitability and feasibility score displays
- **Financial Projections**: Multi-subplot charts for cash flow analysis
- **Comparison Charts**: Before/after subsidy impact visualization

## Installation and Setup

### Prerequisites
- Python 3.8+
- Streamlit 1.25+
- Required packages (see requirements.txt)

### Dependencies
```
streamlit>=1.25.0
pandas>=1.5.0
plotly>=5.15.0
matplotlib>=3.6.0
numpy>=1.24.0
requests>=2.28.0
```

### Environment Variables
- `IMD_API_KEY`: Indian Meteorological Department API key
- `SOIL_API_KEY`: Soil Health API access token
- `CGWB_API_KEY`: Central Ground Water Board API key

### Running the Application
```bash
pip install -r requirements.txt
streamlit run app.py
```

## File Structure
```
├── app.py                 # Main Streamlit application
├── data_fetcher.py        # API integration and data processing
├── requirements.txt       # Python dependencies
├── config.py             # Configuration settings
└── README.md             # This documentation
```

## Key Classes and Functions

### DataFetcher Class
- `get_rainfall_data()`: Fetch IMD rainfall data
- `get_soil_type()`: Retrieve soil characteristics
- `get_groundwater_data()`: Access CGWB groundwater information
- `get_government_schemes()`: Load state-wise subsidy schemes
- `calculate_runoff_coefficient()`: Compute runoff based on materials

### Calculation Functions
- `calculate_harvesting_potential()`: Water harvest estimation
- `calculate_detailed_cost_breakdown()`: Complete cost analysis
- `calculate_payback_analysis()`: Financial projections
- `calculate_feasibility_score()`: Overall viability assessment

### Utility Functions
- `get_lat_lon_from_address()`: Geocoding service
- `validate_api_response()`: Data quality assurance
- `format_currency()`: Indian currency formatting

## Performance Optimizations
- **Session State Management**: Cache API responses to reduce load times
- **Lazy Loading**: Load visualizations only when tabs are accessed
- **Efficient Data Structures**: Use pandas DataFrames for large datasets
- **Minimal API Calls**: Batch requests where possible

## Limitations and Considerations
- **API Dependencies**: Requires active internet connection and API availability
- **Data Accuracy**: Dependent on government data quality and update frequency
- **Regional Variations**: Some calculations use generalized formulas
- **Cost Estimates**: Based on 2024 market rates, may require updates
- **Regulatory Changes**: Government schemes and subsidies subject to policy changes

## Future Enhancements
- **Machine Learning Integration**: Predictive modeling for rainfall patterns
- **IoT Sensor Integration**: Real-time monitoring capabilities
- **Mobile Application**: React Native or Flutter mobile version
- **Community Features**: User reviews and implementation photos
- **Advanced Analytics**: Comparative analysis across regions

## Contributing
- Follow PEP 8 coding standards
- Include unit tests for new functions
- Update documentation for API changes
- Test with multiple Indian locations before submitting

## License
MIT License - See LICENSE file for details

## Support and Documentation
- **Technical Issues**: Create GitHub issues with detailed descriptions
- **API Questions**: Refer to individual government API documentation
- **Feature Requests**: Use GitHub discussions for community input

## Disclaimer
This application provides estimates based on available government data and standard engineering formulas. Actual implementation should involve consultation with certified professionals and compliance with local regulations. The developers are not responsible for implementation decisions based solely on this analysis.
