# ONNX Deployment Project (PyTorch → Quantization → ONNX → Flask API)

This mini-project shows the full path from **training** to **serving** a model in production style.
It is designed for learning and classroom demos.

## What you will build

You will build a complete deployment workflow:

1. Train a PyTorch model.
2. Quantize it to make it smaller and faster.
3. Export it to ONNX (framework-independent format).
4. Serve predictions through a Flask REST API.
5. Call the API from a client script.

---

## Why this matters in production

When you move from notebook experiments to real applications, you hit practical constraints:

- **Model size**: Large files are slow to ship and expensive to store.
- **Inference speed**: Slow predictions hurt user experience and throughput.
- **Framework lock-in**: A model tied only to PyTorch is harder to integrate into mixed stacks.
- **Service integration**: Applications need HTTP endpoints, not local Python objects.

This project addresses all four.

---

## Project structure

```text
onnx_deployment_project/
├── README.md
├── requirements.txt
├── train_model.py
├── optimize_and_export.py
├── api_server.py
├── client.py
└── artifacts/
```

> `artifacts/` is created automatically after scripts run.

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r onnx_deployment_project/requirements.txt
```

---

## Step 1: Train a baseline PyTorch model

Run:

```bash
python onnx_deployment_project/train_model.py
```

What this script does:

- Generates synthetic binary classification data.
- Trains a simple feedforward network.
- Prints progress every 5 epochs.
- Saves model weights to:
  - `onnx_deployment_project/artifacts/credit_risk_model.pt`

---

## Step 2: Quantize and export to ONNX

Run:

```bash
python onnx_deployment_project/optimize_and_export.py
```

What this script does:

- Loads baseline weights.
- Applies **dynamic quantization** to `nn.Linear` layers.
- Saves quantized weights.
- Exports ONNX model.
- Prints an optimization report with:
  - Baseline vs quantized size
  - Baseline vs quantized accuracy
  - Baseline vs quantized latency

Artifacts produced:

- `onnx_deployment_project/artifacts/credit_risk_model_quantized.pt`
- `onnx_deployment_project/artifacts/credit_risk_model.onnx`

### Trade-offs explained simply

- Quantization usually **reduces model size** and can **speed up inference**.
- In some cases, accuracy drops slightly.
- You should measure size, latency, and accuracy together before shipping.

---

## Step 3: Start the Flask API server

Run:

```bash
python onnx_deployment_project/api_server.py
```

Server endpoint:

- `GET /health` → service status
- `POST /predict` → returns prediction

### Request format

```json
{
  "features": [0.82, -1.10, 0.25, -0.70, 1.45, -0.30, 0.15, 0.90]
}
```

### Response format

```json
{
  "prediction": 1,
  "probability": 0.9132,
  "label": "high_risk"
}
```

---

## Step 4: Run the client script

In a second terminal (while server is running), run:

```bash
python onnx_deployment_project/client.py
```

The client sends one sample payload and prints API response.

---

## Learning objective mapping

This project directly supports the requested objectives:

1. **Production challenges**: discussed in README and reflected in optimization/service design.
2. **Quantization**: applied and compared via size/speed/accuracy report.
3. **ONNX conversion**: model exported into platform-agnostic ONNX file.
4. **REST API serving**: Flask app exposes health + predict endpoints.
5. **Client integration**: client script consumes deployed model over HTTP.

---

## Notes for extension

If you want to make this even more production-like, next steps are:

- Add request schema validation with Pydantic.
- Add batch prediction endpoint.
- Add Dockerfile and containerized deployment.
- Add structured logging and monitoring metrics.
- Add automated tests for endpoint behavior.

