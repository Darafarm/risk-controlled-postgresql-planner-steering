# -*- coding: utf-8 -*-
"""
Created on Sat Mar 21 13:32:50 2026

@author: daram
"""

import psycopg2

SCHEMA_FILE = r"C:\Users\daram\Desktop\Relational DBMS ML\SQL queries\join-order-benchmark-master\join-order-benchmark-master\schema.sql"

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="imdb",
    user="postgres",
    password="james1859"
)

conn.autocommit = True
cur = conn.cursor()

# optional cleanup if you want a fresh retry
cur.execute("DROP TABLE IF EXISTS aka_name CASCADE;")
cur.execute("DROP TABLE IF EXISTS aka_title CASCADE;")
cur.execute("DROP TABLE IF EXISTS cast_info CASCADE;")
cur.execute("DROP TABLE IF EXISTS char_name CASCADE;")
cur.execute("DROP TABLE IF EXISTS comp_cast_type CASCADE;")
cur.execute("DROP TABLE IF EXISTS company_name CASCADE;")
cur.execute("DROP TABLE IF EXISTS company_type CASCADE;")
cur.execute("DROP TABLE IF EXISTS complete_cast CASCADE;")
cur.execute("DROP TABLE IF EXISTS info_type CASCADE;")
cur.execute("DROP TABLE IF EXISTS keyword CASCADE;")
cur.execute("DROP TABLE IF EXISTS kind_type CASCADE;")
cur.execute("DROP TABLE IF EXISTS link_type CASCADE;")
cur.execute("DROP TABLE IF EXISTS movie_companies CASCADE;")
cur.execute("DROP TABLE IF EXISTS movie_info CASCADE;")
cur.execute("DROP TABLE IF EXISTS movie_info_idx CASCADE;")
cur.execute("DROP TABLE IF EXISTS movie_keyword CASCADE;")
cur.execute("DROP TABLE IF EXISTS movie_link CASCADE;")
cur.execute("DROP TABLE IF EXISTS name CASCADE;")
cur.execute("DROP TABLE IF EXISTS person_info CASCADE;")
cur.execute("DROP TABLE IF EXISTS role_type CASCADE;")
cur.execute("DROP TABLE IF EXISTS title CASCADE;")

with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
    schema_sql = f.read()

# split by semicolon and run statement by statement
statements = [s.strip() for s in schema_sql.split(";") if s.strip()]

for i, stmt in enumerate(statements, start=1):
    try:
        cur.execute(stmt + ";")
        print(f"Statement {i} executed successfully.")
    except Exception as e:
        print(f"Statement {i} failed:")
        print(stmt)
        print("ERROR:", e)
        break

cur.close()
conn.close()
print("Done.")

