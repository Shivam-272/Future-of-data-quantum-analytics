"""
00_generate_raw_dataset.py
---------------------------------------------------
Generates a synthetic (dummy) "raw" dataset tracking quantum computing
hardware progress and industry activity - the "Future of Data: Quantum
Analytics" theme.

Each row represents a quantum computing system/milestone announcement from
a company in a given quarter, including qubit count, quantum volume, gate
error rate, coherence time, funding raised, publications, patents, and
commercial availability - loosely inspired by real public roadmaps from
players like IBM, Google, IonQ, Rigetti, D-Wave, Quantinuum, PsiQuantum,
and others (with fictionalized/simulated numbers, not real reported figures).

Qubit counts and quantum volume are simulated with an exponential growth
trend by technology type (reflecting the widely-discussed "doubly
exponential" pace of quantum hardware scaling), giving the downstream
trend analysis and prediction models genuine, learnable signal.

The dataset is generated with deliberate real-world data quality issues
(missing values, duplicate rows, inconsistent text casing, and a few
impossible values) so that the cleaning step (01_data_cleaning.py) has
real work to do.

Output: dataset/raw_quantum_analytics_data.csv
---------------------------------------------------
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

# ---------------------------------------------------------
# 1. Define companies, their technology approach, and launch quarter
# ---------------------------------------------------------
COMPANIES = {
    "IBM":          {"tech": "Superconducting", "country": "USA",     "start": "2017-Q1", "maturity": 0.95},
    "Google":       {"tech": "Superconducting", "country": "USA",     "start": "2017-Q3", "maturity": 0.93},
    "IonQ":         {"tech": "Trapped Ion",      "country": "USA",     "start": "2019-Q1", "maturity": 0.80},
    "Rigetti":      {"tech": "Superconducting", "country": "USA",     "start": "2018-Q1", "maturity": 0.70},
    "D-Wave":       {"tech": "Quantum Annealing","country": "Canada",  "start": "2017-Q1", "maturity": 0.85},
    "Quantinuum":   {"tech": "Trapped Ion",      "country": "UK",      "start": "2020-Q3", "maturity": 0.82},
    "PsiQuantum":   {"tech": "Photonic",         "country": "USA",     "start": "2021-Q1", "maturity": 0.55},
    "Xanadu":       {"tech": "Photonic",         "country": "Canada",  "start": "2020-Q1", "maturity": 0.60},
    "Origin Quantum": {"tech": "Superconducting","country": "China",   "start": "2019-Q3", "maturity": 0.65},
    "Pasqal":       {"tech": "Neutral Atom",      "country": "France",  "start": "2021-Q1", "maturity": 0.58},
    "QuEra":        {"tech": "Neutral Atom",      "country": "USA",     "start": "2021-Q3", "maturity": 0.60},
    "Intel":        {"tech": "Silicon Spin",      "country": "USA",     "start": "2020-Q1", "maturity": 0.50},
}

SECTORS = ["Cryptography", "Drug Discovery", "Finance", "Logistics",
           "Materials Science", "AI/ML", "General Research"]

quarters = pd.period_range("2017-01", "2026-06", freq="M")

rows = []
record_id = 1

for company, meta in COMPANIES.items():
    start_q = pd.Period(meta["start"].replace("-Q1", "-01").replace("-Q3", "-07"), freq="M")
    tech = meta["tech"]
    country = meta["country"]
    maturity = meta["maturity"]

    # Technology-specific growth parameters (illustrative, not real reported figures)
    growth_params = {
        "Superconducting": {"base_qubits": 20, "growth": 1.42, "err_start": 3.5, "err_floor": 0.15},
        "Trapped Ion":     {"base_qubits": 11, "growth": 1.30, "err_start": 1.8, "err_floor": 0.05},
        "Quantum Annealing": {"base_qubits": 2000, "growth": 1.28, "err_start": 6.0, "err_floor": 2.0},
        "Photonic":        {"base_qubits": 8,  "growth": 1.55, "err_start": 5.0, "err_floor": 0.8},
        "Neutral Atom":    {"base_qubits": 20, "growth": 1.48, "err_start": 3.0, "err_floor": 0.4},
        "Silicon Spin":    {"base_qubits": 6,  "growth": 1.35, "err_start": 4.5, "err_floor": 0.6},
    }[tech]

    for q in quarters:
        if q < start_q:
            continue
        months_since_start = (q - start_q).n
        if months_since_start < 0:
            continue

        # Not every company announces every month - sparse, realistic reporting cadence
        if np.random.random() < 0.30:
            continue

        # How many sector-specific deployment records this period (1-2)
        n_records = np.random.choice([1, 2], p=[0.65, 0.35])

        for _ in range(n_records):
            quarters_since_start = months_since_start / 3.0  # keep growth curves on a quarterly-equivalent scale

            # Exponential-ish qubit growth with company maturity + noise
            growth_factor = growth_params["growth"] ** (quarters_since_start / 2.2)
            qubit_count = growth_params["base_qubits"] * growth_factor * maturity
            qubit_count = max(2, qubit_count * np.random.uniform(0.85, 1.18))
            qubit_count = round(qubit_count)

            # Gate error rate improves (decreases) over time toward a technology floor
            err_decay = np.exp(-quarters_since_start / 14)
            gate_error_rate = growth_params["err_floor"] + (growth_params["err_start"] - growth_params["err_floor"]) * err_decay
            gate_error_rate = round(max(growth_params["err_floor"] * 0.9, gate_error_rate * np.random.uniform(0.9, 1.15)), 3)

            # Coherence time improves over time (microseconds)
            coherence_time = round(max(5, (10 + quarters_since_start * 3.2) * maturity * np.random.uniform(0.8, 1.3)), 1)

            # Quantum volume - loosely a function of qubit count and inverse of error rate
            qv_log2 = np.log2(max(2, qubit_count)) * (1 - gate_error_rate / 10) * maturity
            quantum_volume = round(2 ** max(1, qv_log2))

            # Cumulative funding raised (million USD) - grows over time, company-specific scale
            base_funding = {"IBM": 500, "Google": 800, "IonQ": 250, "Rigetti": 200, "D-Wave": 300,
                             "Quantinuum": 600, "PsiQuantum": 700, "Xanadu": 220, "Origin Quantum": 180,
                             "Pasqal": 150, "QuEra": 170, "Intel": 400}[company]
            funding_raised = round(base_funding * (1 + quarters_since_start * 0.045) * np.random.uniform(0.85, 1.2), 1)

            publications_count = int(max(0, np.random.poisson(3 + quarters_since_start * 0.15) * maturity))
            patents_filed = int(max(0, np.random.poisson(1.5 + quarters_since_start * 0.08) * maturity))

            # Commercial availability more likely for mature companies with decent qubit counts & lower error
            commercial_logit = (
                -3.0
                + 2.5 * maturity
                + 0.9 * min(1, qubit_count / 100)
                - 0.6 * min(1, gate_error_rate / 3)
                + 0.5 * min(1, quarters_since_start / 20)
            )
            is_commercially_available = int(np.random.random() < 1 / (1 + np.exp(-commercial_logit)))

            sector_focus = np.random.choice(SECTORS)

            rows.append({
                "record_id": record_id,
                "announcement_date": q.end_time.strftime("%Y-%m-%d"),
                "company": company,
                "country": country,
                "technology_type": tech,
                "qubit_count": qubit_count,
                "gate_error_rate_pct": gate_error_rate,
                "coherence_time_us": coherence_time,
                "quantum_volume": quantum_volume,
                "funding_raised_million_usd": funding_raised,
                "publications_count": publications_count,
                "patents_filed": patents_filed,
                "sector_focus": sector_focus,
                "is_commercially_available": is_commercially_available,
            })
            record_id += 1

df = pd.DataFrame(rows)

# ---------------------------------------------------------
# 2. Deliberately inject realistic data-quality issues
# ---------------------------------------------------------
n = len(df)
rng = np.random.default_rng(7)

# a) Inconsistent text casing / stray whitespace
idx = rng.choice(n, size=int(n * 0.06), replace=False)
df.loc[idx, "technology_type"] = df.loc[idx, "technology_type"].str.upper()

idx2 = rng.choice(n, size=int(n * 0.05), replace=False)
df.loc[idx2, "country"] = df.loc[idx2, "country"].str.lower() + "  "

idx3 = rng.choice(n, size=int(n * 0.04), replace=False)
df.loc[idx3, "company"] = " " + df.loc[idx3, "company"]

# b) Missing values sprinkled across several columns
for col, frac in [("gate_error_rate_pct", 0.03), ("coherence_time_us", 0.025),
                   ("funding_raised_million_usd", 0.02), ("quantum_volume", 0.02),
                   ("sector_focus", 0.015)]:
    idx = rng.choice(n, size=int(n * frac), replace=False)
    df.loc[idx, col] = np.nan

# c) A handful of duplicate rows (reporting glitch)
dup_rows = df.sample(n=int(n * 0.012), random_state=1)
df = pd.concat([df, dup_rows], ignore_index=True)

# d) A few impossible / out-of-range values (data entry errors)
bad_idx = rng.choice(len(df), size=12, replace=False)
df.loc[bad_idx[:6], "qubit_count"] = -df.loc[bad_idx[:6], "qubit_count"]           # negative qubits, impossible
df.loc[bad_idx[6:], "gate_error_rate_pct"] = df.loc[bad_idx[6:], "gate_error_rate_pct"] * 15  # >100%, impossible

# e) Shuffle rows and save
df = df.sample(frac=1, random_state=99).reset_index(drop=True)

output_path = "/home/claude/Future-of-Data-Quantum-Analytics/dataset/raw_quantum_analytics_data.csv"
df.to_csv(output_path, index=False)

print(f"Raw dataset generated: {output_path}")
print(f"Shape: {df.shape}")
print(f"Commercial availability rate: {df['is_commercially_available'].mean():.3f}")
print(f"Missing values per column:\n{df.isna().sum()}")
print(f"Duplicate rows: {df.duplicated().sum()}")
