from flask import Flask, jsonify
import requests

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"   # change only if you used a different working model

@app.route("/")
def test():
    payload = {
        "model": MODEL,
        "prompt": "Say hello in one sentence",
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    result = response.json()

    return jsonify({"ollama_response": result["response"]})

if __name__ == "__main__":
    app.run(debug=True)
