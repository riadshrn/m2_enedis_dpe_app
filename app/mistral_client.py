import requests
import os

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "BwW2Rlm3rbt58NOFOgzzVtIYEhbxw8gp")
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"

def get_interpretation(prompt: str):
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}
    payload = {
        "model": "mistral-small-latest",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }
    r = requests.post(MISTRAL_URL, headers=headers, json=payload)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]
