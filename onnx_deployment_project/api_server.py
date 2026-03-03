"""Step 3: Serve ONNX model with Flask + ONNX Runtime."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import onnxruntime as ort
from flask import Flask, jsonify, request


MODEL_PATH = Path("onnx_deployment_project/artifacts/credit_risk_model.onnx")

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        "ONNX model not found. Run optimize_and_export.py first to create it."
    )

session = ort.InferenceSession(str(MODEL_PATH), providers=["CPUExecutionProvider"])
input_name = session.get_inputs()[0].name

app = Flask(__name__)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


@app.get("/health")
def health_check():
    return jsonify({"status": "ok", "model": MODEL_PATH.name})


@app.post("/predict")
def predict():
    payload = request.get_json(silent=True)

    if not payload or "features" not in payload:
        return jsonify({"error": "Send JSON with a 'features' list."}), 400

    features = payload["features"]
    if not isinstance(features, list) or len(features) != 8:
        return jsonify({"error": "'features' must be a list of 8 numbers."}), 400

    try:
        model_input = np.array([features], dtype=np.float32)
    except Exception:
        return jsonify({"error": "Invalid values in 'features'."}), 400

    logits = session.run(None, {input_name: model_input})[0]
    probability = float(sigmoid(logits)[0][0])
    prediction = int(probability >= 0.5)

    return jsonify(
        {
            "prediction": prediction,
            "probability": round(probability, 4),
            "label": "high_risk" if prediction == 1 else "low_risk",
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
