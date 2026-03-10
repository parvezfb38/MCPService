from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

# --------------------------------
# LOAD ENV VARIABLES
# --------------------------------

load_dotenv()

MCP_URL = os.getenv("MCP_URL")
TOKEN = os.getenv("TOKEN")

# --------------------------------
# FLASK APP
# --------------------------------

app = Flask(__name__)


# --------------------------------
# MCP TOOL CALL
# --------------------------------

def call_tool(tool):

    try:

        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        }

        body = {
            "tool": tool
        }

        response = requests.post(
            MCP_URL,
            headers=headers,
            json=body
        )

        data = response.json()

        print("\n-----------------------------")
        print("Tool:", tool)
        print("Response:", data)
        print("-----------------------------\n")

        return data

    except Exception as e:

        print("Tool Error:", str(e))

        return {"error": str(e)}


# --------------------------------
# PERFORMANCE TESTS
# --------------------------------

def run_tests():

    print("\nStarting Performance Tests\n")

    k6 = call_tool("k6_test")

    speedcurve = call_tool("speedcurve")

    grafana = call_tool("grafana_dashboards")

    datadog = call_tool("datadog_metrics")

    return {
        "k6": k6,
        "speedcurve": speedcurve,
        "grafana": grafana,
        "datadog": datadog
    }


# --------------------------------
# ROOT CAUSE CHECK
# --------------------------------

def run_rca():

    print("\nRunning Root Cause Analysis\n")

    commits = call_tool("github_commits")

    return commits


# --------------------------------
# MAIN AGENT
# --------------------------------

def run_agent():

    perf_data = run_tests()

    infra_data = run_rca()

    result = {
        "performance": perf_data,
        "infra": infra_data
    }

    print("\nFinal Agent Data:")
    print(result)

    return result


# --------------------------------
# GITHUB WEBHOOK
# --------------------------------

@app.route("/github-webhook", methods=["POST"])
def github_push():

    try:

        payload = request.json

        print("\n=================================")
        print("GitHub Push Detected")
        print("Payload:", payload)
        print("=================================\n")

        result = run_agent()

        return jsonify({
            "message": "Tests triggered",
            "result": result
        }), 200

    except Exception as e:

        print("Webhook Error:", str(e))

        return jsonify({
            "error": str(e)
        }), 500


# --------------------------------
# HEALTH CHECK
# --------------------------------

@app.route("/", methods=["GET"])
def home():

    return {
        "status": "AI Performance Agent Running"
    }


# --------------------------------
# MAIN
# --------------------------------

if __name__ == "__main__":

    print("\nAI Performance Webhook Agent Started\n")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )