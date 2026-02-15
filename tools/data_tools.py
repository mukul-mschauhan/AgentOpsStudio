from __future__ import annotations

from io import BytesIO
from typing import Dict, List

import pandas as pd


def load_tabular_file(file_bytes: bytes, filename: str) -> pd.DataFrame:
    if filename.lower().endswith(".csv"):
        return pd.read_csv(BytesIO(file_bytes))
    if filename.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(BytesIO(file_bytes))
    raise ValueError("Unsupported file type. Please upload CSV or Excel.")


def profile_dataset(df: pd.DataFrame) -> Dict:
    missing = (df.isnull().sum() / max(len(df), 1)).round(3)
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    preview = df.head(8).to_dict(orient="records")
    return {
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "column_names": df.columns.tolist(),
        "numeric_cols": numeric_cols,
        "missing_ratio": missing[missing > 0].to_dict(),
        "preview": preview,
    }


def basic_findings(df: pd.DataFrame) -> List[str]:
    findings = [f"Dataset has {df.shape[0]} rows and {df.shape[1]} columns."]
    numeric = df.select_dtypes(include="number")
    if not numeric.empty:
        means = numeric.mean(numeric_only=True).sort_values(ascending=False)
        top_col = means.index[0]
        findings.append(f"Highest average metric is '{top_col}' at {means.iloc[0]:.2f}.")
        stds = numeric.std(numeric_only=True).sort_values(ascending=False)
        findings.append(f"Most volatile metric appears to be '{stds.index[0]}'.")
    else:
        findings.append("No numeric columns found; recommendations are based on categorical patterns.")
    dupes = int(df.duplicated().sum())
    findings.append(f"Detected {dupes} duplicate rows.")
    return findings


def detect_anomalies(df: pd.DataFrame) -> List[str]:
    anomalies: List[str] = []
    numeric = df.select_dtypes(include="number")
    for col in numeric.columns[:4]:
        q1 = numeric[col].quantile(0.25)
        q3 = numeric[col].quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        outliers = ((numeric[col] < q1 - 1.5 * iqr) | (numeric[col] > q3 + 1.5 * iqr)).sum()
        if outliers > 0:
            anomalies.append(f"{col}: {int(outliers)} potential outliers by IQR rule.")
    return anomalies or ["No severe anomalies detected with the quick IQR scan."]
