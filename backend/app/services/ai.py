import json
import pandas as pd
from openai import OpenAI
import os

class AISemanticAnalyst:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def analyze_and_respond(self, user_query: str, dataset_path: str, profiling_summary: dict, target_lang: str = "en") -> dict:
        df = pd.read_csv(dataset_path) if dataset_path.endswith('.csv') else pd.read_excel(dataset_path)
        
        sample_context = df.head(5).to_dict(orient='records')
        schema = profiling_summary.get("schema", {})
        
        system_prompt = f"""
You are the lead execution analytical engine of DataPilot AI, processing dynamic business datasets for SMEs.
Analyze the target user dataset signature, data dimensions, and underlying schema structure configuration to address user inquiries.

Target Language for analysis: {target_lang} (Provide business responses in this specific language natively).

Metadata Footprint:
- Schema Definition: {json.dumps(schema)}
- Structural Profile Snapshot: {json.dumps(profiling_summary.get('descriptive_stats', {}))}
- Sample Records Data Model: {json.dumps(sample_context)}

CRITICAL COMPLIANCE EXPECTATION:
You must output a single, strictly formed JSON block using the template structure below. Do not prepend any text, do not append markdown, and do not embed trailing commas.

Required output structure:
{{
  "response_text": "Root cause business driver summary in requested language context...",
  "requires_visualization": true,
  "visualization_type": "bar", 
  "visualization_config": {{
    "xAxisKey": "column_name_x",
    "yAxisKey": "column_name_y",
    "data": [
      {{"column_name_x": "Category A", "column_name_y": 4500}},
      {{"column_name_x": "Category B", "column_name_y": 7200}}
    ]
  }},
  "strategic_recommendations": [
    "Concrete actionable data-driven execution step 1...",
    "Concrete actionable data-driven execution step 2..."
  ]
}}
"""
        response = self.client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0.1
        )
        
        return json.loads(response.choices[0].message.content)
