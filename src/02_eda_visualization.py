"""
02_eda_visualization.py
---------------------------------------------------
Performs exploratory data analysis (EDA) on the cleaned quantum computing
industry dataset and saves a set of publication-ready charts to visuals/.

Charts produced:
    01_qubit_growth_by_technology.png     - Qubit count growth over time by technology type
    02_qubit_count_by_company.png         - Latest reported qubit count by company
    03_error_rate_trend.png               - Gate error rate improvement over time by technology
    04_funding_by_country.png             - Total funding raised by country
    05_commercial_availability_rate.png   - Commercial availability rate by technology type
    06_correlation_heatmap.png            - Correlation between numeric quantum metrics
    07_sector_focus_distribution.png      - Distribution of application sector focus
    08_quantum_volume_trend.png           - Quantum volume trend over time by technology
---------------------------------------------------
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

DATA_PATH = "/home/claude/Future-of-Data-Quantum-Analytics/dataset/cleaned_quantum_analytics_data.csv"
VISUALS_DIR = "/home/claude/Future-of-Data-Quantum-Analytics/visuals"

sns.set_theme(style="whitegrid", palette="viridis")
plt.rcParams["figure.dpi"] = 110
plt.rcParams["savefig.bbox"] = "tight"

df = pd.read_csv(DATA_PATH, parse_dates=["announcement_date"])

# ---------------------------------------------------------
# Chart 1: Qubit count growth over time by technology (log scale)
# ---------------------------------------------------------
yearly_tech = df.groupby(["year", "technology_type"])["qubit_count"].mean().reset_index()
pivot = yearly_tech.pivot(index="year", columns="technology_type", values="qubit_count")

plt.figure(figsize=(12, 6))
for tech in pivot.columns:
    plt.plot(pivot.index, pivot[tech], marker="o", markersize=4, linewidth=2, label=tech)
plt.yscale("log")
plt.title("Average Qubit Count Growth by Technology Type (Log Scale)", fontsize=14, fontweight="bold")
plt.xlabel("Year")
plt.ylabel("Average Qubit Count (log scale)")
plt.legend(title="Technology", bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout()
plt.savefig(f"{VISUALS_DIR}/01_qubit_growth_by_technology.png")
plt.close()

# ---------------------------------------------------------
# Chart 2: Latest reported qubit count by company
# ---------------------------------------------------------
latest_per_company = df.sort_values("announcement_date").groupby("company").tail(1)
latest_per_company = latest_per_company.sort_values("qubit_count", ascending=False)

plt.figure(figsize=(11, 6))
bars = plt.bar(latest_per_company["company"], latest_per_company["qubit_count"],
                color=sns.color_palette("viridis", len(latest_per_company)))
plt.title("Most Recent Reported Qubit Count by Company", fontsize=14, fontweight="bold")
plt.ylabel("Qubit Count")
plt.xticks(rotation=40, ha="right")
for bar in bars:
    h = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, h, f"{int(h):,}", ha="center", va="bottom", fontsize=8)
plt.tight_layout()
plt.savefig(f"{VISUALS_DIR}/02_qubit_count_by_company.png")
plt.close()

# ---------------------------------------------------------
# Chart 3: Gate error rate improvement over time by technology
# ---------------------------------------------------------
yearly_err = df.groupby(["year", "technology_type"])["gate_error_rate_pct"].mean().reset_index()
pivot_err = yearly_err.pivot(index="year", columns="technology_type", values="gate_error_rate_pct")

plt.figure(figsize=(12, 6))
for tech in pivot_err.columns:
    plt.plot(pivot_err.index, pivot_err[tech], marker="o", markersize=4, linewidth=2, label=tech)
plt.title("Gate Error Rate Improvement Over Time by Technology", fontsize=14, fontweight="bold")
plt.xlabel("Year")
plt.ylabel("Average Gate Error Rate (%)")
plt.legend(title="Technology", bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout()
plt.savefig(f"{VISUALS_DIR}/03_error_rate_trend.png")
plt.close()

# ---------------------------------------------------------
# Chart 4: Total funding raised by country
# ---------------------------------------------------------
funding_by_country = df.groupby("country")["funding_raised_million_usd"].max().sort_values(ascending=False)
# max used since funding is cumulative per company; sum by country of each company's latest cumulative figure
latest_funding = df.sort_values("announcement_date").groupby("company").tail(1)
funding_by_country = latest_funding.groupby("country")["funding_raised_million_usd"].sum().sort_values(ascending=False)

plt.figure(figsize=(9, 6))
bars = plt.bar(funding_by_country.index, funding_by_country.values,
                color=sns.color_palette("flare", len(funding_by_country)))
plt.title("Total Cumulative Funding Raised by Country ($M)", fontsize=14, fontweight="bold")
plt.ylabel("Funding Raised ($ Million)")
plt.xticks(rotation=30, ha="right")
for bar in bars:
    h = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, h, f"${h:,.0f}M", ha="center", va="bottom", fontsize=8)
plt.tight_layout()
plt.savefig(f"{VISUALS_DIR}/04_funding_by_country.png")
plt.close()

# ---------------------------------------------------------
# Chart 5: Commercial availability rate by technology type
# ---------------------------------------------------------
commercial_by_tech = (df.groupby("technology_type")["is_commercially_available"].mean() * 100).sort_values(ascending=False)

plt.figure(figsize=(9, 6))
bars = plt.barh(commercial_by_tech.index[::-1], commercial_by_tech.values[::-1],
                 color=sns.color_palette("crest", len(commercial_by_tech)))
plt.title("Commercial Availability Rate (%) by Technology Type", fontsize=14, fontweight="bold")
plt.xlabel("Commercial Availability Rate (%)")
for bar in bars:
    w = bar.get_width()
    plt.text(w, bar.get_y() + bar.get_height() / 2, f"{w:.1f}%", va="center", fontsize=8)
plt.tight_layout()
plt.savefig(f"{VISUALS_DIR}/05_commercial_availability_rate.png")
plt.close()

# ---------------------------------------------------------
# Chart 6: Correlation heatmap of numeric quantum metrics
# ---------------------------------------------------------
numeric_cols = ["qubit_count", "gate_error_rate_pct", "coherence_time_us", "quantum_volume",
                 "funding_raised_million_usd", "publications_count", "patents_filed",
                 "qubits_per_error", "is_commercially_available"]
corr = df[numeric_cols].corr()

plt.figure(figsize=(11, 8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, linewidths=0.5,
            cbar_kws={"label": "Correlation Coefficient"})
plt.title("Correlation Heatmap of Quantum Computing Metrics", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{VISUALS_DIR}/06_correlation_heatmap.png")
plt.close()

# ---------------------------------------------------------
# Chart 7: Distribution of application sector focus
# ---------------------------------------------------------
sector_counts = df["sector_focus"].value_counts()

plt.figure(figsize=(9, 9))
colors = sns.color_palette("viridis", len(sector_counts))
plt.pie(sector_counts.values, labels=sector_counts.index, autopct="%1.1f%%",
        colors=colors, startangle=90, pctdistance=0.8,
        wedgeprops={"edgecolor": "white", "linewidth": 1})
plt.title("Distribution of Application Sector Focus", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{VISUALS_DIR}/07_sector_focus_distribution.png")
plt.close()

# ---------------------------------------------------------
# Chart 8: Quantum volume trend over time by technology (log scale)
# ---------------------------------------------------------
yearly_qv = df.groupby(["year", "technology_type"])["quantum_volume"].mean().reset_index()
pivot_qv = yearly_qv.pivot(index="year", columns="technology_type", values="quantum_volume")

plt.figure(figsize=(12, 6))
for tech in pivot_qv.columns:
    plt.plot(pivot_qv.index, pivot_qv[tech], marker="o", markersize=4, linewidth=2, label=tech)
plt.yscale("log")
plt.title("Quantum Volume Trend by Technology Type (Log Scale)", fontsize=14, fontweight="bold")
plt.xlabel("Year")
plt.ylabel("Average Quantum Volume (log scale)")
plt.legend(title="Technology", bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout()
plt.savefig(f"{VISUALS_DIR}/08_quantum_volume_trend.png")
plt.close()

print("All 8 visualizations saved to:", VISUALS_DIR)
for f in sorted(pd.io.common.os.listdir(VISUALS_DIR)):
    print(" -", f)
