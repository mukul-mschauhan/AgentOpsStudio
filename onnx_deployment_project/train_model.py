"""Step 1: Train a simple PyTorch model and save weights.

This script uses synthetic data so anyone can run it quickly.
"""

from __future__ import annotations

from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


ARTIFACT_DIR = Path("onnx_deployment_project/artifacts")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


class CreditRiskNet(nn.Module):
    """Small MLP for binary classification."""

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


def make_synthetic_data(samples: int = 4000, features: int = 8) -> tuple[torch.Tensor, torch.Tensor]:
    """Create a synthetic binary classification dataset."""
    torch.manual_seed(42)
    x = torch.randn(samples, features)
    weights = torch.tensor([1.2, -0.7, 0.8, -1.1, 0.6, -0.4, 0.3, 0.9])
    logits = x @ weights + 0.2 * torch.randn(samples)
    y = (logits > 0.0).float().unsqueeze(1)
    return x, y


def train_model(epochs: int = 25, batch_size: int = 64) -> None:
    x, y = make_synthetic_data()

    train_size = int(0.8 * len(x))
    x_train, x_val = x[:train_size], x[train_size:]
    y_train, y_val = y[:train_size], y[train_size:]

    train_loader = DataLoader(TensorDataset(x_train, y_train), batch_size=batch_size, shuffle=True)

    model = CreditRiskNet(input_dim=x.shape[1])
    optimizer = torch.optim.Adam(model.parameters(), lr=0.003)
    loss_fn = nn.BCEWithLogitsLoss()

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        for batch_x, batch_y in train_loader:
            optimizer.zero_grad()
            logits = model(batch_x)
            loss = loss_fn(logits, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        if epoch % 5 == 0:
            model.eval()
            with torch.no_grad():
                val_logits = model(x_val)
                val_preds = (torch.sigmoid(val_logits) > 0.5).float()
                val_acc = (val_preds == y_val).float().mean().item()
            print(f"Epoch {epoch:02d} | loss={total_loss/len(train_loader):.4f} | val_acc={val_acc:.4f}")

    model_path = ARTIFACT_DIR / "credit_risk_model.pt"
    torch.save(model.state_dict(), model_path)
    print(f"Saved trained model to: {model_path}")


if __name__ == "__main__":
    train_model()
