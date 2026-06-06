# -*- coding: utf-8 -*-
"""
Created on Fri Feb 27 10:06:26 2026

@author: daram
"""

# import psycopg2

# conn = psycopg2.connect(host="127.0.0.1", port=5433, dbname="imdb", user="postgres", password="")
# cur = conn.cursor()
# cur.execute("SELECT current_database(), current_schema();")
# print(cur.fetchone())

# cur.execute("SELECT to_regclass('public.char_name');")
# print("public.char_name =", cur.fetchone()[0])

# cur.close()
# conn.close()

from pathlib import Path
from datetime import datetime
import random
import json
import psycopg2


# CONFIG

HOST = "127.0.0.1"
PORT = 5433
DBNAME = "imdb"
USER = "postgres"
PASSWORD = ""  # put your password if you use one

QUERIES_DIR = Path(r"C:\Users\daram\Desktop\SQL queries\join-order-benchmark-master\join-order-benchmark-master")

LIMIT = 0      # 0 = run ALL queries (113 after filtering)
WARMUP = 1
REPEATS = 3
QUERY_GROUP = "JOB"

# Reproducible randomization 
RANDOM_SEED = 0

ARMS = {
    "default": [],
    "no_hashjoin": ["SET enable_hashjoin = off;"],
    "no_mergejoin": ["SET enable_mergejoin = off;"],
    "no_nestloop": ["SET enable_nestloop = off;"],
}

RESET_CMDS = [
    "RESET enable_hashjoin;",
    "RESET enable_mergejoin;",
    "RESET enable_nestloop;",
]

EXPLAIN_PREFIX = "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) "


# Helpers

def read_sql(path: Path) -> str:
    """Read a .sql file and strip trailing semicolons."""
    txt = path.read_text(encoding="utf-8").strip()
    return txt.rstrip(";").strip()

def set_arm(cur, arm: str):
    """Reset join settings, then apply this arm's settings."""
    for cmd in RESET_CMDS:
        cur.execute(cmd)
    for cmd in ARMS[arm]:
        cur.execute(cmd)

def get_settings(cur) -> dict:
    """Snapshot the current join-related settings (for logging)."""
    cur.execute("""
        SELECT
          current_setting('enable_hashjoin'),
          current_setting('enable_mergejoin'),
          current_setting('enable_nestloop');
    """)
    row = cur.fetchone()
    return {
        "enable_hashjoin": row[0],
        "enable_mergejoin": row[1],
        "enable_nestloop": row[2],
    }

def explain_json(cur, query_sql: str) -> dict:
    """
    Run EXPLAIN ANALYZE FORMAT JSON and return the first JSON plan object.
    Postgres returns: [ { ...plan keys..., "Execution Time": ... } ]
    """
    cur.execute(EXPLAIN_PREFIX + query_sql)
    plan = cur.fetchone()[0]
    if isinstance(plan, str):
        plan = json.loads(plan)
    return plan[0]

def execution_time_ms(plan_root: dict) -> float:
    """Extract total execution time from the JSON plan (ms)."""
    return float(plan_root["Execution Time"])

def insert_run(cur, query_id, arm, run_idx, runtime_ms, plan_root, settings, query_sql,
               session_id, query_seq, arm_seq):
    """Insert one measured run into job_runs (includes session/order)."""
    cur.execute("""
        INSERT INTO job_runs
          (query_id, arm, run_kind, run_idx, runtime_ms, plan_json, settings, query_sql, query_group,
           session_id, query_seq, arm_seq)
        VALUES
          (%s, %s, 'measured', %s, %s, %s::jsonb, %s::jsonb, %s, %s,
           %s, %s, %s)
    """, (
        query_id, arm, run_idx, runtime_ms,
        json.dumps(plan_root),
        json.dumps(settings),
        query_sql,
        QUERY_GROUP,
        session_id, query_seq, arm_seq
    ))


# Main

def main():
    # Collect benchmark query files (exclude setup scripts)
    exclude = {"schema.sql", "fkindexes.sql"}
    sql_files = sorted([f for f in QUERIES_DIR.glob("*.sql") if f.name not in exclude])

    if not sql_files:
        raise RuntimeError(f"No .sql files found in: {QUERIES_DIR}")

    if LIMIT and LIMIT > 0:
        sql_files = sql_files[:LIMIT]

    #  Create a unique session id for this experimental run
    session_id = datetime.utcnow().strftime("JOB_%Y%m%d_%H%M%S")
    print(f"Session ID: {session_id}")
    print(f"Found {len(sql_files)} benchmark .sql files (LIMIT={LIMIT})")

    # Randomize order to reduce cache/order bias (reproducible with seed)
    random.seed(RANDOM_SEED)
    random.shuffle(sql_files)

    # 4) Connect to Postgres
    conn = psycopg2.connect(
        host=HOST, port=PORT, dbname=DBNAME, user=USER, password=PASSWORD
    )
    conn.autocommit = True
    cur = conn.cursor()

    # sanity check
    cur.execute("SELECT current_database(), current_schema();")
    db, schema = cur.fetchone()
    print(f"Connected to DB={db}, schema={schema}")

    # 5) Run queries
    for query_seq, f in enumerate(sql_files, start=1):
        query_id = f"job_{f.stem}"
        query_sql = read_sql(f)

        # Randomize arm order per query
        arms = list(ARMS.keys())
        random.shuffle(arms)

        for arm_seq, arm in enumerate(arms, start=1):
            set_arm(cur, arm)

            # warmup (not logged)
            for _ in range(WARMUP):
                _ = explain_json(cur, query_sql)

            # measured runs (logged)
            for run_idx in range(1, REPEATS + 1):
                plan = explain_json(cur, query_sql)
                ms = execution_time_ms(plan)
                settings = get_settings(cur)

                insert_run(cur, query_id, arm, run_idx, ms, plan, settings, query_sql,
                           session_id, query_seq, arm_seq)

                print(f"{query_id} | qseq {query_seq} | {arm} (aseq {arm_seq}) | run {run_idx} | {ms:.3f} ms")

    cur.close()
    conn.close()
    print("Done.")

if __name__ == "__main__":
    main()