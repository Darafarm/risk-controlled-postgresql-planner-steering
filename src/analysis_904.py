# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 12:13:22 2026

@author: 4605daramoj
"""


#Computing Oracle 
import pandas as pd

INPUT = r"C:\Users\4605DARAMOJ\Desktop\Relational DBMS ML\SQL queries\scaled_job_runs_904_safe.csv"
OUT_ORACLE = r"C:\Users\4605DARAMOJ\Desktop\Relational DBMS ML\SQL queries\oracle_scaled_904.csv"

df = pd.read_csv(INPUT)

# get best arm per query
oracle_idx = df.groupby("query_id")["execution_time_ms"].idxmin()
oracle_df = df.loc[oracle_idx, ["query_id", "arm", "execution_time_ms"]]

oracle_df.columns = ["query_id", "oracle_arm", "oracle_time_ms"]

oracle_df.to_csv(OUT_ORACLE, index=False)

print("Saved:", OUT_ORACLE)
print("Shape:", oracle_df.shape)
print(oracle_df.head())


# Compute Regret 
OUT_REGRET = r"C:\Users\4605DARAMOJ\Desktop\Relational DBMS ML\SQL queries\regret_scaled_904.csv"

merged = df.merge(oracle_df, on="query_id")

merged["regret_ms"] = merged["execution_time_ms"] - merged["oracle_time_ms"]

merged.to_csv(OUT_REGRET, index=False)

print("Saved:", OUT_REGRET)
print("Shape:", merged.shape)
print(merged.head())


# The core analysis

print("\n=== ARM WIN COUNTS (Oracle) ===")
print(oracle_df["oracle_arm"].value_counts())

print("\n=== AVG RUNTIME PER ARM ===")
print(df.groupby("arm")["execution_time_ms"].mean())

print("\n=== AVG REGRET PER ARM ===")
print(merged.groupby("arm")["regret_ms"].mean())

print("\n=== P95 REGRET ===")
print(merged.groupby("arm")["regret_ms"].quantile(0.95))

print("\n=== P99 REGRET ===")
print(merged.groupby("arm")["regret_ms"].quantile(0.99)) 






# Computing total runtime per arm
import pandas as pd

DATA = r"C:\Users\4605DARAMOJ\Desktop\Relational DBMS ML\SQL queries\regret_scaled_904.csv"

df = pd.read_csv(DATA)

print("\n=== TOTAL RUNTIME PER ARM ===")
total_runtime = df.groupby("arm")["execution_time_ms"].sum()
print(total_runtime)

print("\n=== AVERAGE RUNTIME PER ARM ===")
print(df.groupby("arm")["execution_time_ms"].mean())


best_arm = total_runtime.idxmin()
print("\nBest fixed arm:", best_arm)



oracle_total = df.groupby("query_id")["oracle_time_ms"].first().sum()

default_total = df[df["arm"] == "default"]["execution_time_ms"].sum()

best_fixed_total = total_runtime.min()

print("\n=== TOTAL WORKLOAD RUNTIME ===")
print("Default:", default_total)
print("Best fixed arm:", best_fixed_total)
print("Oracle:", oracle_total)



print("\n=== IMPROVEMENT OVER DEFAULT ===")
print("Best fixed improvement:",
      (default_total - best_fixed_total) / default_total * 100, "%")

print("Oracle improvement:",
      (default_total - oracle_total) / default_total * 100, "%")


