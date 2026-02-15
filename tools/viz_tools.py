from __future__ import annotations

from typing import Dict, List, Tuple

import pandas as pd
import plotly.express as px


def suggest_charts(df: pd.DataFrame) -> List[Dict]:
    charts: List[Dict] = []
    numeric = df.select_dtypes(include="number").columns.tolist()
    if len(numeric) >= 1:
        charts.append({"title": f"Distribution of {numeric[0]}", "type": "histogram", "cols": [numeric[0]]})
    if len(numeric) >= 2:
        charts.append({"title": f"{numeric[0]} vs {numeric[1]}", "type": "scatter", "cols": [numeric[0], numeric[1]]})
    if not charts:
        categorical = df.select_dtypes(exclude="number").columns.tolist()
        if categorical:
            charts.append({"title": f"Top {categorical[0]} categories", "type": "bar", "cols": [categorical[0]]})
    return charts


def render_chart(df: pd.DataFrame, chart_spec: Dict):
    ctype = chart_spec.get("type")
    cols = chart_spec.get("cols", [])
    title = chart_spec.get("title", "Chart")
    if ctype == "histogram" and cols:
        return px.histogram(df, x=cols[0], title=title)
    if ctype == "scatter" and len(cols) >= 2:
        return px.scatter(df, x=cols[0], y=cols[1], title=title)
    if ctype == "bar" and cols:
        counts = df[cols[0]].value_counts().head(10).reset_index()
        counts.columns = [cols[0], "count"]
        return px.bar(counts, x=cols[0], y="count", title=title)
    return None
