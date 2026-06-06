# -*- coding: utf-8 -*-
"""
Created on Fri Mar 13 12:43:17 2026

@author: daram
"""

# -*- coding: utf-8 -*-
"""
Full plotting and figure-generation script for JOB planner steering project


1. Loads the exported CSV dataset
2. Trains two models:
   - Post-execution model
   - Pre-execution model
3. Generates and saves figures for the full pipeline

"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay
)


# FILE PATHS
csv_path = r"C:\Users\daram\Desktop\Relational DBMS ML\data-1773085170907.csv"
output_dir = r"C:\Users\daram\Desktop\Relational DBMS ML\figures"

os.makedirs(output_dir, exist_ok=True)

# LOAD DATA
df = pd.read_csv(csv_path)

print("Dataset shape:", df.shape)
print(df.head())
print(df.columns)

# BASIC CLEANUP
numeric_cols = [
    "runtime_ms", "startup_cost", "total_cost", "plan_rows",
    "plan_width", "actual_rows", "actual_total_time",
    "oracle_runtime", "regret_ms"
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["oracle_arm", "arm", "runtime_ms"])
print("Dataset shape after cleanup:", df.shape)

# HELPER FUNCTION TO SAVE FIGURES
def save_current_figure(filename: str):
    full_path = os.path.join(output_dir, filename)
    plt.tight_layout()
    plt.savefig(full_path, dpi=300, bbox_inches="tight")
    print(f"Saved: {full_path}")
    plt.close()

# FIGURE 1 - ORACLE ARM DISTRIBUTION

oracle_counts = df["oracle_arm"].value_counts().sort_values(ascending=False)

plt.figure(figsize=(8, 5))
oracle_counts.plot(kind="bar")
plt.title("Oracle Arm Distribution")
plt.xlabel("Oracle Arm")
plt.ylabel("Count")
plt.xticks(rotation=20)
save_current_figure("01_oracle_arm_distribution.png")

# FIGURE 2 - EXECUTED ARM DISTRIBUTION

arm_counts = df["arm"].value_counts().sort_index()

plt.figure(figsize=(8, 5))
arm_counts.plot(kind="bar")
plt.title("Executed Planner Arm Distribution")
plt.xlabel("Planner Arm")
plt.ylabel("Count")
plt.xticks(rotation=20)
save_current_figure("02_executed_arm_distribution.png")

#  FIGURE 3 - AVG RUNTIME BY ARM
avg_runtime_by_arm = df.groupby("arm")["runtime_ms"].mean().sort_values()

plt.figure(figsize=(8, 5))
avg_runtime_by_arm.plot(kind="bar")
plt.title("Average Runtime by Planner Arm")
plt.xlabel("Planner Arm")
plt.ylabel("Average Runtime (ms)")
plt.xticks(rotation=20)
save_current_figure("03_avg_runtime_by_arm.png")

# FIGURE 4 - AVG ORACLE RUNTIME BY ORACLE ARM

avg_oracle_runtime = df.groupby("oracle_arm")["oracle_runtime"].mean().sort_values()

plt.figure(figsize=(8, 5))
avg_oracle_runtime.plot(kind="bar")
plt.title("Average Oracle Runtime by Oracle Arm")
plt.xlabel("Oracle Arm")
plt.ylabel("Average Oracle Runtime (ms)")
plt.xticks(rotation=20)
save_current_figure("04_avg_oracle_runtime_by_arm.png")

# FIGURE 5 - REGRET DISTRIBUTION

plt.figure(figsize=(8, 5))
plt.hist(df["regret_ms"].dropna(), bins=40)
plt.title("Regret Distribution")
plt.xlabel("Regret (ms)")
plt.ylabel("Frequency")
save_current_figure("05_regret_distribution.png")

# FIGURE 6 - REGRET BY EXECUTED ARM
regret_by_arm = df.groupby("arm")["regret_ms"].mean().sort_values()

plt.figure(figsize=(8, 5))
regret_by_arm.plot(kind="bar")
plt.title("Average Regret by Executed Arm")
plt.xlabel("Executed Arm")
plt.ylabel("Average Regret (ms)")
plt.xticks(rotation=20)
save_current_figure("06_avg_regret_by_arm.png")

# QUERY-LEVEL SUMMARY FOR PLOTTING

query_summary = (
    df.groupby("query_id")
    .agg(
        oracle_arm=("oracle_arm", "first"),
        oracle_runtime=("oracle_runtime", "first")
    )
    .reset_index()
)

print("\nQuery-level summary shape:", query_summary.shape)

# FIGURE 7 - ORACLE RUNTIME BY QUERY
query_summary_sorted = query_summary.sort_values("oracle_runtime").reset_index(drop=True)

plt.figure(figsize=(12, 5))
plt.plot(query_summary_sorted.index, query_summary_sorted["oracle_runtime"])
plt.title("Oracle Runtime per Query (Sorted)")
plt.xlabel("Query Index (sorted by oracle runtime)")
plt.ylabel("Oracle Runtime (ms)")
save_current_figure("07_oracle_runtime_per_query_sorted.png")

# MODEL SETUP
features_post = [
    "startup_cost",
    "total_cost",
    "plan_rows",
    "plan_width",
    "actual_rows",
    "actual_total_time"
]

features_pre = [
    "startup_cost",
    "total_cost",
    "plan_rows",
    "plan_width"
]

target = "oracle_arm"

# Drop rows with missing values for model training
df_post = df.dropna(subset=features_post + [target]).copy()
df_pre = df.dropna(subset=features_pre + [target]).copy()

#  TRAIN POST-EXECUTION MODEL
X_post = df_post[features_post]
y_post = df_post[target]

X_train_post, X_test_post, y_train_post, y_test_post = train_test_split(
    X_post, y_post, test_size=0.2, random_state=42, stratify=y_post
)

model_post = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42
)
model_post.fit(X_train_post, y_train_post)
y_pred_post = model_post.predict(X_test_post)

acc_post = accuracy_score(y_test_post, y_pred_post)

print("\nPost-execution model accuracy:", acc_post)
print(classification_report(y_test_post, y_pred_post))

# TRAIN PRE-EXECUTION MODEL
X_pre = df_pre[features_pre]
y_pre = df_pre[target]

X_train_pre, X_test_pre, y_train_pre, y_test_pre = train_test_split(
    X_pre, y_pre, test_size=0.2, random_state=42, stratify=y_pre
)

model_pre = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42
)
model_pre.fit(X_train_pre, y_train_pre)
y_pred_pre = model_pre.predict(X_test_pre)

acc_pre = accuracy_score(y_test_pre, y_pred_pre)

print("\nPre-execution model accuracy:", acc_pre)
print(classification_report(y_test_pre, y_pred_pre))

#  FIGURE 8 - POST-EXECUTION CONFUSION MATRIX
plt.figure(figsize=(8, 6))
disp_post = ConfusionMatrixDisplay.from_predictions(y_test_post, y_pred_post)
plt.title("Confusion Matrix - Post-Execution Model")
save_current_figure("08_confusion_matrix_post_execution.png")

# FIGURE 9 - PRE-EXECUTION CONFUSION MATRIX
plt.figure(figsize=(8, 6))
disp_pre = ConfusionMatrixDisplay.from_predictions(y_test_pre, y_pred_pre)
plt.title("Confusion Matrix - Pre-Execution Model")
save_current_figure("09_confusion_matrix_pre_execution.png")

# FIGURE 10 - POST-EXECUTION FEATURE IMPORTANCE
importance_post = pd.Series(
    model_post.feature_importances_,
    index=features_post
).sort_values()

plt.figure(figsize=(8, 5))
importance_post.plot(kind="barh")
plt.title("Feature Importance - Post-Execution Model")
plt.xlabel("Importance")
save_current_figure("10_feature_importance_post_execution.png")

#  FIGURE 11 - PRE-EXECUTION FEATURE IMPORTANCE
importance_pre = pd.Series(
    model_pre.feature_importances_,
    index=features_pre
).sort_values()

plt.figure(figsize=(8, 5))
importance_pre.plot(kind="barh")
plt.title("Feature Importance - Pre-Execution Model")
plt.xlabel("Importance")
save_current_figure("11_feature_importance_pre_execution.png")

# FIGURE 12 - ACCURACY COMPARISON
accuracy_compare = pd.Series({
    "Post-Execution": acc_post,
    "Pre-Execution": acc_pre
})

plt.figure(figsize=(7, 5))
accuracy_compare.plot(kind="bar")
plt.title("Model Accuracy Comparison")
plt.ylabel("Accuracy")
plt.ylim(0, 1.05)
save_current_figure("12_accuracy_comparison.png")

#  BUILD PER-QUERY/PER-ARM AVERAGE TABLE
# Useful for runtime and regret evaluation plots
arm_avg = (
    df.groupby(["query_id", "arm"], as_index=False)
    .agg(avg_runtime_ms=("runtime_ms", "mean"))
)

oracle_avg = (
    df.groupby("query_id", as_index=False)
    .agg(
        oracle_arm=("oracle_arm", "first"),
        oracle_runtime=("oracle_runtime", "first")
    )
)

default_avg = (
    arm_avg[arm_avg["arm"] == "default"][["query_id", "avg_runtime_ms"]]
    .rename(columns={"avg_runtime_ms": "default_runtime"})
)

merged_eval = oracle_avg.merge(default_avg, on="query_id", how="left")
merged_eval["default_regret"] = merged_eval["default_runtime"] - merged_eval["oracle_runtime"]

#  FIGURE 13 - DEFAULT RUNTIME VS ORACLE RUNTIME
merged_sorted = merged_eval.sort_values("oracle_runtime").reset_index(drop=True)

plt.figure(figsize=(12, 5))
plt.plot(merged_sorted.index, merged_sorted["oracle_runtime"], label="Oracle Runtime")
plt.plot(merged_sorted.index, merged_sorted["default_runtime"], label="Default Runtime")
plt.title("Default Runtime vs Oracle Runtime per Query")
plt.xlabel("Query Index (sorted by oracle runtime)")
plt.ylabel("Runtime (ms)")
plt.legend()
save_current_figure("13_default_vs_oracle_runtime.png")

# FIGURE 14 - DEFAULT REGRET DISTRIBUTION

plt.figure(figsize=(8, 5))
plt.hist(merged_eval["default_regret"].dropna(), bins=30)
plt.title("Default Planner Regret Distribution")
plt.xlabel("Default Regret (ms)")
plt.ylabel("Frequency")
save_current_figure("14_default_regret_distribution.png")

# FIGURE 15 - TOP QUERIES WITH HIGHEST DEFAULT REGRET

top_regret = merged_eval.sort_values("default_regret", ascending=False).head(20)

plt.figure(figsize=(10, 6))
plt.barh(top_regret["query_id"], top_regret["default_regret"])
plt.gca().invert_yaxis()
plt.title("Top 20 Queries with Highest Default Regret")
plt.xlabel("Default Regret (ms)")
plt.ylabel("Query ID")
save_current_figure("15_top20_default_regret_queries.png")

#  SAVE SUMMARY TABLES

importance_post.to_csv(os.path.join(output_dir, "feature_importance_post_execution.csv"))
importance_pre.to_csv(os.path.join(output_dir, "feature_importance_pre_execution.csv"))
merged_eval.to_csv(os.path.join(output_dir, "query_runtime_regret_summary.csv"), index=False)

#  PRINT SUMMARY METRICS
print("\nSUMMARY")
print(f"Post-execution model accuracy: {acc_post:.4f}")
print(f"Pre-execution model accuracy:  {acc_pre:.4f}")
print(f"Mean default regret:           {merged_eval['default_regret'].mean():.4f} ms")
print(f"P95 default regret:            {merged_eval['default_regret'].quantile(0.95):.4f} ms")
print(f"P99 default regret:            {merged_eval['default_regret'].quantile(0.99):.4f} ms")
print("Figures saved to:", output_dir)
