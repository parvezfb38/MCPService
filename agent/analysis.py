import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_results(data):

    prompt = f"""
You are a performance engineer AI.

Analyze this performance data and detect regression.

Data:
{data}

Explain:
1) Is there regression?
2) What is the possible root cause?
3) What should engineers fix?
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content