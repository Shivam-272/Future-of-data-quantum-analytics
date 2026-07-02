"""
01_data_cleaning.py
---------------------------------------------------
Cleans the raw quantum computing industry dataset.

Cleaning steps performed:
    1. Standardize text columns (strip whitespace, fix casing)
    2. Parse the announcement_date column into a proper datetime type
    3. Remove exact duplicate rows
    4. Fix impossible values (negative qubit counts, error rate > 100%)
    5. Handle missing values with sensible imputation strategies
    6. Add helpful derived columns (year, quarter, qubits-per-error ratio)
    7. Save the cleaned dataset for analysis / modeling

Input : dataset/raw_quantum_analytics_data.csv
Output: dataset/cleaned_quantum_analytics_data.csv
---------------------------------------------------
"""

import pandas as pd
import numpy as np

RAW_PATH = "/home/claude/Future-of-Data-Quantum-Analytics/dataset/raw_quantum_analytics_data.csv"
CLEAN_PATH = "/home/claude/Future-of-Data-Quantum-Analytics/dataset/cleaned_quantum_analytics_data.csv"
LOG_PATH = "/home/claude/Future-of-Data-Quantum-Analytics/output/data_cleaning_report.txt"

log_lines = []


def log(msg):
    print(msg)
    log_lines.append(str(msg))


# ---------------------------------------------------------
# 1. Load the raw data
# ---------------------------------------------------------
df = pd.read_csv(RAW_PATH)
log(f"Loaded raw dataset: {df.shape[0]} rows, {df.shape[1]} columns")

# ---------------------------------------------------------
# 2. Standardize text / categorical columns
# ---------------------------------------------------------
text_cols = ["company", "country", "technology_type", "sector_focus"]
for col in text_cols:
    df[col] = df[col].astype(str).str.strip().str.title()
    df[col] = df[col].replace("Nan", np.nan)

# Title-casing mangles brand names with unconventional capitalization
# (e.g. "IBM" -> "Ibm", "IonQ" -> "Ionq"). Restore the correct official names.
company_name_fix = {
    "Ibm": "IBM", "Ionq": "IonQ", "Psiquantum": "PsiQuantum", "Quera": "QuEra",
    "D-Wave": "D-Wave", "Google": "Google", "Rigetti": "Rigetti",
    "Quantinuum": "Quantinuum", "Xanadu": "Xanadu", "Origin Quantum": "Origin Quantum",
    "Pasqal": "Pasqal", "Intel": "Intel",
}
df["company"] = df["company"].replace(company_name_fix)
log("Restored correct brand-name capitalization for company column (e.g. Ibm -> IBM, Ionq -> IonQ)")

log(f"Standardized text formatting for columns: {text_cols}")

# ---------------------------------------------------------
# 3. Parse the date column properly
# ---------------------------------------------------------
df["announcement_date"] = pd.to_datetime(df["announcement_date"], errors="coerce")
bad_dates = df["announcement_date"].isna().sum()
log(f"Rows with unparseable dates dropped: {bad_dates}")
df = df.dropna(subset=["announcement_date"])

# ---------------------------------------------------------
# 4. Remove exact duplicate rows
# ---------------------------------------------------------
before = len(df)
df = df.drop_duplicates()
log(f"Removed {before - len(df)} exact duplicate rows")

before = len(df)
df = df.drop_duplicates(subset=["record_id"])
log(f"Removed {before - len(df)} duplicate rows on business key (record_id)")

# ---------------------------------------------------------
# 5. Fix impossible / out-of-range values
# ---------------------------------------------------------
neg_qubits = (df["qubit_count"] < 0).sum()
df.loc[df["qubit_count"] < 0, "qubit_count"] = df.loc[df["qubit_count"] < 0, "qubit_count"].abs()
log(f"Fixed {neg_qubits} negative 'qubit_count' values by taking absolute value")

bad_err = (df["gate_error_rate_pct"] > 100).sum()
df.loc[df["gate_error_rate_pct"] > 100, "gate_error_rate_pct"] = np.nan  # treat as missing, re-impute below
log(f"Flagged {bad_err} impossible gate_error_rate_pct values (>100%) as missing for re-imputation")

# ---------------------------------------------------------
# 6. Handle missing values
#    Strategy:
#      - Numeric metrics -> impute using the median FOR THAT TECHNOLOGY TYPE
#        (different quantum hardware approaches have very different baselines)
#      - sector_focus -> impute with the overall mode
# ---------------------------------------------------------
numeric_impute_cols = ["gate_error_rate_pct", "coherence_time_us", "quantum_volume", "funding_raised_million_usd"]

missing_before = df[numeric_impute_cols].isna().sum().sum()
for col in numeric_impute_cols:
    df[col] = df.groupby("technology_type")[col].transform(lambda s: s.fillna(s.median()))
    df[col] = df[col].fillna(df[col].median())
missing_after = df[numeric_impute_cols].isna().sum().sum()
log(f"Imputed {missing_before - missing_after} missing numeric values using per-technology median")

mode_sector = df["sector_focus"].mode()[0]
missing_sector = df["sector_focus"].isna().sum()
df["sector_focus"] = df["sector_focus"].fillna(mode_sector)
log(f"Imputed {missing_sector} missing sector_focus values with mode ('{mode_sector}')")

# ---------------------------------------------------------
# 7. Add derived / helper columns for analysis
# ---------------------------------------------------------
df["year"] = df["announcement_date"].dt.year
df["quarter"] = df["announcement_date"].dt.to_period("Q").astype(str)
df["qubits_per_error"] = (df["qubit_count"] / df["gate_error_rate_pct"].replace(0, np.nan)).round(1).fillna(0)

# Round metrics for cleanliness
df["gate_error_rate_pct"] = df["gate_error_rate_pct"].round(3)
df["quantum_volume"] = df["quantum_volume"].round(0).astype(int)
df["funding_raised_million_usd"] = df["funding_raised_million_usd"].round(1)

df = df.reset_index(drop=True)

# ---------------------------------------------------------
# 8. Final sanity check + save
# ---------------------------------------------------------
log(f"\nFinal cleaned dataset shape: {df.shape}")
log(f"Remaining missing values total: {df.isna().sum().sum()}")
log(f"Date range: {df['announcement_date'].min().date()} to {df['announcement_date'].max().date()}")
log(f"Commercial availability rate: {df['is_commercially_available'].mean():.3f}")
log(f"Unique companies: {sorted(df['company'].unique().tolist())}")
log(f"Unique technology types: {sorted(df['technology_type'].unique().tolist())}")

df.to_csv(CLEAN_PATH, index=False)
log(f"\nCleaned dataset saved to: {CLEAN_PATH}")

with open(LOG_PATH, "w") as f:
    f.write("\n".join(log_lines))
print(f"\nCleaning report saved to: {LOG_PATH}")
