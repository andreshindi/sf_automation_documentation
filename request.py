##testing call to ollama

import requests
import json

def stream_ollama(model: str, prompt: str):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }

    with requests.post(url, json=payload, stream=True) as response:
        for line in response.iter_lines():
            if line:
                data = line.decode("utf-8")
                if data.strip() == "": continue
                token = json.loads(data).get("response", "")
                print(token, end="", flush=True)