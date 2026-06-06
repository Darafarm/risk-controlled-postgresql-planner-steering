import os
import time
import json
import pandas as pd
import psycopg2

QUERY_DIR = r"C:\Users\daram\Desktop\Relational DBMS ML\SQL queries\job_queries_scaled_clean"
OUTPUT_CSV = r"C:\Users\daram\Desktop\Relational DBMS ML\SQL queries\scaled_job_runs_200_safe.csv"

DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "dbname": "imdb",
    "user": "imdb",
    "password": "imdb"
}

ARMS = {
    "default": {
        "enable_hashjoin": "on",
        "enable_mergejoin": "on",
        "enable_nestloop": "on"
    },
    "no_hashjoin": {
        "enable_hashjoin": "off",
        "enable_mergejoin": "on",
        "enable_nestloop": "on"
    },
    "no_mergejoin": {
        "enable_hashjoin": "on",
        "enable_mergejoin": "off",
        "enable_nestloop": "on"
    },
    "no_nestloop": {
        "enable_hashjoin": "on",
        "enable_mergejoin": "on",
        "enable_nestloop": "off"
    }
}

REPEATS = 1
STATEMENT_TIMEOUT_MS = 60000
PILOT_N = 200


def connect_db():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"SET statement_timeout = {STATEMENT_TIMEOUT_MS};")
    return conn, cur


def set_arm(cur, arm_settings):
    for k, v in arm_settings.items():
        cur.execute(f"SET {k} TO {v};")


def reset_session(cur):
    cur.execute("RESET ALL;")
    cur.execute(f"SET statement_timeout = {STATEMENT_TIMEOUT_MS};")


def extract_plan_features(plan):
    features = {
        "root_total_cost": plan.get("Total Cost"),
        "root_plan_rows": plan.get("Plan Rows"),
        "root_plan_width": plan.get("Plan Width"),
        "hash_join_count": 0,
        "merge_join_count": 0,
        "nested_loop_count": 0,
        "seq_scan_count": 0,
        "index_scan_count": 0,
        "total_node_count": 0,
        "max_depth": 0
    }

    def walk(node, depth=1):
        features["total_node_count"] += 1
        features["max_depth"] = max(features["max_depth"], depth)

        node_type = node.get("Node Type", "")
        if node_type == "Hash Join":
            features["hash_join_count"] += 1
        elif node_type == "Merge Join":
            features["merge_join_count"] += 1
        elif node_type == "Nested Loop":
            features["nested_loop_count"] += 1
        elif node_type == "Seq Scan":
            features["seq_scan_count"] += 1
        elif node_type in ["Index Scan", "Index Only Scan", "Bitmap Index Scan"]:
            features["index_scan_count"] += 1

        for child in node.get("Plans", []):
            walk(child, depth + 1)

    walk(plan)
    return features


def run_explain_analyze(cur, sql):
    explain_sql = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {sql}"
    cur.execute(explain_sql)
    result = cur.fetchone()[0]
    return result[0]


def append_row_to_csv(row, output_csv):
    df_row = pd.DataFrame([row])
    write_header = not os.path.exists(output_csv)
    df_row.to_csv(output_csv, mode="a", header=write_header, index=False)


def main():
    query_files = sorted([f for f in os.listdir(QUERY_DIR) if f.endswith(".sql")])[:PILOT_N]
    print(f"Found {len(query_files)} queries")

    conn, cur = connect_db()

    for q_idx, file_name in enumerate(query_files, start=1):
        query_id = os.path.splitext(file_name)[0]
        file_path = os.path.join(QUERY_DIR, file_name)

        with open(file_path, "r", encoding="utf-8") as f:
            sql = f.read().strip().rstrip(";")

        print(f"\n[{q_idx}/{len(query_files)}] Running {query_id}")

        for arm_name, arm_settings in ARMS.items():
            for repeat in range(1, REPEATS + 1):
                try:
                    # reconnect if connection/cursor is broken
                    if conn.closed:
                        conn, cur = connect_db()

                    reset_session(cur)
                    set_arm(cur, arm_settings)

                    start = time.time()
                    explain_json = run_explain_analyze(cur, sql)
                    wall_ms = (time.time() - start) * 1000.0

                    plan = explain_json["Plan"]
                    exec_time = explain_json.get("Execution Time", None)
                    planning_time = explain_json.get("Planning Time", None)

                    features = extract_plan_features(plan)

                    row = {
                        "query_id": query_id,
                        "arm": arm_name,
                        "repeat": repeat,
                        "execution_time_ms": exec_time,
                        "planning_time_ms": planning_time,
                        "wall_time_ms": wall_ms,
                        "root_total_cost": features["root_total_cost"],
                        "root_plan_rows": features["root_plan_rows"],
                        "root_plan_width": features["root_plan_width"],
                        "hash_join_count": features["hash_join_count"],
                        "merge_join_count": features["merge_join_count"],
                        "nested_loop_count": features["nested_loop_count"],
                        "seq_scan_count": features["seq_scan_count"],
                        "index_scan_count": features["index_scan_count"],
                        "total_node_count": features["total_node_count"],
                        "max_depth": features["max_depth"],
                        "status": "ok",
                        "error_message": None
                    }

                    append_row_to_csv(row, OUTPUT_CSV)
                    print(f"  {arm_name} | repeat {repeat} | {exec_time:.2f} ms")

                except Exception as e:
                    # try reconnect for next iteration
                    try:
                        cur.close()
                    except Exception:
                        pass
                    try:
                        conn.close()
                    except Exception:
                        pass

                    try:
                        conn, cur = connect_db()
                    except Exception:
                        pass

                    row = {
                        "query_id": query_id,
                        "arm": arm_name,
                        "repeat": repeat,
                        "execution_time_ms": None,
                        "planning_time_ms": None,
                        "wall_time_ms": None,
                        "root_total_cost": None,
                        "root_plan_rows": None,
                        "root_plan_width": None,
                        "hash_join_count": None,
                        "merge_join_count": None,
                        "nested_loop_count": None,
                        "seq_scan_count": None,
                        "index_scan_count": None,
                        "total_node_count": None,
                        "max_depth": None,
                        "status": "error",
                        "error_message": str(e)
                    }

                    try:
                        append_row_to_csv(row, OUTPUT_CSV)
                    except Exception as csv_err:
                        print(f"  FAILED TO WRITE CSV ROW: {csv_err}")

                    print(f"  {arm_name} | repeat {repeat} | ERROR: {e}")

    try:
        cur.close()
    except Exception:
        pass
    try:
        conn.close()
    except Exception:
        pass

    print("\nDone.")
    print("Saved incrementally to:", OUTPUT_CSV)


if __name__ == "__main__":
    main()