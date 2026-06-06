# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 13:09:42 2026

@author: 4605daramoj
"""

#Ml training 

import pandas as pd

DATA = r"C:\Users\4605DARAMOJ\Desktop\Relational DBMS ML\SQL queries\regret_scaled_904.csv"

df = pd.read_csv(DATA)

features = [
    "root_total_cost",
    "root_plan_rows",
    "root_plan_width",
    "hash_join_count",
    "merge_join_count",
    "nested_loop_count",
    "seq_scan_count",
    "index_scan_count",
    "total_node_count",
    "max_depth"
]

X = df[features]
y = df["oracle_arm"]

print("Feature matrix shape:", X.shape)
print("Target shape:", y.shape)




from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("X_train:", X_train.shape)
print("X_test :", X_test.shape)
print("y_train:", y_train.shape)
print("y_test :", y_test.shape)

print("\nTrain class distribution:")
print(y_train.value_counts())

print("\nTest class distribution:")
print(y_test.value_counts())


from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    random_state=42,
    n_jobs=-1
)

rf.fit(X_train, y_train)

print("Random Forest training complete")


from sklearn.metrics import accuracy_score, classification_report

preds = rf.predict(X_test)

acc = accuracy_score(y_test, preds)

print("Model Accuracy:", acc)

print("\nClassification Report:\n")
print(classification_report(y_test, preds))



# Simulate if the model chose the join strategy before execution

df["predicted_arm"] = rf.predict(X)

pred_runtime = []

for q in df["query_id"].unique():

    sub = df[df["query_id"] == q]

    pred_arm = sub["predicted_arm"].iloc[0]

    pred_time = sub[sub["arm"] == pred_arm]["execution_time_ms"].values[0]

    pred_runtime.append(pred_time)

learned_total = sum(pred_runtime)

print("Learned optimizer runtime:", learned_total)




# System Comparison 
print("\n=== SYSTEM COMPARISON ===")
print("Default runtime:", default_total)
print("Best fixed arm:", best_fixed_total)
print("Learned model:", learned_total)
print("Oracle:", oracle_total)




