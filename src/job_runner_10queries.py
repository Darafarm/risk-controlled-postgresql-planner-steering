from pathlib import Path
import json
import psycopg2

# CONFIG
HOST = "127.0.0.1"
PORT = 5433
DBNAME = "imdb"
USER = "postgres"
PASSWORD = ""  

QUERIES_DIR = Path(r"C:\Users\daram\Desktop\SQL queries\join-order-benchmark-master\join-order-benchmark-master")

LIMIT = 0       # 0 = running ALL queries (113 after filtering)
WARMUP = 1
REPEATS = 3
QUERY_GROUP = "JOB"

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
    txt = path.read_text(encoding="utf-8").strip()
    return txt.rstrip(";").strip()

def set_arm(cur, arm: str):
    for cmd in RESET_CMDS:
        cur.execute(cmd)
    for cmd in ARMS[arm]:
        cur.execute(cmd)

def get_settings(cur) -> dict:
    cur.execute("""
        SELECT
          current_setting('enable_hashjoin')  AS enable_hashjoin,
          current_setting('enable_mergejoin') AS enable_mergejoin,
          current_setting('enable_nestloop')  AS enable_nestloop;
    """)
    row = cur.fetchone()
    return {
        "enable_hashjoin": row[0],
        "enable_mergejoin": row[1],
        "enable_nestloop": row[2],
    }

def explain_json(cur, query_sql: str) -> dict:
    cur.execute(EXPLAIN_PREFIX + query_sql)
    plan = cur.fetchone()[0]  # JSON array (usually length 1)
    if isinstance(plan, str):
        plan = json.loads(plan)
    return plan[0]  # first object

def execution_time_ms(plan_root: dict) -> float:
    return float(plan_root["Execution Time"])

def insert_run(cur, query_id, arm, run_idx, runtime_ms, plan_root, settings, query_sql):
    cur.execute("""
        INSERT INTO job_runs
          (query_id, arm, run_kind, run_idx, runtime_ms, plan_json, settings, query_sql, query_group)
        VALUES
          (%s, %s, 'measured', %s, %s, %s::jsonb, %s::jsonb, %s, %s)
    """, (
        query_id, arm, run_idx, runtime_ms,
        json.dumps(plan_root),
        json.dumps(settings),
        query_sql,
        QUERY_GROUP
    ))


# Main

def main():
    # Filter out setup files (not benchmark queries)
    exclude = {"schema.sql", "fkindexes.sql"}

    sql_files = sorted([
        f for f in QUERIES_DIR.glob("*.sql")
        if f.name not in exclude
    ])

    if not sql_files:
        raise RuntimeError(f"No .sql files found in: {QUERIES_DIR}")

    # Optional LIMIT (keep 0 to run all)
    if LIMIT and LIMIT > 0:
        sql_files = sql_files[:LIMIT]

    print(f"Found {len(sql_files)} benchmark .sql files (LIMIT={LIMIT}) in {QUERIES_DIR}")

    conn = psycopg2.connect(
        host=HOST, port=PORT, dbname=DBNAME, user=USER, password=PASSWORD
    )
    conn.autocommit = True
    cur = conn.cursor()

    # Sanity check DB + schema
    cur.execute("SELECT current_database(), current_schema();")
    db, schema = cur.fetchone()
    print(f"Connected to DB={db}, schema={schema}")

    for f in sql_files:
        query_id = f"job_{f.stem}"
        query_sql = read_sql(f)

        for arm in ARMS.keys():
            set_arm(cur, arm)

            # warmup (not logged)
            for _ in range(WARMUP):
                _ = explain_json(cur, query_sql)

            # measured runs (logged)
            for run_idx in range(1, REPEATS + 1):
                plan = explain_json(cur, query_sql)
                ms = execution_time_ms(plan)
                settings = get_settings(cur)

                insert_run(cur, query_id, arm, run_idx, ms, plan, settings, query_sql)
                print(f"{query_id} | {arm} | run {run_idx} | {ms:.3f} ms")

    cur.close()
    conn.close()
    print("Done")

if __name__ == "__main__":
    main()