import requests
import os
from dotenv import load_dotenv

load_dotenv()

MCP_URL = os.getenv("MCP_URL")
TOKEN = os.getenv("TOKEN")

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

def call_tool(tool):

    body = {
        "tool": tool
    }

    r = requests.post(MCP_URL, json=body, headers=headers)

    return r.json()


def run_performance_analysis():

    # Run performance tools
    k6 = call_tool("k6_test")
    speedcurve = call_tool("speedcurve")

    # Combine results
    data = {
        "k6": k6,
        "speedcurve": speedcurve
    }

    print("\nPerformance Analysis Result\n")
    print(data)


if __name__ == "__main__":
    run_performance_analysis()