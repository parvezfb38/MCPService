import requests
import os
from dotenv import load_dotenv
from analysis import analyze_results

load_dotenv()

MCP_URL = os.getenv("MCP_URL")
TOKEN = os.getenv("TOKEN")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


def call_tool(tool):

    body = {
        "tool": tool
    }

    try:
        r = requests.post(MCP_URL, json=body, headers=headers)
        return r.json()

    except Exception as e:
        return {"error": str(e)}


def run_performance_analysis():

    print("\nStarting Performance Tests\n")

    # Run tools
    k6 = call_tool("k6_test")
    speedcurve = call_tool("speedcurve")

    # Combine results
    data = {
        "k6": k6,
        "speedcurve": speedcurve
    }

    print("\nPerformance Analysis Result\n")
    print(data)

    print("\nRunning AI Root Cause Analysis...\n")

    try:
        ai_report = analyze_results(data)

        print("\nAI RCA Result\n")
        print(ai_report)

    except Exception as e:
        print("AI Analysis Error:", e)


if __name__ == "__main__":
    run_performance_analysis()