"""
03_prediction_model.py
---------------------------------------------------
Builds two machine learning models on top of the cleaned quantum computing
industry dataset:

    MODEL 1 (Classification): Random Forest Classifier
        Predicts whether a quantum computing system/deployment record is
        COMMERCIALLY AVAILABLE (1) or still in R&D/lab stage (0), based on
        qubit count, error rate, funding, coherence time, and technology
        maturity signals. This helps investors/analysts flag which
        systems are closest to real-world deployment.

    MODEL 2 (Regression): Random Forest Regressor
        Predicts the QUBIT COUNT of a system from its technology type,
        year, funding, error rate, and other attributes - useful for
        estimating where a given technology roadmap is headed.

Outputs:
    - output/model_performance_report.txt
    - visuals/09_feature_importance_classification.png
    - visuals/10_roc_curve.png
    - visuals/11_confusion_matrix.png
    - visuals/12_feature_importance_regression.png
    - visuals/13_actual_vs_predicted_qubit_count.png
---------------------------------------------------
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, roc_curve,
    confusion_matrix, classification_report,
    mean_absolute_error, mean_squared_error, r2_score
)

DATA_PATH = "/home/claude/Future-of-Data-Quantum-Analytics/dataset/cleaned_quantum_analytics_data.csv"
VISUALS_DIR = "/home/claude/Future-of-Data-Quantum-Analytics/visuals"
REPORT_PATH = "/home/claude/Future-of-Data-Quantum-Analytics/output/model_performance_report.txt"

sns.set_theme(style="whitegrid")
report_lines = []


def log(msg=""):
    print(msg)
    report_lines.append(str(msg))


df = pd.read_csv(DATA_PATH, parse_dates=["announcement_date"])

# ===========================================================
# Feature engineering (shared by both models)
# ===========================================================
feature_df = df.copy()

cat_cols = ["company", "country", "technology_type", "sector_focus"]
for col in cat_cols:
    le = LabelEncoder()
    feature_df[col + "_enc"] = le.fit_transform(feature_df[col])

feature_df["month_num"] = feature_df["announcement_date"].dt.month
feature_df["years_since_2017"] = (feature_df["announcement_date"].dt.year - 2017) + feature_df["month_num"] / 12

CLF_FEATURES = [
    "company_enc", "country_enc", "technology_type_enc", "sector_focus_enc",
    "qubit_count", "gate_error_rate_pct", "coherence_time_us", "quantum_volume",
    "funding_raised_million_usd", "publications_count", "patents_filed", "years_since_2017"
]

log("=" * 70)
log("FUTURE OF DATA: QUANTUM ANALYTICS - MODEL PERFORMANCE REPORT")
log("=" * 70)
log(f"Dataset size: {len(feature_df)} rows")
log(f"Overall commercial availability rate: {feature_df['is_commercially_available'].mean():.3f}")
log(f"Features used (classification): {CLF_FEATURES}")

# ===========================================================
# MODEL 1: Classification -> Commercial Availability Prediction
# ===========================================================
log("\n" + "-" * 70)
log("MODEL 1: Random Forest Classifier - Commercial Availability Prediction")
log("-" * 70)

X = feature_df[CLF_FEATURES]
y = feature_df["is_commercially_available"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

clf = RandomForestClassifier(n_estimators=250, max_depth=8, min_samples_leaf=5,
                              class_weight="balanced", random_state=42, n_jobs=-1)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
y_proba = clf.predict_proba(X_test)[:, 1]

acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_proba)

log(f"\nAccuracy : {acc:.4f}")
log(f"Precision: {prec:.4f}")
log(f"Recall   : {rec:.4f}")
log(f"F1-score : {f1:.4f}")
log(f"ROC-AUC  : {auc:.4f}")
log("\nClassification Report:")
log(classification_report(y_test, y_pred, target_names=["Not Yet Commercial", "Commercially Available"]))

# Confusion matrix plot
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Purples",
            xticklabels=["Not Commercial", "Commercial"], yticklabels=["Not Commercial", "Commercial"])
plt.title("Confusion Matrix - Commercial Availability Classifier", fontsize=12, fontweight="bold")
plt.ylabel("Actual")
plt.xlabel("Predicted")
plt.tight_layout()
plt.savefig(f"{VISUALS_DIR}/11_confusion_matrix.png")
plt.close()

# ROC curve
fpr, tpr, _ = roc_curve(y_test, y_proba)
plt.figure(figsize=(7, 6))
plt.plot(fpr, tpr, color="#845EF7", linewidth=2.5, label=f"ROC Curve (AUC = {auc:.3f})")
plt.plot([0, 1], [0, 1], "k--", linewidth=1, label="Random Classifier")
plt.title("ROC Curve - Commercial Availability Classifier", fontsize=13, fontweight="bold")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.legend()
plt.tight_layout()
plt.savefig(f"{VISUALS_DIR}/10_roc_curve.png")
plt.close()

# Feature importance plot
importances = pd.Series(clf.feature_importances_, index=CLF_FEATURES).sort_values(ascending=True)
plt.figure(figsize=(9, 7))
plt.barh(importances.index, importances.values, color=sns.color_palette("viridis", len(importances)))
plt.title("Feature Importance - Commercial Availability Classifier", fontsize=13, fontweight="bold")
plt.xlabel("Importance")
plt.tight_layout()
plt.savefig(f"{VISUALS_DIR}/09_feature_importance_classification.png")
plt.close()

# ===========================================================
# MODEL 2: Regression -> Qubit Count Prediction
# ===========================================================
log("\n" + "-" * 70)
log("MODEL 2: Random Forest Regressor - Qubit Count Prediction")
log("-" * 70)

REG_FEATURES = [
    "company_enc", "country_enc", "technology_type_enc", "sector_focus_enc",
    "gate_error_rate_pct", "coherence_time_us", "funding_raised_million_usd",
    "publications_count", "patents_filed", "years_since_2017"
]

Xr = feature_df[REG_FEATURES]
yr = feature_df["qubit_count"]

Xr_train, Xr_test, yr_train, yr_test = train_test_split(
    Xr, yr, test_size=0.2, random_state=42
)

reg = RandomForestRegressor(n_estimators=300, max_depth=12, random_state=42, n_jobs=-1)
reg.fit(Xr_train, yr_train)
yr_pred = reg.predict(Xr_test)

mae = mean_absolute_error(yr_test, yr_pred)
rmse = np.sqrt(mean_squared_error(yr_test, yr_pred))
r2 = r2_score(yr_test, yr_pred)

log(f"\nMean Absolute Error (MAE) : {mae:.1f} qubits")
log(f"Root Mean Squared Error   : {rmse:.1f} qubits")
log(f"R-squared (R2 Score)      : {r2:.4f}")

# Actual vs predicted plot (log-log scale given the huge qubit count range across technologies)
plt.figure(figsize=(8, 7))
plt.scatter(yr_test, yr_pred, alpha=0.4, s=20, color="#20C997")
lims = [max(1, min(yr_test.min(), yr_pred.min())), max(yr_test.max(), yr_pred.max())]
plt.plot(lims, lims, "r--", linewidth=2, label="Perfect Prediction Line")
plt.xscale("log")
plt.yscale("log")
plt.title(f"Actual vs Predicted Qubit Count (R² = {r2:.3f}, log scale)", fontsize=13, fontweight="bold")
plt.xlabel("Actual Qubit Count")
plt.ylabel("Predicted Qubit Count")
plt.legend()
plt.tight_layout()
plt.savefig(f"{VISUALS_DIR}/13_actual_vs_predicted_qubit_count.png")
plt.close()

# Feature importance plot for regression
reg_importances = pd.Series(reg.feature_importances_, index=REG_FEATURES).sort_values(ascending=True)
plt.figure(figsize=(9, 7))
plt.barh(reg_importances.index, reg_importances.values, color=sns.color_palette("flare", len(reg_importances)))
plt.title("Feature Importance - Qubit Count Regression Model", fontsize=13, fontweight="bold")
plt.xlabel("Importance")
plt.tight_layout()
plt.savefig(f"{VISUALS_DIR}/12_feature_importance_regression.png")
plt.close()

log("\n" + "=" * 70)
log("All model artifacts (plots) saved to visuals/ folder.")
log("=" * 70)

with open(REPORT_PATH, "w") as f:
    f.write("\n".join(report_lines))

print(f"\nFull report saved to: {REPORT_PATH}")
