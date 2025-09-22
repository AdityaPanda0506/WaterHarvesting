
# rainwater_pipeline.py
import warnings
warnings.filterwarnings('ignore')

from pydantic import BaseModel
from typing import Optional, Dict
import os
from dotenv import load_dotenv
from openai import OpenAI
import asyncio

# ------------------ Load environment variables ------------------
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key is None:
    raise ValueError("OPENAI_API_KEY not found in environment!")

client = OpenAI(api_key=openai_api_key)

# ------------------ Pydantic Models ------------------
class InputData(BaseModel):
    roof_area: float
    rainfall_mm: float
    soil_type: str
    budget: float

class CalculationResult(BaseModel):
    tank_volume: Optional[float] = None
    cost_estimate: Optional[float] = None
    overflow: Optional[float] = None

class DesignRecommendation(BaseModel):
    tank_type: Optional[str] = None
    material: Optional[str] = None
    dimensions: Optional[Dict[str, float]] = None

class RecommendationReport(BaseModel):
    text: Optional[str] = None

class FinalReport(BaseModel):
    input_data: Optional[InputData] = None
    calculation_result: Optional[CalculationResult] = None
    design_recommendation: Optional[DesignRecommendation] = None
    recommendation_report: Optional[RecommendationReport] = None

# ------------------ Pipeline Function ------------------
async def run_rainwater_pipeline(roof_area, rainfall_mm, soil_type, budget):
    # Step 1: Input data
    input_data = InputData(
        roof_area=roof_area,
        rainfall_mm=rainfall_mm,
        soil_type=soil_type,
        budget=budget
    )

    # Step 2: Local Calculations (fast, no LLM)
    runoff_coeff = 0.8 if soil_type != 'rocky' else 0.5
    runoff_volume = roof_area * rainfall_mm * runoff_coeff
    tank_volume = min(runoff_volume, budget * 0.3)  # simple cost constraint
    cost_estimate = tank_volume * 3  # dummy cost per liter
    overflow = max(runoff_volume - tank_volume, 0)

    calculation_result = CalculationResult(
        tank_volume=tank_volume,
        cost_estimate=cost_estimate,
        overflow=overflow
    )

    # Step 3: Local Design Logic
    design_recommendation = DesignRecommendation(
        tank_type="Ferrocement",
        material="Cement+Mesh",
        dimensions={"length": 5.0, "width": 3.0, "height": 3.0}
    )

    # Step 4: Use LLM for final human-readable recommendation
    prompt = f"""
    Based on the following data, generate clear recommendations for rainwater harvesting:

    Input Data: {input_data.dict()}
    Calculation Result: {calculation_result.dict()}
    Design Recommendation: {design_recommendation.dict()}

    Write a short, practical, and human-friendly explanation of the system and its benefits.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a civil engineer and sustainability expert."},
            {"role": "user", "content": prompt}
        ]
    )

    report_text = response.choices[0].message.content

    recommendation_report = RecommendationReport(text=report_text)

    # Step 5: Compile final report
    final_report = FinalReport(
        input_data=input_data,
        calculation_result=calculation_result,
        design_recommendation=design_recommendation,
        recommendation_report=recommendation_report
    )

    return final_report
