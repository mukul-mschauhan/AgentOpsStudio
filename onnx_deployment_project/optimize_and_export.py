"""Step 2: Quantize a PyTorch model and export to ONNX."""

from __future__ import annotations

import time
from pathlib import Path

import torch
import torch.nn as nn


ARTIFACT_DIR = Path("onnx_deployment_project/artifacts")
BASELINE_PATH = ARTIFACT_DIR / "credit_risk_model.pt"
QUANTIZED_PATH = ARTIFACT_DIR / "credit_risk_model_quantized.pt"
ONNX_PATH = ARTIFACT_DIR / "credit_risk_model.onnx"


class CreditRiskNet(nn.Module):
    def __init__(self, input_dim: int = 8) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


def synthetic_eval_data(samples: int = 800, features: int = 8) -> tuple[torch.Tensor, torch.Tensor]:
    torch.manual_seed(42)
    x = torch.randn(samples, features)
    weights = torch.tensor([1.2, -0.7, 0.8, -1.1, 0.6, -0.4, 0.3, 0.9])
    logits = x @ weights + 0.2 * torch.randn(samples)
    y = (logits > 0.0).float().unsqueeze(1)
    return x, y


def accuracy(model: nn.Module, x: torch.Tensor, y: torch.Tensor) -> float:
    model.eval()
    with torch.no_grad():
        pred = (torch.sigmoid(model(x)) > 0.5).float()
    return (pred == y).float().mean().item()


def latency_ms(model: nn.Module, x: torch.Tensor, repeats: int = 300) -> float:
    model.eval()
    with torch.no_grad():
        _ = model(x)
        start = time.perf_counter()
        for _ in range(repeats):
            _ = model(x)
        end = time.perf_counter()
    return ((end - start) / repeats) * 1000


def export_onnx(quantized_model: nn.Module, input_dim: int = 8) -> None:
    dummy_input = torch.randn(1, input_dim)
    torch.onnx.export(
        quantized_model,
        dummy_input,
        ONNX_PATH,
        input_names=["features"],
        output_names=["logits"],
        dynamic_axes={"features": {0: "batch_size"}, "logits": {0: "batch_size"}},
        opset_version=13,
    )


def main() -> None:
    if not BASELINE_PATH.exists():
        raise FileNotFoundError(
            "Baseline model not found. Run train_model.py first to create artifacts."
        )

    model = CreditRiskNet(input_dim=8)
    model.load_state_dict(torch.load(BASELINE_PATH, map_location="cpu"))

    quantized_model = torch.quantization.quantize_dynamic(
        model,
        {nn.Linear},
        dtype=torch.qint8,
    )

    torch.save(quantized_model.state_dict(), QUANTIZED_PATH)
    export_onnx(quantized_model)

    x_eval, y_eval = synthetic_eval_data()
    baseline_acc = accuracy(model, x_eval, y_eval)
    quantized_acc = accuracy(quantized_model, x_eval, y_eval)

    single_batch = torch.randn(1, 8)
    baseline_latency = latency_ms(model, single_batch)
    quantized_latency = latency_ms(quantized_model, single_batch)

    baseline_size_kb = BASELINE_PATH.stat().st_size / 1024
    quantized_size_kb = QUANTIZED_PATH.stat().st_size / 1024

    print("\nOptimization Report")
    print("-" * 50)
    print(f"Baseline model size:   {baseline_size_kb:.2f} KB")
    print(f"Quantized model size:  {quantized_size_kb:.2f} KB")
    print(f"Baseline accuracy:     {baseline_acc:.4f}")
    print(f"Quantized accuracy:    {quantized_acc:.4f}")
    print(f"Baseline latency:      {baseline_latency:.3f} ms/request")
    print(f"Quantized latency:     {quantized_latency:.3f} ms/request")
    print(f"ONNX model saved to:   {ONNX_PATH}")


if __name__ == "__main__":
    main()
