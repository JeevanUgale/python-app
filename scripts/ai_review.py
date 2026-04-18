import os
from datetime import datetime
from openai import OpenAI

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not set")

client = OpenAI(api_key=api_key)


def read_trivy_reports():
    files = [
        "trivy-web.txt",
        "trivy-auth.txt",
        # "trivy-user.txt",
        # "trivy-admin.txt"
    ]

    combined_report = ""

    for file in files:
        if os.path.exists(file):
            with open(file, "r") as f:
                combined_report += f"\n\n===== {file} =====\n"
                combined_report += f.read()

    return combined_report[:12000]  # prevent token overflow


def analyze_trivy_report(report):

    prompt = f"""
You are a senior DevSecOps engineer.

Analyze the following Trivy vulnerability scan results.

Tasks:

1. Count CRITICAL, HIGH, MEDIUM vulnerabilities
2. Provide overall security risk level
3. Identify major risks
4. Suggest remediation steps
5. Recommend security best practices

Scan Output:

{report}
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

    return response.choices[0].message.content


def generate_summary(ai_output):

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    summary = f"""
AI Security Review Summary
==========================

Scan Date: {timestamp}

Overall Security Assessment
---------------------------

{ai_output}

End of Report
"""

    return summary


if __name__ == "__main__":

    report_data = read_trivy_reports()

    if not report_data:
        print("No Trivy reports found.")
        exit(1)

    ai_analysis = analyze_trivy_report(report_data)

    final_report = generate_summary(ai_analysis)

    with open("ai-review.txt", "w") as f:
        f.write(final_report)

    print("ai-review.txt generated successfully")