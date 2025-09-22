# govt_schemes_pipeline.py
import os
from dotenv import load_dotenv
from openai import OpenAI

# ------------------ Load environment variables ------------------
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key is None:
    raise ValueError("OPENAI_API_KEY not found in environment!")

client = OpenAI(api_key=openai_api_key)

# ------------------ Function to get schemes ------------------
def get_govt_schemes(state: str):
    prompt = f"""
    You are an expert on Indian government water conservation policies.

    Task: Provide a detailed list of government schemes, subsidies, and programs
    available in the state of {state} for rainwater harvesting structure implementation.

    For each scheme, include:
    - Scheme Name
    - Benefits (e.g., subsidies, grants, loans, tax benefits)
    - Eligibility criteria
    - How to apply (website links, forms, offices)
    - Contact details (official portals, helpline numbers, relevant departments)

    Keep the explanation clear, structured, and helpful for a citizen.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a government policy assistant for water management."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
