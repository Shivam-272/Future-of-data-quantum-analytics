# Project Documentation — Future of Data: Quantum Analytics

## 1. Objective

To analyze the trajectory of quantum computing hardware progress across
leading companies and technology approaches, in order to:
- Track how qubit counts, quantum volume, and gate error rates evolve over time
- Compare technology approaches (Superconducting, Trapped Ion, Photonic,
  Neutral Atom, Quantum Annealing, Silicon Spin) on scale and fidelity
- Understand what drives a system's transition from lab research to
  commercial availability
- Predict commercial readiness and future qubit-count trajectories
- Present findings through an interactive dashboard

## 2. Dataset

> **Important note:** This is a demonstration / internship project, so a
> **fully synthetic (dummy) dataset** was generated to illustrate realistic
> industry trends and relationships. The generation logic lives in
> `src/00_generate_raw_dataset.py`. Figures such as qubit counts, funding
> amounts, and error rates are **simulated for learning purposes** — they
> are loosely inspired by publicly discussed industry trends (e.g. the
> widely-reported exponential pace of qubit scaling) but are **not** real
> reported numbers from IBM, Google, IonQ, or any other named company.

To make the "Data Cleaning" step meaningful, the raw dataset was
deliberately seeded with common real-world data issues:
- Missing values in `gate_error_rate_pct`, `coherence_time_us`, `quantum_volume`, `funding_raised_million_usd`, `sector_focus`
- ~11 duplicate rows (simulating a reporting glitch)
- Inconsistent text casing/whitespace (`"SUPERCONDUCTING"`, `" usa"`, `"IBM"` → mangled by naive title-casing)
- A handful of impossible values (negative qubit counts, gate error rate > 100%)

A particularly instructive cleaning step: naively applying `.str.title()`
to standardize the `company` column turns brand names like **"IBM"** into
**"Ibm"** and **"IonQ"** into **"Ionq"** — the cleaning script explicitly
detects and corrects this with a brand-name mapping, which is a common
real-world data cleaning gotcha worth highlighting.

### Schema (cleaned dataset — `dataset/cleaned_quantum_analytics_data.csv`)

| Column | Description |
|---|---|
| `record_id` | Unique record identifier |
| `announcement_date` | Date of the reported milestone |
| `company` | Quantum computing company (IBM, Google, IonQ, etc.) |
| `country` | Company's home country |
| `technology_type` | Superconducting, Trapped Ion, Photonic, Neutral Atom, Quantum Annealing, Silicon Spin |
| `qubit_count` | Reported qubit count |
| `gate_error_rate_pct` | Gate error rate (%) |
| `coherence_time_us` | Qubit coherence time (microseconds) |
| `quantum_volume` | Composite metric combining scale and fidelity |
| `funding_raised_million_usd` | Cumulative funding raised ($M) |
| `publications_count` | Research publications that period |
| `patents_filed` | Patents filed that period |
| `sector_focus` | Target application sector (Finance, Drug Discovery, etc.) |
| `is_commercially_available` | 1 = commercially accessible, 0 = R&D/lab stage |
| `year`, `quarter` | Derived date parts |
| `qubits_per_error` | `qubit_count / gate_error_rate_pct` |

Rows: **983** (after cleaning) &nbsp;|&nbsp; Period: **Jan 2017 – Jun 2026** &nbsp;|&nbsp; Companies: **12** &nbsp;|&nbsp; Technologies: **6**

## 3. Methodology

### Step 1 — Data Cleaning (`src/01_data_cleaning.py`)
- Standardized text formatting across categorical columns
- Corrected brand-name capitalization mangled by title-casing (IBM, IonQ, PsiQuantum, QuEra)
- Parsed and validated the announcement date column
- Removed exact and business-key (record_id) duplicate rows
- Corrected impossible values (negative qubit counts, error rate > 100%)
- Imputed missing numeric values using **per-technology-type median** (different
  hardware approaches have very different baseline metrics)
- Engineered helper columns: `year`, `quarter`, `qubits_per_error`

Full cleaning log: `output/data_cleaning_report.txt`

### Step 2 — Exploratory Data Analysis (`src/02_eda_visualization.py`)
Eight charts were produced covering: qubit growth by technology (log scale),
latest qubit count by company, gate error rate trend, funding by country,
commercial availability rate by technology, metric correlations, sector
focus distribution, and quantum volume trend. See `visuals/`.

### Step 3 — Prediction Models (`src/03_prediction_model.py`)

**Model 1 — Random Forest Classifier** (Commercial Availability Prediction)
Predicts whether a system/deployment record is commercially available,
using class-balanced weighting to handle class imbalance (~41% commercial rate).

| Metric | Score |
|---|---|
| Accuracy | 0.660 |
| Precision (Commercial) | 0.577 |
| Recall (Commercial) | 0.613 |
| F1-score (Commercial) | 0.594 |
| ROC-AUC | 0.725 |

**Model 2 — Random Forest Regressor** (Qubit Count Prediction)
Predicts qubit count from technology type, company, funding, error rate,
and time — capturing the strong exponential growth pattern in the data.

| Metric | Score |
|---|---|
| MAE | 304.8 qubits |
| RMSE | 1,058.4 qubits |
| R² | 0.988 |

> **Note on model performance:** The regression model achieves a very high
> R² because qubit-count trajectories follow a strong, largely deterministic
> exponential pattern by technology and company maturity in this dataset —
> a genuinely learnable signal. The classification task is inherently
> harder (commercial launch decisions depend on many unobserved business
> factors beyond hardware specs), so a ROC-AUC around 0.73 reflects a
> realistic, moderate predictive signal rather than a data leak.

Full report: `output/model_performance_report.txt`

### Step 4 — Dashboard (`src/04_build_dashboard.py`)
A self-contained interactive HTML dashboard (Plotly, no server required)
was built combining 6 KPI cards and 6 interactive charts. Open
`dashboard/quantum_analytics_dashboard.html` directly in any browser.

## 4. Key Findings

1. **Qubit counts grow at a strikingly exponential pace** across every
   technology approach, consistent with the widely-discussed "doubly
   exponential" scaling trend in quantum hardware roadmaps.
2. **Quantum Annealing (D-Wave)** reports far higher raw qubit counts than
   gate-model approaches, but annealing qubits solve a narrower class of
   optimization problems and aren't directly comparable to gate-model qubits.
3. **Trapped Ion systems show the lowest gate error rates**, reflecting the
   inherently high-fidelity nature of the technology, even though they scale
   to fewer qubits than Superconducting approaches.
4. **Commercial availability correlates more with company maturity and time
   elapsed** than with raw qubit count alone — software/ecosystem maturity
   matters as much as hardware specs for real-world deployment.
5. **Funding scales with company age/maturity** more than with a specific
   technology choice, suggesting investor confidence tracks execution track
   record broadly across approaches.

## 5. Recommendations

- Track technology-specific error-rate floors and commercial-availability
  signals (company maturity, publication/patent cadence) as leading
  indicators of deployment readiness, rather than raw qubit count alone.
- When comparing companies, normalize by technology type — a 1,000-qubit
  annealer and a 100-qubit gate-model processor are not solving the same
  class of problems.
- Monitor trapped-ion and neutral-atom approaches for fidelity-sensitive
  use cases (e.g. cryptography, chemistry simulation) even though they may
  report lower headline qubit counts.
- Use the regression model's qubit-count trajectory to inform roadmap
  planning, and the classifier's probability output to flag which
  companies/technologies are approaching commercial inflection points.

## 6. Tools & Libraries Used

Python, Pandas, NumPy, Matplotlib, Seaborn, Scikit-learn (RandomForestClassifier,
RandomForestRegressor, ROC-AUC), Plotly (interactive dashboard), Jupyter Notebook.

## 7. Folder Structure

```
Future-of-Data-Quantum-Analytics/
├── README.md
├── dataset/
│   ├── raw_quantum_analytics_data.csv
│   └── cleaned_quantum_analytics_data.csv
├── notebook/
│   └── Quantum_Analytics_Analysis.ipynb
├── src/
│   ├── 00_generate_raw_dataset.py
│   ├── 01_data_cleaning.py
│   ├── 02_eda_visualization.py
│   ├── 03_prediction_model.py
│   ├── 04_build_dashboard.py
│   └── build_notebook.py
├── visuals/            (13 charts, .png)
├── dashboard/
│   └── quantum_analytics_dashboard.html
├── screenshots/         (dashboard + notebook screenshots)
├── output/               (cleaning & model reports, .txt)
└── documentation/
    └── Project_Documentation.md
```
