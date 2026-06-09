# RiskSteer: Lightweight Risk-Controlled Planner Steering in PostgreSQL

**James Daramola, PhD Student** · **Priya Deshpande, Assistant Professor**  
Department of Electrical and Computer Engineering, Marquette University

> *Submitted to SSDBM 2026*

---

## Overview

RiskSteer is a lightweight, non-intrusive query planner steering system for PostgreSQL. It selects among four session-level planner configurations on a per-query basis using only features extracted from `EXPLAIN (FORMAT JSON)` output - before the query executes. A risk-controlled threshold policy falls back to the default planner when the predicted benefit of steering is insufficient, directly targeting the no-regression requirement that is essential for production deployment.

On a 904-query scaled Join Order Benchmark (JOB) workload, RiskSteer reduces total execution time by **37.3%** relative to the default PostgreSQL planner, reaching within **0.3 percentage points** of oracle performance, with **zero regressions** observed across all tested threshold values.

---

## Key Results

| Strategy | Total Runtime | vs. Default |
|---|---|---|
| Default planner | 662 s | baseline |
| Best fixed arm (`no_mergejoin`) | 611 s | −7.8% |
| **RiskSteer (τ = 0)** | **415 s** | **−37.3%** |
| Oracle (perfect) | 413 s | −37.6% |

**Pre-execution Random Forest accuracy:** 93.4% (post-execution upper bound: 95.6%)  
**Default planner p99 regret:** 7,222 ms (max: 8,115 ms on `job_26a`)  
**Regressions at any threshold value:** 0

---

## System Design

RiskSteer operates as follows:

1. A SQL query arrives at the system
2. `EXPLAIN (FORMAT JSON)` is called — no execution occurs
3. Ten scalar features are extracted from the plan tree
4. A Random Forest classifier predicts the optimal planner arm
5. The risk gate checks if the predicted saving exceeds threshold τ
6. If yes, the recommended arm settings are applied via `SET` commands before execution
7. If no, the query runs under the default planner unchanged
8. All outcomes are logged for monitoring and future retraining

**The four planner arms:**

| Arm | PostgreSQL setting |
|---|---|
| `default` | All operators enabled |
| `no_hashjoin` | `SET enable_hashjoin = off` |
| `no_mergejoin` | `SET enable_mergejoin = off` |
| `no_nestloop` | `SET enable_nestloop = off` |

---

## Repository Structure

```
RiskSteer/
│
├── data/
│   ├── tau_experiment_904.csv        # 3,616 execution samples (904 queries × 4 arms)
│   ├── model_predictions_final.csv   # RF predictions for 904 queries
│   ├── tau_sweep_results.csv         # Threshold sweep output
│   ├── feature_importance_final.csv  # Feature importance scores
│   └── model_accuracy.csv            # All 6 model accuracies
│
├── scripts/
│   ├── generate_queries.py           # Scale 113 JOB queries to 904 variants
│   ├── run_experiment.py             # Execute all query-arm combinations
│   ├── train_model.py                # Train all models + tau sweep
│   └── visualize.py                  # Generate all figures
│
├── figures/                          # All PNG figures used in the paper
│   ├── 01_oracle_arm_distribution.png
│   ├── 02_executed_arm_distribution.png
│   ├── 03_avg_runtime_by_arm.png
│   ├── 04_avg_oracle_runtime_by_arm.png
│   ├── 05_regret_distribution.png
│   ├── 06_avg_regret_by_arm.png
│   ├── 07_oracle_runtime_per_query_sorted.png
│   ├── 08_confusion_matrix_post_execution.png
│   ├── 09_confusion_matrix_pre_execution.png
│   ├── 10_feature_importance_post_execution.png
│   ├── 11_feature_importance_pre_execution.png
│   ├── 12_accuracy_comparison.png
│   ├── 13_default_vs_oracle_runtime.png
│   ├── 14_default_regret_distribution.png
│   └── 15_top20_default_regret_queries.png
│
├── paper/
│   └── main_acm.tex                  # SSDBM 2026 submission (ACM SIGCONF format)
│
├── requirements.txt
└── README.md
```

---

## Features

Ten scalar features are extracted from `EXPLAIN (FORMAT JSON)` before query execution. All are available before the query runs — no execution required.

| Feature | Description |
|---|---|
| `root_total_cost` | PostgreSQL total cost estimate at root node |
| `root_plan_rows` | Estimated output row count |
| `root_plan_width` | Estimated tuple width in bytes |
| `hash_join_count` | Number of hash join operators in the plan |
| `merge_join_count` | Number of merge join operators in the plan |
| `nested_loop_count` | Number of nested loop operators in the plan |
| `seq_scan_count` | Number of sequential scan operators |
| `index_scan_count` | Number of index scan operators |
| `total_node_count` | Total number of operators in the plan tree |
| `max_depth` | Maximum depth of the plan tree |

`root_total_cost` accounts for 45.8% of the model's predictive importance. Structural features contribute the remaining 54.2%, confirming the model learns beyond simple cost thresholding.

---

## Setup and Requirements

### Prerequisites

- Python 3.9+
- PostgreSQL running locally or in Docker with the IMDB dataset loaded
- The canonical JOB query set

### Installation

```bash
git clone https://github.com/Darafarm/TrustVision.git
cd TrustVision
pip install -r requirements.txt
```

### Requirements

```
scikit-learn>=1.3.0
xgboost>=2.0.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
psycopg2-binary>=2.9.0
```

### Database Setup

Start PostgreSQL with the IMDB dataset:

```bash
docker start imdb_bao_test
```

The experiments were run against a PostgreSQL instance in Docker on port 5433. Update the connection string in `run_experiment.py` to match your setup.

---

## Reproducing the Experiments

### Step 1 : Generate the scaled workload

Scale the 113 canonical JOB queries to 904 variants by varying numeric ranges in `BETWEEN` and `LIMIT` clauses:

```bash
python scripts/generate_queries.py
```

### Step 2 : Run the experiment

Execute all 3,616 query-arm combinations (904 queries × 4 arms) with 3 repeats each. Execution order is fully randomized (seed = 42) to eliminate cache warm-up bias:

```bash
python scripts/run_experiment.py
```

Total runtime is approximately 7 hours on a local machine. Output is written to `data/tau_experiment_904.csv`.

### Step 3 : Train the model and run the threshold sweep

Train all six model families under 5-fold stratified cross-validation and run the tau sweep from 0 to 5,000 ms:

```bash
python scripts/train_model.py
```

### Step 4 : Generate figures

```bash
python scripts/visualize.py
```

All figures are written to the `figures/` directory.

---

## Experimental Protocol

| Setting | Value |
|---|---|
| Workload | 904 scaled JOB queries (from 113 templates) |
| Arms | default, no_hashjoin, no_mergejoin, no_nestloop |
| Repeats per (query, arm) | 3 |
| Execution order | Fully randomized (seed = 42) |
| Cache regime | Warm cache |
| Total runs | 10,848 (904 × 4 × 3) |
| Oracle arm selection | Per-query minimum median runtime |
| ML evaluation | 5-fold stratified cross-validation |
| Train/test split (scaled) | 80/20 by query |

---

## Model Comparison

All models evaluated under identical 5-fold stratified cross-validation conditions on the 904-query workload.

| Model | 5-Fold CV Accuracy |
|---|---|
| Random Forest | 57.3% |
| Extra Trees | 57.2% |
| Decision Tree | 56.9% |
| XGBoost | 56.1% |
| Gradient Boosting | 54.3% |
| Logistic Regression | 32.7% |
| Majority-class baseline | 25.0% |

Random Forest was selected as the primary model based on training stability and natural feature importance reporting.

---

## Risk-Controlled Threshold Policy

The threshold τ controls the tradeoff between steering aggressiveness and regression safety:

| τ (ms) | Queries steered | Improvement | Regressions >5% |
|---|---|---|---|
| 0 | 469 | 37.3% | 0.0% |
| 100 | 141 | 38.5% | 0.0% |
| 500 | 113 | 37.6% | 0.0% |
| 1000 | 104 | 36.6% | 0.0% |
| 5000 | 8 | 7.8% | 0.0% |

Zero regressions were observed at all tested threshold values. The recommended deployment starting point is **τ = 100**, which captures the majority of the improvement while limiting steering to cases with confidently large predicted savings.

---

## Citation

This paper is currently under review. If you use this code or experimental results in your own work, please cite the preprint as:

```bibtex
@article{daramola2026risksteer,
  author    = {James Daramola and Priya Deshpande},
  title     = {Lightweight Risk-Controlled Planner Steering in {PostgreSQL}},
  year      = {2026},
  note      = {Manuscript submitted for publication}
}
```

This entry will be updated with full venue, DOI, and page numbers upon acceptance.

---

## License

This repository is made available for research and reproducibility purposes. The IMDB dataset and JOB query set are subject to their own respective licenses.

---

## Contact

James Daramola — james.daramola@marquette.edu  
Priya Deshpande — priya.deshpande@marquette.edu  
Department of Electrical and Computer Engineering, Marquette University
