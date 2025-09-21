# rainwater_pipeline.py
import warnings
warnings.filterwarnings('ignore')

from crewai import Agent, Task, Crew
from pydantic import BaseModel
from typing import Optional, Dict
import os
from dotenv import load_dotenv
import asyncio

# ------------------ Load environment variables ------------------
load_dotenv()  # loads OPENAI_API_KEY from .env
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key is None:
    raise ValueError("OPENAI_API_KEY not found in environment!")

os.environ["OPENAI_API_KEY"] = openai_api_key
os.environ["OPENAI_MODEL_NAME"] = "gpt-4o-mini"

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

# ------------------ Agents ------------------
calculation_agent = Agent(
    role='Calculation Expert',
    goal='Compute runoff, tank size, dimensions, overflow, and cost locally without LLM.',
    backstory='Hydrology and civil engineer.',
    verbose=True,
    allow_delegation=False,
    tools=[]
)

design_agent = Agent(
    role='Design Specialist',
    goal='Recommend tank type, material, dimensions using simple logic.',
    backstory='Civil engineering design logic.',
    verbose=True,
    allow_delegation=False,
    tools=[]
)

recommendation_agent = Agent(
    role='Recommendation Advisor',
    goal='Generate human-readable suggestions using LLM.',
    backstory='Smart AI assistant for detailed explanations.',
    verbose=True,
    allow_delegation=True,
    tools=[]
)

report_agent = Agent(
    role='Report Generator',
    goal='Create JSON or text report using results.',
    backstory='Formats outputs into readable report.',
    verbose=True,
    allow_delegation=False,
    tools=[]
)

# ------------------ Tasks ------------------
calculation_task = Task(
    description="Compute runoff volume, recommended tank volume, overflow, cost.",
    expected_output="Calculated tank_volume, cost_estimate, overflow.",
    human_input=False,
    output_json=CalculationResult,
    output_file=None,
    agent=calculation_agent
)

design_task = Task(
    description="Recommend tank type, material, and dimensions based on tank_volume.",
    expected_output="DesignRecommendation",
    human_input=False,
    output_json=DesignRecommendation,
    output_file=None,
    agent=design_agent
)

recommendation_task = Task(
    description="Generate human-readable recommendations based on calculation and design results.",
    expected_output="RecommendationReport",
    human_input=False,
    output_json=RecommendationReport,
    output_file=None,
    agent=recommendation_agent
)

report_task = Task(
    description="Compile all results into final report.",
    expected_output="FinalReport",
    human_input=False,
    output_json=FinalReport,
    output_file=None,
    agent=report_agent
)

# ------------------ Crew ------------------
rainwater_harvesting_crew = Crew(
    agents=[calculation_agent, design_agent, recommendation_agent, report_agent],
    tasks=[calculation_task, design_task, recommendation_task, report_task],
    verbose=True
)

# ------------------ Pipeline Function ------------------
async def run_rainwater_pipeline(roof_area, rainfall_mm, soil_type, budget):
    # Prepare input
    input_data = {
        'roof_area': roof_area,
        'rainfall_mm': rainfall_mm,
        'soil_type': soil_type,
        'budget': budget
    }

    # ------------------ Compute Calculation & Design Locally ------------------
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

    design_recommendation = DesignRecommendation(
        tank_type="Ferrocement",
        material="Cement+Mesh",
        dimensions={"length": 5.0, "width": 3.0, "height": 3.0}
    )

    # ------------------ Use LLM Only for Human-readable Text ------------------
    results = await rainwater_harvesting_crew.kickoff_async(inputs={
        'calculation_result': calculation_result.dict(),
        'design_recommendation': design_recommendation.dict(),
        'input_data': input_data
    })

    return results
