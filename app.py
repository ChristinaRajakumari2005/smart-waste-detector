import os
import base64
import json
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

genai.configure(api_key="AIzaSyCWUONBDjJK_St8ksmzNusduI7KSvddSuY")
model = genai.GenerativeModel("gemini-2.0-flash-lite")

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
        image_part = {
            "inline_data": {
                "mime_type": content_type,
                "data": image_base64
            }
        }

        response = model.generate_content([PROMPT, image_part])
        response_text = response.text.strip()

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