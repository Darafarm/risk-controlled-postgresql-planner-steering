import json
from pathlib import Path

import psycopg2
from psycopg2.extras import Json


# USER SETTINGS
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5433,
    "dbname": "imdb",
    "user": "postgres",
    "password": ""   # put your password here if needed
}

QUERY_DIR = Path(r"C:\Users\daram\Desktop\SQL queries\join-order-benchmark-master\join-order-benchmark-master")

SESSION_ID = "JOB_20260228_044411"

# Start small first
LIMIT_QUERIES = None
REPEATS = 1

ARMS = {
    "default": {
        "enable_hashjoin": "on",
        "enable_mergejoin": "on",
        "enable_nestloop": "on",
    },
    "no_hashjoin": {
        "enable_hashjoin": "off",
        "enable_mergejoin": "on",
        "enable_nestloop": "on",
    },
    "no_mergejoin": {
        "enable_hashjoin": "on",
        "enable_mergejoin": "off",
        "enable_nestloop": "on",
    },
    "no_nestloop": {
        "enable_hashjoin": "on",
        "enable_mergejoin": "on",
        "enable_nestloop": "off",
    },
}


def create_table(conn):
    sql = """
    CREATE TABLE IF NOT EXISTS job_runs_with_plan (
        id SERIAL PRIMARY KEY,
        ts TIMESTAMPTZ DEFAULT NOW(),
        session_id TEXT,
        query_id TEXT,
        arm TEXT,
        run_type TEXT,
        run_idx INT,
        runtime_ms DOUBLE PRECISION,
        plan_json JSONB,
        settings JSONB
    );
    """
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


def reset_settings(cur):
    cur.execute("RESET enable_hashjoin;")
    cur.execute("RESET enable_mergejoin;")
    cur.execute("RESET enable_nestloop;")
    cur.execute("RESET geqo_seed;")


def apply_arm_settings(cur, arm_settings):
    for key, value in arm_settings.items():
        cur.execute(f"SET {key} = {value};")
    cur.execute("SET geqo_seed = 0.5;")


def load_queries(query_dir, limit=None):
    sql_files = sorted(query_dir.glob("*.sql"))

    if not sql_files:
        raise FileNotFoundError(f"No .sql files found in: {query_dir}")

    if limit is not None:
        sql_files = sql_files[:limit]

    queries = []
    for file_path in sql_files:
        query_id = file_path.stem
        sql_text = file_path.read_text(encoding="utf-8").strip()

        if sql_text.endswith(";"):
            sql_text = sql_text[:-1].strip()

        queries.append((query_id, sql_text))

    return queries


def explain_analyze_json(cur, sql_text):
    explain_sql = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {sql_text}"
    cur.execute(explain_sql)
    row = cur.fetchone()

    if row is None:
        raise RuntimeError("No EXPLAIN output returned.")

    plan_json = row[0]

    if isinstance(plan_json, str):
        plan_json = json.loads(plan_json)

    return plan_json


def extract_execution_time(plan_json):
    if not isinstance(plan_json, list) or not plan_json:
        raise ValueError("Unexpected plan JSON format.")

    top = plan_json[0]

    if "Execution Time" not in top:
        raise ValueError("Execution Time not found in EXPLAIN ANALYZE JSON.")

    return float(top["Execution Time"])


def insert_run(conn, session_id, query_id, arm, run_idx, runtime_ms, plan_json, settings):
    sql = """
    INSERT INTO job_runs_with_plan
    (session_id, query_id, arm, run_type, run_idx, runtime_ms, plan_json, settings)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """
    with conn.cursor() as cur:
        cur.execute(
            sql,
            (
                session_id,
                query_id,
                arm,
                "measured",
                run_idx,
                runtime_ms,
                Json(plan_json),
                Json(settings),
            ),
        )
    conn.commit()


def main():
    if not QUERY_DIR.exists():
        raise FileNotFoundError(f"Query directory does not exist: {QUERY_DIR}")

    queries = load_queries(QUERY_DIR, LIMIT_QUERIES)
    print(f"Found {len(queries)} query files.")

    conn = psycopg2.connect(**DB_CONFIG)

    try:
        create_table(conn)

        total_runs = len(queries) * len(ARMS) * REPEATS
        completed = 0

        for query_id, sql_text in queries:
            print(f"\n=== Query: {query_id} ===")

            for arm_name, arm_settings in ARMS.items():
                for run_idx in range(1, REPEATS + 1):
                    try:
                        with conn.cursor() as cur:
                            reset_settings(cur)
                            apply_arm_settings(cur, arm_settings)

                            print(f"Running: {query_id} | {arm_name} | repeat {run_idx}")
                            plan_json = explain_analyze_json(cur, sql_text)
                            runtime_ms = extract_execution_time(plan_json)

                        insert_run(
                            conn,
                            SESSION_ID,
                            query_id,
                            arm_name,
                            run_idx,
                            runtime_ms,
                            plan_json,
                            arm_settings,
                        )

                        completed += 1
                        print(f"Saved: {query_id} | {arm_name} | {runtime_ms:.3f} ms")

                    except Exception as e:
                        conn.rollback()
                        print(f"FAILED: {query_id} | {arm_name} | repeat {run_idx}")
                        print(f"Reason: {e}")

        print(f"\nDone. Saved {completed}/{total_runs} runs.")

    finally:
        conn.close()


if __name__ == "__main__":
    main()