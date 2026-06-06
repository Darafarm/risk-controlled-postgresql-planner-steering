# -*- coding: utf-8 -*-
"""
Created on Sat Mar 21 13:20:55 2026

@author: daram
"""

import os
import random
import re

INPUT_DIR = r"C:\Users\daram\Desktop\Relational DBMS ML\SQL queries\join-order-benchmark-master\join-order-benchmark-master"
OUTPUT_DIR = r"C:\Users\daram\Desktop\Relational DBMS ML\SQL queries\job_queries_scaled"

os.makedirs(OUTPUT_DIR, exist_ok=True)

VARIANTS_PER_QUERY = 8  # 113 * 8 ≈ 904 queries


def mutate_year(sql):
    def repl(match):
        a = random.randint(1950, 2005)
        b = a + random.randint(1, 10)
        return f"BETWEEN {a} AND {b}"
    return re.sub(r"BETWEEN\s+\d+\s+AND\s+\d+", repl, sql)


def mutate_limit(sql):
    def repl(match):
        n = random.randint(5, 200)
        return f"LIMIT {n}"
    return re.sub(r"LIMIT\s+\d+", repl, sql)


def mutate(sql):
    sql = mutate_year(sql)
    sql = mutate_limit(sql)
    return sql


query_id = 0

print("Reading from:", INPUT_DIR)

for file in os.listdir(INPUT_DIR):
    if not file.endswith(".sql"):
        continue

    with open(os.path.join(INPUT_DIR, file), "r", encoding="utf-8") as f:
        base_sql = f.read()

    for i in range(VARIANTS_PER_QUERY):
        new_sql = mutate(base_sql)
        out_name = f"q{query_id}.sql"

        with open(os.path.join(OUTPUT_DIR, out_name), "w", encoding="utf-8") as f:
            f.write(new_sql)

        query_id += 1

print("Generated:", query_id, "queries")
print("Saved to:", OUTPUT_DIR)