import os
import json
from datetime import datetime
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not set")

client = OpenAI(api_key=api_key)


# ----------------------------
# Get JSON files
# ----------------------------

def get_trivy_files():

    files = []

    for f in os.listdir("."):
        if f.startswith("trivy-") and f.endswith(".json"):
            files.append(f)

    if not files:
        raise Exception("No Trivy json reports found")

    files.sort()  # important

    print("Reports included:", files)

    return files


# ----------------------------
# Parse vulnerability counts
# ----------------------------

def parse_json_summary(filename):

    with open(filename, "r") as f:
        data = json.load(f)

    critical = 0
    high = 0
    medium = 0

    for result in data.get("Results", []):

        for vuln in result.get("Vulnerabilities", []):

            sev = vuln.get("Severity")

            if sev == "CRITICAL":
                critical += 1

            elif sev == "HIGH":
                high += 1

            elif sev == "MEDIUM":
                medium += 1

    return critical, high, medium


# ----------------------------
# AI Analysis
# ----------------------------

def analyze_single_report(filename):

    critical, high, medium = parse_json_summary(filename)

    prompt = f"""
You are a senior DevSecOps engineer.

Analyze the container security posture.

Image File: {filename}

Vulnerability Summary:

CRITICAL: {critical}
HIGH: {high}
MEDIUM: {medium}

Tasks:

1. Assign overall risk level (LOW / MEDIUM / HIGH / CRITICAL)
2. Identify major security risks
3. Suggest remediation strategy
4. Recommend security best practices
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an expert container security reviewer."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return (
        critical,
        high,
        medium,
        response.choices[0].message.content
    )


# ----------------------------
# Build Final Report
# ----------------------------

def generate_final_report():

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    files = get_trivy_files()

    full_report = f"""
AI Security Review Summary
==========================

Scan Date: {timestamp}

Overall Security Assessment
---------------------------
"""

    total_critical = 0
    total_high = 0
    total_medium = 0

    for file in files:

        print(f"Analyzing {file}...")

        critical, high, medium, result = analyze_single_report(file)

        total_critical += critical
        total_high += high
        total_medium += medium

        full_report += f"""

====================================================
Report: {file}
====================================================

CRITICAL: {critical}
HIGH: {high}
MEDIUM: {medium}

{result}
"""

    full_report += f"""

====================================================
GLOBAL SUMMARY
====================================================

TOTAL CRITICAL: {total_critical}
TOTAL HIGH: {total_high}
TOTAL MEDIUM: {total_medium}

"""

    return full_report


# ----------------------------
# Main Execution
# ----------------------------

if __name__ == "__main__":

    final_report = generate_final_report()

    with open("ai-trivy-review.txt", "w") as f:
        f.write(final_report)

    print("ai-trivy-review.txt generated successfully")