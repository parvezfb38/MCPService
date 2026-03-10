import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ai_root_cause(data):

    prompt = f"""
You are a senior performance engineer.

Analyze the performance regression and find the root cause.

Data:
{data}

Explain:
- what failed
- possible root cause
- recommended fix
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content