import os
from openai import OpenAI

# Initialize client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def review_code(diff):

    prompt = f"""
You are a senior DevOps engineer.

Review the following code diff and:

- Identify bugs
- Suggest improvements
- Highlight security risks

Code:

{diff}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert DevOps reviewer"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()


if __name__ == "__main__":

    with open("diff.txt", "r") as f:
        diff = f.read()

    review = review_code(diff)

    with open("review.txt", "w") as f:
        f.write(review)
