# -*- coding: utf-8 -*-
"""
Created on Fri Mar 13 12:33:19 2026

@author: daram
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# LOAD CSV ONLY

df = pd.read_csv(r"C:\Users\daram\Desktop\Relational DBMS ML\data-1773085170907.csv")

print("Dataset shape:", df.shape)
print(df.head())
print(df.columns)

# DEFINE FEATURES AND LABEL
features = [
    "startup_cost",
    "total_cost",
    "plan_rows",
    "plan_width",
    "actual_rows",
    "actual_total_time"
]

X = df[features]
y = df["oracle_arm"]

print("\nLabel distribution:")
print(y.value_counts())


# TRAIN / TEST SPLIT
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nTrain shape:", X_train.shape)
print("Test shape:", X_test.shape)

# TRAIN MODEL
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42
)

model.fit(X_train, y_train)

# PREDICT
y_pred = model.predict(X_test)

print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# FEATURE IMPORTANCE
importance = pd.Series(
    model.feature_importances_,
    index=features
).sort_values(ascending=False)

print("\nFeature importance:")
print(importance)

# SAVE RESULTS

results = X_test.copy()
results["true_oracle"] = y_test.values
results["predicted_arm"] = y_pred
results.to_csv("planner_predictions.csv", index=False)

print("\nSaved: planner_predictions.csv")