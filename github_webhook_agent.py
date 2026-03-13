from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
from openai import OpenAI

# --------------------------------
# LOAD ENV VARIABLES
# --------------------------------

load_dotenv()

MCP_URL = os.getenv("MCP_URL")
TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

GRAFANA_RW_URL = os.getenv("GRAFANA_RW_URL")
GRAFANA_USERNAME = os.getenv("GRAFANA_USERNAME")
GRAFANA_API_KEY = os.getenv("GRAFANA_API_KEY")
K6_SCRIPT = os.getenv("K6_SCRIPT", "script.js")

SFCC_SITE_URL = os.getenv("SFCC_SITE_URL")

JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

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
# RUN K6 + PUSH METRICS TO GRAFANA
# --------------------------------

def run_k6():

    try:

        print("\nRunning k6 performance test\n")

        os.environ["K6_PROMETHEUS_RW_SERVER_URL"] = GRAFANA_RW_URL
        os.environ["K6_PROMETHEUS_RW_USERNAME"] = GRAFANA_USERNAME
        os.environ["K6_PROMETHEUS_RW_PASSWORD"] = GRAFANA_API_KEY

        os.environ["SFCC_SITE_URL"] = SFCC_SITE_URL

        print("Testing SFCC site:", SFCC_SITE_URL)

        cmd = f'k6 run -o experimental-prometheus-rw {K6_SCRIPT}'

        os.system(cmd)

        return {"status": "k6 test executed"}

    except Exception as e:

        print("k6 Error:", str(e))
        return {"error": str(e)}

# --------------------------------
# PERFORMANCE TESTS
# --------------------------------

def run_tests():

    print("\nStarting Performance Tests\n")

    k6 = run_k6()

    speedcurve = call_tool("speedcurve")

    datadog = call_tool("datadog_metrics")

    return {
        "k6": k6,
        "speedcurve": speedcurve,
        "datadog": datadog
    }


# --------------------------------
# ROOT CAUSE DATA
# --------------------------------

def run_rca():

    print("\nRunning Root Cause Data Collection\n")

    commits = call_tool("github_commits")

    return commits



def create_jira_ticket(summary, description):

    try:

        url = f"{JIRA_URL}/rest/api/3/issue"

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        auth = (JIRA_EMAIL, JIRA_API_TOKEN)

        payload = {
            "fields": {
                "project": {
                    "key": JIRA_PROJECT_KEY
                },
                "summary": summary,
                "description": description,
                "issuetype": {
                    "name": "Bug"
                }
            }
        }

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            auth=auth
        )

        print("\nJIRA Ticket Created\n", response.json())

        return response.json()

    except Exception as e:

        print("JIRA Error:", str(e))
        return {"error": str(e)}
# --------------------------------
# AI ROOT CAUSE ANALYSIS
# --------------------------------

def ai_analysis(data):

    try:

        print("\nRunning AI Root Cause Analysis\n")

        prompt = f"""
You are a senior performance engineer.

Analyze this system performance data and GitHub commits.

Explain:

1) Is there any performance regression?
2) What could be the root cause?
3) Which system component might be responsible?
4) What should developers fix?

Data:
{data}
"""

        response = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[
                {
                    "role": "system",
                    "content": "You are a performance engineering expert."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.2
        )

        ai_result = response.choices[0].message.content

        print("\nAI ANALYSIS RESULT\n")
        print(ai_result)

        return ai_result

    except Exception as e:

        print("AI Error:", str(e))
        return {"error": str(e)}


# --------------------------------
# MAIN AGENT
# --------------------------------

def run_agent():

    perf_data = run_tests()

    infra_data = run_rca()

    combined_data = {
        "performance": perf_data,
        "infra": infra_data
    }

    ai_result = ai_analysis(combined_data)

    jira_ticket = create_jira_ticket(
             "Performance Regression Detected",
        ai_result
)

    result = {
        "performance": perf_data,
        "infra": infra_data,
        "ai_analysis": ai_result,
        "jira": jira_ticket
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
            "message": "AI Agent Executed",
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