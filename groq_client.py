import os
import requests
from typing import Dict, Any

class GroqClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def send_request(self, prompt: str, model: str = "llama-3.3-70b-versatile", temperature: float = 0.7) -> Dict[str, Any]:
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature
        }

        try:
            response = requests.post(self.url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "type": type(e).__name__
            }

# Example usage
if __name__ == "__main__":
    api_key = os.getenv("GROQ_API_KEY")
    client = GroqClient(api_key)
    prompt = "You are a hotel concierge. What restaurants would you recommend for Italian food?"
    result = client.send_request(prompt)
    print(result)