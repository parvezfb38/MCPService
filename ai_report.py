# ai_report.py

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env
load_dotenv()

# Get OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# Create OpenAI client
client = OpenAI(api_key=api_key)


def generate_ai_report(data):

    prompt = f"""
You are an AI performance engineer.

Analyze this performance regression data and provide:

1. Issue summary
2. Possible root cause
3. Recommendations to fix it

Performance Data:
{data}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a senior performance engineer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


# Sample regression data (from k6 parser)
sample_data = {
    "previous_latency": 300,
    "current_latency": 480,
    "latency_change_percent": 60.0,
    "previous_error_rate": 1.0,
    "current_error_rate": 3.0,
    "regression_detected": True
}


if __name__ == "__main__":

    print("\n==============================")
    print("AI PERFORMANCE REPORT")
    print("==============================\n")

    report = generate_ai_report(sample_data)

    print(report)