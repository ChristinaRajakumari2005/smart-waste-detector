import os
import base64
import json
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "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")
PROMPT = """You are a smart waste classifier. Look at the image and classify it.

Respond ONLY in this exact JSON format, nothing else:
{
  "material": "name of the material or object",
  "classification": "BIODEGRADABLE or NON-BIODEGRADABLE",
  "confidence": 85,
  "explanation": "one sentence why",
  "disposal_tip": "how to dispose of it"
}

Rules:
- Paper, cardboard, food, wood, leaves, cotton = BIODEGRADABLE
- Plastic, glass, metal, styrofoam = NON-BIODEGRADABLE
"""

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image_file = request.files["image"]
    image_data = image_file.read()
    image_base64 = base64.standard_b64encode(image_data).decode("utf-8")
    content_type = image_file.content_type or "image/jpeg"

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/auto",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{content_type};base64,{image_base64}"
                                }
                            },
                            {
                                "type": "text",
                                "text": PROMPT
                            }
                        ]
                    }
                ],
                "max_tokens": 500
            }
        )

        raw = response.json()
        print(raw)
        if "choices" not in raw:
            return jsonify({"error": str(raw)}), 500
        response_text = raw["choices"][0]["message"]["content"].strip()

        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]

        result = json.loads(response_text)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)