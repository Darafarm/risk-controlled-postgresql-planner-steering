SQL Queries for Experimental Analysis
Base Table Assumption
-- Main experiment table
-- Replace experiment_runs with your actual table name if different.
SELECT *
FROM experiment_runs
LIMIT 5;

--- Check Dataset Size and Valid Runs
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT query_id) AS unique_queries,
    COUNT(DISTINCT arm) AS unique_arms
FROM experiment_runs;
SELECT
    status,
    COUNT(*) AS count
FROM experiment_runs
GROUP BY status;

--- Average Runtime per Planner Arm
SELECT
    arm,
    ROUND(AVG(execution_time_ms)::numeric, 2) AS avg_runtime_ms,
    ROUND(MIN(execution_time_ms)::numeric, 2) AS min_runtime_ms,
    ROUND(MAX(execution_time_ms)::numeric, 2) AS max_runtime_ms,
    COUNT(*) AS runs
FROM experiment_runs
WHERE status = 'ok'
GROUP BY arm
ORDER BY avg_runtime_ms;

--- Oracle Arm per Query
WITH oracle AS (
    SELECT
        query_id,
        arm AS oracle_arm,
        execution_time_ms AS oracle_time_ms,
        ROW_NUMBER() OVER (
            PARTITION BY query_id
            ORDER BY execution_time_ms ASC
        ) AS rn
    FROM experiment_runs
    WHERE status = 'ok'
)
SELECT
    query_id,
    oracle_arm,
    oracle_time_ms
FROM oracle
WHERE rn = 1
ORDER BY query_id;

---- Oracle Arm Distribution
WITH oracle AS (
    SELECT
        query_id,
        arm AS oracle_arm,
        execution_time_ms AS oracle_time_ms,
        ROW_NUMBER() OVER (
            PARTITION BY query_id
            ORDER BY execution_time_ms ASC
        ) AS rn
    FROM experiment_runs
    WHERE status = 'ok'
)
SELECT
    oracle_arm,
    COUNT(*) AS query_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM oracle
WHERE rn = 1
GROUP BY oracle_arm
ORDER BY query_count DESC;

--- How Often Is Default the Best Arm?
WITH oracle AS (
    SELECT
        query_id,
        arm AS oracle_arm,
        execution_time_ms AS oracle_time_ms,
        ROW_NUMBER() OVER (
            PARTITION BY query_id
            ORDER BY execution_time_ms ASC
        ) AS rn
    FROM experiment_runs
    WHERE status = 'ok'
)
SELECT
    COUNT(*) AS total_queries,
    SUM(CASE WHEN oracle_arm = 'default' THEN 1 ELSE 0 END) AS default_best_queries,
    ROUND(
        100.0 * SUM(CASE WHEN oracle_arm = 'default' THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS default_best_percentage
FROM oracle
WHERE rn = 1;

--- Default Planner Regret per Query
WITH oracle AS (
    SELECT
        query_id,
        arm AS oracle_arm,
        execution_time_ms AS oracle_time_ms,
        ROW_NUMBER() OVER (
            PARTITION BY query_id
            ORDER BY execution_time_ms ASC
        ) AS rn
    FROM experiment_runs
    WHERE status = 'ok'
),
default_runs AS (
    SELECT
        query_id,
        execution_time_ms AS default_time_ms
    FROM experiment_runs
    WHERE status = 'ok'
      AND arm = 'default'
)
SELECT
    d.query_id,
    d.default_time_ms,
    o.oracle_arm,
    o.oracle_time_ms,
    d.default_time_ms - o.oracle_time_ms AS default_regret_ms
FROM default_runs d
JOIN oracle o
    ON d.query_id = o.query_id
WHERE o.rn = 1
ORDER BY default_regret_ms DESC;


--- Default Regret Summary: Mean, Median, p95, p99
WITH oracle AS (
    SELECT
        query_id,
        arm AS oracle_arm,
        execution_time_ms AS oracle_time_ms,
        ROW_NUMBER() OVER (
            PARTITION BY query_id
            ORDER BY execution_time_ms ASC
        ) AS rn
    FROM experiment_runs
    WHERE status = 'ok'
),
default_regret AS (
    SELECT
        d.query_id,
        d.execution_time_ms AS default_time_ms,
        o.oracle_time_ms,
        d.execution_time_ms - o.oracle_time_ms AS regret_ms
    FROM experiment_runs d
    JOIN oracle o
        ON d.query_id = o.query_id
    WHERE d.status = 'ok'
      AND d.arm = 'default'
      AND o.rn = 1
)
SELECT
    ROUND(AVG(regret_ms)::numeric, 2) AS mean_regret_ms,
    ROUND(
        percentile_cont(0.50) WITHIN GROUP (ORDER BY regret_ms)::numeric,
        2
    ) AS median_regret_ms,
    ROUND(
        percentile_cont(0.95) WITHIN GROUP (ORDER BY regret_ms)::numeric,
        2
    ) AS p95_regret_ms,
    ROUND(
        percentile_cont(0.99) WITHIN GROUP (ORDER BY regret_ms)::numeric,
        2
    ) AS p99_regret_ms,
    ROUND(MAX(regret_ms)::numeric, 2) AS max_regret_ms
FROM default_regret;

--- Total Runtime per Arm
SELECT
    arm,
    ROUND(SUM(execution_time_ms)::numeric, 2) AS total_runtime_ms,
    ROUND((SUM(execution_time_ms) / 1000.0)::numeric, 2) AS total_runtime_sec
FROM experiment_runs
WHERE status = 'ok'
GROUP BY arm
ORDER BY total_runtime_ms;


--- Best Fixed Arm
SELECT
    arm AS best_fixed_arm,
    ROUND(SUM(execution_time_ms)::numeric, 2) AS total_runtime_ms
FROM experiment_runs
WHERE status = 'ok'
GROUP BY arm
ORDER BY total_runtime_ms
LIMIT 1;

--- Default vs Best Fixed vs Oracle Runtime
WITH arm_totals AS (
    SELECT
        arm,
        SUM(execution_time_ms) AS total_runtime_ms
    FROM experiment_runs
    WHERE status = 'ok'
    GROUP BY arm
),
oracle AS (
    SELECT
        query_id,
        execution_time_ms AS oracle_time_ms,
        ROW_NUMBER() OVER (
            PARTITION BY query_id
            ORDER BY execution_time_ms ASC
        ) AS rn
    FROM experiment_runs
    WHERE status = 'ok'
),
summary AS (
    SELECT
        (SELECT total_runtime_ms FROM arm_totals WHERE arm = 'default') AS default_runtime_ms,
        (SELECT MIN(total_runtime_ms) FROM arm_totals) AS best_fixed_runtime_ms,
        (SELECT SUM(oracle_time_ms) FROM oracle WHERE rn = 1) AS oracle_runtime_ms
)
SELECT
    ROUND(default_runtime_ms::numeric, 2) AS default_runtime_ms,
    ROUND(best_fixed_runtime_ms::numeric, 2) AS best_fixed_runtime_ms,
    ROUND(oracle_runtime_ms::numeric, 2) AS oracle_runtime_ms,
    ROUND(
        100.0 * (default_runtime_ms - best_fixed_runtime_ms) / default_runtime_ms,
        2
    ) AS best_fixed_improvement_pct,
    ROUND(
        100.0 * (default_runtime_ms - oracle_runtime_ms) / default_runtime_ms,
        2
    ) AS oracle_improvement_pct
FROM summary;


--- Runtime Tail Metrics per Arm
SELECT
    arm,
    ROUND(AVG(execution_time_ms)::numeric, 2) AS mean_runtime_ms,
    ROUND(
        percentile_cont(0.50) WITHIN GROUP (ORDER BY execution_time_ms)::numeric,
        2
    ) AS median_runtime_ms,
    ROUND(
        percentile_cont(0.95) WITHIN GROUP (ORDER BY execution_time_ms)::numeric,
        2
    ) AS p95_runtime_ms,
    ROUND(
        percentile_cont(0.99) WITHIN GROUP (ORDER BY execution_time_ms)::numeric,
        2
    ) AS p99_runtime_ms,
    ROUND(MAX(execution_time_ms)::numeric, 2) AS max_runtime_ms
FROM experiment_runs
WHERE status = 'ok'
GROUP BY arm
ORDER BY mean_runtime_ms;

--- Feature Summary by Oracle Arm
WITH oracle AS (
    SELECT
        query_id,
        arm AS oracle_arm,
        execution_time_ms AS oracle_time_ms,
        ROW_NUMBER() OVER (
            PARTITION BY query_id
            ORDER BY execution_time_ms ASC
        ) AS rn
    FROM experiment_runs
    WHERE status = 'ok'
),
features AS (
    SELECT DISTINCT ON (query_id)
        query_id,
        root_total_cost,
        root_plan_rows,
        root_plan_width,
        hash_join_count,
        merge_join_count,
        nested_loop_count,
        seq_scan_count,
        index_scan_count,
        total_node_count,
        max_depth
    FROM experiment_runs
    WHERE status = 'ok'
    ORDER BY query_id, execution_sequence
)
SELECT
    o.oracle_arm,
    COUNT(*) AS query_count,
    ROUND(AVG(f.root_total_cost)::numeric, 2) AS avg_root_total_cost,
    ROUND(AVG(f.total_node_count)::numeric, 2) AS avg_total_node_count,
    ROUND(AVG(f.max_depth)::numeric, 2) AS avg_max_depth,
    ROUND(AVG(f.hash_join_count)::numeric, 2) AS avg_hash_joins,
    ROUND(AVG(f.merge_join_count)::numeric, 2) AS avg_merge_joins,
    ROUND(AVG(f.nested_loop_count)::numeric, 2) AS avg_nested_loops
FROM oracle o
JOIN features f
    ON o.query_id = f.query_id
WHERE o.rn = 1
GROUP BY o.oracle_arm
ORDER BY query_count DESC;


--- Queries with Largest Default Regret
WITH oracle AS (
    SELECT
        query_id,
        arm AS oracle_arm,
        execution_time_ms AS oracle_time_ms,
        ROW_NUMBER() OVER (
            PARTITION BY query_id
            ORDER BY execution_time_ms ASC
        ) AS rn
    FROM experiment_runs
    WHERE status = 'ok'
),
default_runs AS (
    SELECT
        query_id,
        execution_time_ms AS default_time_ms
    FROM experiment_runs
    WHERE status = 'ok'
      AND arm = 'default'
)
SELECT
    d.query_id,
    d.default_time_ms,
    o.oracle_arm,
    o.oracle_time_ms,
    d.default_time_ms - o.oracle_time_ms AS default_regret_ms
FROM default_runs d
JOIN oracle o
    ON d.query_id = o.query_id
WHERE o.rn = 1
ORDER BY default_regret_ms DESC
LIMIT 20;


--- Arm Runtime Comparison for a Single Query
SELECT
    query_id,
    arm,
    execution_time_ms,
    planning_time_ms,
    root_total_cost,
    hash_join_count,
    merge_join_count,
    nested_loop_count,
    seq_scan_count,
    index_scan_count,
    total_node_count,
    max_depth
FROM experiment_runs
WHERE query_id = 'q0'
  AND status = 'ok'
ORDER BY execution_time_ms;
Change 'q0' to any query you want.


--- Regression Check Against Default
This checks how often each non-default arm is slower than default.
WITH default_runs AS (
    SELECT
        query_id,
        execution_time_ms AS default_time_ms
    FROM experiment_runs
    WHERE status = 'ok'
      AND arm = 'default'
),
other_arms AS (
    SELECT
        query_id,
        arm,
        execution_time_ms
    FROM experiment_runs
    WHERE status = 'ok'
      AND arm <> 'default'
)
SELECT
    o.arm,
    COUNT(*) AS total_queries,
    SUM(CASE WHEN o.execution_time_ms > d.default_time_ms THEN 1 ELSE 0 END) AS regressions,
    ROUND(
        100.0 * SUM(CASE WHEN o.execution_time_ms > d.default_time_ms THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS regression_rate_pct
FROM other_arms o
JOIN default_runs d
    ON o.query_id = d.query_id
GROUP BY o.arm
ORDER BY regression_rate_pct DESC;


--- Regression Rate at 5% and 10% Tolerance
WITH default_runs AS (
    SELECT
        query_id,
        execution_time_ms AS default_time_ms
    FROM experiment_runs
    WHERE status = 'ok'
      AND arm = 'default'
),
other_arms AS (
    SELECT
        query_id,
        arm,
        execution_time_ms
    FROM experiment_runs
    WHERE status = 'ok'
      AND arm <> 'default'
)
SELECT
    o.arm,
    COUNT(*) AS total_queries,
    SUM(CASE WHEN o.execution_time_ms > 1.05 * d.default_time_ms THEN 1 ELSE 0 END) AS regressions_over_5pct,
    SUM(CASE WHEN o.execution_time_ms > 1.10 * d.default_time_ms THEN 1 ELSE 0 END) AS regressions_over_10pct,
    ROUND(
        100.0 * SUM(CASE WHEN o.execution_time_ms > 1.05 * d.default_time_ms THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS regression_5pct_rate,
    ROUND(
        100.0 * SUM(CASE WHEN o.execution_time_ms > 1.10 * d.default_time_ms THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS regression_10pct_rate
FROM other_arms o
JOIN default_runs d
    ON o.query_id = d.query_id
GROUP BY o.arm
ORDER BY regression_5pct_rate DESC;

--- Execution Order Check
SELECT
    MIN(execution_sequence) AS first_run,
    MAX(execution_sequence) AS last_run,
    COUNT(*) AS total_runs
FROM experiment_runs;
SELECT
    arm,
    MIN(execution_sequence) AS first_seen,
    MAX(execution_sequence) AS last_seen,
    COUNT(*) AS count
FROM experiment_runs
GROUP BY arm
ORDER BY arm;


--- Arm Order Randomization Check
SELECT
    arm_order,
    COUNT(*) AS occurrences
FROM experiment_runs
GROUP BY arm_order
ORDER BY occurrences DESC;


--- Warm Cache Regime Check
SELECT
    cache_regime,
    COUNT(*) AS count
FROM experiment_runs
GROUP BY cache_regime;

--- Create Oracle + Regret View
Use this view so you do not need to repeat the oracle CTE every time.
CREATE OR REPLACE VIEW experiment_with_regret AS
WITH oracle AS (
    SELECT
        query_id,
        arm AS oracle_arm,
        execution_time_ms AS oracle_time_ms,
        ROW_NUMBER() OVER (
            PARTITION BY query_id
            ORDER BY execution_time_ms ASC
        ) AS rn
    FROM experiment_runs
    WHERE status = 'ok'
)
SELECT
    r.*,
    o.oracle_arm,
    o.oracle_time_ms,
    r.execution_time_ms - o.oracle_time_ms AS regret_ms
FROM experiment_runs r
JOIN oracle o
    ON r.query_id = o.query_id
WHERE r.status = 'ok'
  AND o.rn = 1;
After creating the view, you can run simpler queries like:
SELECT *
FROM experiment_with_regret
LIMIT 10;

--- Average Regret per Arm
SELECT
    arm,
    ROUND(AVG(regret_ms)::numeric, 2) AS avg_regret_ms,
    ROUND(
        percentile_cont(0.95) WITHIN GROUP (ORDER BY regret_ms)::numeric,
        2
    ) AS p95_regret_ms,
    ROUND(
        percentile_cont(0.99) WITHIN GROUP (ORDER BY regret_ms)::numeric,
        2
    ) AS p99_regret_ms,
    ROUND(MAX(regret_ms)::numeric, 2) AS max_regret_ms
FROM experiment_with_regret
GROUP BY arm
ORDER BY avg_regret_ms;

--- Export Oracle Table
CREATE TABLE oracle_scaled_904 AS
WITH ranked AS (
    SELECT
        query_id,
        arm AS oracle_arm,
        execution_time_ms AS oracle_time_ms,
        ROW_NUMBER() OVER (
            PARTITION BY query_id
            ORDER BY execution_time_ms ASC
        ) AS rn
    FROM experiment_runs
    WHERE status = 'ok'
)
SELECT
    query_id,
    oracle_arm,
    oracle_time_ms
FROM ranked
WHERE rn = 1;


--- Export Regret Table
CREATE TABLE regret_scaled_904 AS
WITH oracle AS (
    SELECT
        query_id,
        arm AS oracle_arm,
        execution_time_ms AS oracle_time_ms,
        ROW_NUMBER() OVER (
            PARTITION BY query_id
            ORDER BY execution_time_ms ASC
        ) AS rn
    FROM experiment_runs
    WHERE status = 'ok'
)
SELECT
    r.*,
    o.oracle_arm,
    o.oracle_time_ms,
    r.execution_time_ms - o.oracle_time_ms AS regret_ms
FROM experiment_runs r
JOIN oracle o
    ON r.query_id = o.query_id
WHERE r.status = 'ok'
  AND o.rn = 1;
