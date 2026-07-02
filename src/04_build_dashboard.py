"""
04_build_dashboard.py
---------------------------------------------------
Builds a single, self-contained, interactive HTML dashboard (using Plotly)
summarizing the "Future of Data: Quantum Analytics" dataset.

Plotly.js is embedded directly in the file (not loaded from a CDN) so the
dashboard works fully offline - just double-click it to open in any browser.

Output: dashboard/quantum_analytics_dashboard.html
---------------------------------------------------
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

DATA_PATH = "/home/claude/Future-of-Data-Quantum-Analytics/dataset/cleaned_quantum_analytics_data.csv"
OUT_PATH = "/home/claude/Future-of-Data-Quantum-Analytics/dashboard/quantum_analytics_dashboard.html"

df = pd.read_csv(DATA_PATH, parse_dates=["announcement_date"])

# ---------------------------------------------------------
# Pre-aggregate the data needed for each panel
# ---------------------------------------------------------
kpi_total_records = len(df)
kpi_companies = df["company"].nunique()
kpi_max_qubits = df["qubit_count"].max()
kpi_commercial_rate = df["is_commercially_available"].mean() * 100
latest_funding = df.sort_values("announcement_date").groupby("company").tail(1)
kpi_total_funding = latest_funding["funding_raised_million_usd"].sum()
kpi_avg_error = df["gate_error_rate_pct"].mean()

yearly_tech_qubits = df.groupby(["year", "technology_type"])["qubit_count"].mean().reset_index()
pivot_qubits = yearly_tech_qubits.pivot(index="year", columns="technology_type", values="qubit_count").ffill()

latest_per_company = df.sort_values("announcement_date").groupby("company").tail(1).sort_values("qubit_count", ascending=False)

commercial_by_tech = (df.groupby("technology_type")["is_commercially_available"].mean() * 100).sort_values(ascending=False)

funding_by_country = latest_per_company.groupby("country")["funding_raised_million_usd"].sum().sort_values(ascending=False)

sector_counts = df["sector_focus"].value_counts()

yearly_err = df.groupby(["year", "technology_type"])["gate_error_rate_pct"].mean().reset_index()
pivot_err = yearly_err.pivot(index="year", columns="technology_type", values="gate_error_rate_pct").ffill()

# ---------------------------------------------------------
# Build the subplot grid
# ---------------------------------------------------------
fig = make_subplots(
    rows=3, cols=2,
    subplot_titles=(
        "Avg Qubit Count Growth by Technology (Log Scale)", "Latest Qubit Count by Company",
        "Commercial Availability Rate (%) by Technology", "Funding Raised by Country ($M)",
        "Application Sector Focus Distribution", "Gate Error Rate Trend by Technology"
    ),
    specs=[
        [{"type": "scatter"}, {"type": "bar"}],
        [{"type": "bar"}, {"type": "bar"}],
        [{"type": "domain"}, {"type": "scatter"}],
    ],
    vertical_spacing=0.11,
    horizontal_spacing=0.10,
)

palette = ["#4C6EF5", "#22B8CF", "#20C997", "#94D82D", "#FCC419",
           "#FF922B", "#FF6B6B", "#CC5DE8", "#845EF7", "#5C7CFA"]

# Panel 1: Qubit growth by technology (log scale line chart)
for i, tech in enumerate(pivot_qubits.columns):
    fig.add_trace(go.Scatter(x=pivot_qubits.index, y=pivot_qubits[tech],
                              mode="lines+markers", name=tech,
                              line=dict(width=2, color=palette[i % len(palette)]),
                              hovertemplate="%{x}<br>Avg Qubits: %{y:,.0f}<extra>" + tech + "</extra>"),
                  row=1, col=1)
fig.update_yaxes(type="log", row=1, col=1)

# Panel 2: Latest qubit count by company
fig.add_trace(go.Bar(x=latest_per_company["company"], y=latest_per_company["qubit_count"],
                      marker_color=palette, showlegend=False,
                      hovertemplate="%{x}<br>Qubits: %{y:,}<extra></extra>"),
              row=1, col=2)

# Panel 3: Commercial availability rate by technology
fig.add_trace(go.Bar(x=commercial_by_tech.index, y=commercial_by_tech.values,
                      marker_color="#20C997", showlegend=False,
                      hovertemplate="%{x}<br>Commercial Rate: %{y:.1f}%<extra></extra>"),
              row=2, col=1)

# Panel 4: Funding by country
fig.add_trace(go.Bar(x=funding_by_country.index, y=funding_by_country.values,
                      marker_color="#FF922B", showlegend=False,
                      hovertemplate="%{x}<br>Funding: $%{y:,.0f}M<extra></extra>"),
              row=2, col=2)

# Panel 5: Sector focus distribution (pie)
fig.add_trace(go.Pie(labels=sector_counts.index, values=sector_counts.values,
                      marker=dict(colors=palette), hole=0.45,
                      hovertemplate="%{label}<br>Records: %{value}<br>%{percent}<extra></extra>"),
              row=3, col=1)

# Panel 6: Gate error rate trend by technology
for i, tech in enumerate(pivot_err.columns):
    fig.add_trace(go.Scatter(x=pivot_err.index, y=pivot_err[tech],
                              mode="lines+markers", name=tech, showlegend=False,
                              line=dict(width=2, color=palette[i % len(palette)]),
                              hovertemplate="%{x}<br>Error Rate: %{y:.2f}%<extra>" + tech + "</extra>"),
                  row=3, col=2)

fig.update_layout(
    height=1400, width=1300,
    title=dict(text="Future of Data — Quantum Analytics Dashboard", x=0.5, font=dict(size=24)),
    template="plotly_white",
    legend=dict(orientation="h", yanchor="bottom", y=1.06, xanchor="center", x=0.5, font=dict(size=10)),
    margin=dict(t=130, l=60, r=60, b=60),
    font=dict(family="Segoe UI, Arial", size=12),
)
fig.update_xaxes(tickangle=-35, row=1, col=2)
fig.update_xaxes(tickangle=-20, row=2, col=2)

# ---------------------------------------------------------
# Build the KPI header
# ---------------------------------------------------------
plot_html = pio.to_html(fig, include_plotlyjs=True, full_html=False, config={"displaylogo": False})

kpi_cards = f"""
<div class="kpi-row">
  <div class="kpi-card"><div class="kpi-value">{kpi_total_records:,}</div><div class="kpi-label">Total Records</div></div>
  <div class="kpi-card"><div class="kpi-value">{kpi_companies}</div><div class="kpi-label">Companies Tracked</div></div>
  <div class="kpi-card"><div class="kpi-value">{kpi_max_qubits:,.0f}</div><div class="kpi-label">Max Qubit Count</div></div>
  <div class="kpi-card"><div class="kpi-value">{kpi_commercial_rate:.1f}%</div><div class="kpi-label">Commercial Availability Rate</div></div>
  <div class="kpi-card"><div class="kpi-value">${kpi_total_funding:,.0f}M</div><div class="kpi-label">Total Funding Raised</div></div>
  <div class="kpi-card"><div class="kpi-value">{kpi_avg_error:.2f}%</div><div class="kpi-label">Avg Gate Error Rate</div></div>
</div>
"""

html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Future of Data: Quantum Analytics Dashboard</title>
<style>
    body {{
        font-family: 'Segoe UI', Arial, sans-serif;
        background: linear-gradient(135deg, #f5f7fb 0%, #eef1f8 100%);
        margin: 0;
        padding: 24px;
        color: #1f2430;
    }}
    .header {{
        text-align: center;
        margin-bottom: 20px;
    }}
    .header h1 {{
        margin: 0;
        font-size: 28px;
        color: #2b2f3a;
    }}
    .header p {{
        color: #6b7280;
        margin-top: 6px;
    }}
    .kpi-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        justify-content: center;
        margin-bottom: 28px;
    }}
    .kpi-card {{
        background: white;
        border-radius: 14px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
        padding: 18px 26px;
        min-width: 150px;
        text-align: center;
        border-top: 4px solid #845EF7;
    }}
    .kpi-value {{
        font-size: 24px;
        font-weight: 700;
        color: #2b2f3a;
    }}
    .kpi-label {{
        font-size: 12px;
        color: #6b7280;
        margin-top: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .chart-container {{
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.07);
        padding: 10px;
        max-width: 1340px;
        margin: 0 auto;
    }}
    .footer {{
        text-align: center;
        color: #9aa1ad;
        font-size: 12px;
        margin-top: 20px;
    }}
</style>
</head>
<body>
    <div class="header">
        <h1>⚛️ Future of Data — Quantum Analytics Dashboard</h1>
        <p>Tracking period: {df['announcement_date'].min().date()} to {df['announcement_date'].max().date()} &nbsp;|&nbsp; Generated from cleaned_quantum_analytics_data.csv</p>
    </div>
    {kpi_cards}
    <div class="chart-container">
        {plot_html}
    </div>
    <div class="footer">Future of Data: Quantum Analytics Project &copy; 2026 — Interactive dashboard built with Plotly. Figures are illustrative/simulated, not real reported company data.</div>
</body>
</html>
"""

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"Interactive dashboard saved to: {OUT_PATH}")
