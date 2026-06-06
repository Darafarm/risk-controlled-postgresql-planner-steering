# -*- coding: utf-8 -*-
"""
Created on Sat Mar 21 13:28:14 2026

@author: daram
"""

import os
import random
import re

INPUT_DIR = r"C:\Users\daram\Desktop\Relational DBMS ML\SQL queries\join-order-benchmark-master\join-order-benchmark-master"
OUTPUT_DIR = r"C:\Users\daram\Desktop\Relational DBMS ML\SQL queries\job_queries_scaled_clean"

os.makedirs(OUTPUT_DIR, exist_ok=True)

VARIANTS_PER_QUERY = 8

job_file_pattern = re.compile(r"^\d+[a-z]\.sql$", re.IGNORECASE)


def is_real_job_query(filename, sql_text):
    if not job_file_pattern.match(filename):
        return False

    first_line = sql_text.strip().lower()
    return first_line.startswith("select")


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
kept_files = []

for file in sorted(os.listdir(INPUT_DIR)):
    if not file.endswith(".sql"):
        continue

    file_path = os.path.join(INPUT_DIR, file)
    with open(file_path, "r", encoding="utf-8") as f:
        base_sql = f.read()

    if not is_real_job_query(file, base_sql):
        print("Skipping non-query file:", file)
        continue

    kept_files.append(file)

    for i in range(VARIANTS_PER_QUERY):
        new_sql = mutate(base_sql)
        out_name = f"q{query_id}.sql"

        with open(os.path.join(OUTPUT_DIR, out_name), "w", encoding="utf-8") as f:
            f.write(new_sql)

        query_id += 1

print("\nValid JOB query files kept:", len(kept_files))
print("Generated queries:", query_id)
print("Saved to:", OUTPUT_DIR)