"""Step 4: Client script that calls the Flask REST API."""

from __future__ import annotations

import requests


API_URL = "http://127.0.0.1:8000/predict"


def main() -> None:
    sample_features = [0.82, -1.10, 0.25, -0.70, 1.45, -0.30, 0.15, 0.90]
    response = requests.post(API_URL, json={"features": sample_features}, timeout=10)

    print(f"Status code: {response.status_code}")
    print("Response JSON:")
    print(response.json())


if __name__ == "__main__":
    main()
