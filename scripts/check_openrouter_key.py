import requests
from config import OPEN_ROUTER_TOKEN

# Your OpenRouter API token
api_key = OPEN_ROUTER_TOKEN

# Endpoint (for DeepSeek model)
url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

data = {
    "model": "deepseek/deepseek-chat:free",
    "messages": [
        {"role": "user", "content": "Hello, who are you?"}
    ]
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
