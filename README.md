# Risk-Controlled Planner Steering in PostgreSQL

This repository contains code and experiments for lightweight learned planner steering in PostgreSQL using the Join Order Benchmark (JOB).

## Main Results

- 904 scaled JOB queries
- Random Forest learned policy
- ~39% workload runtime improvement over PostgreSQL default
- Near-oracle performance

## Structure

- src/: experiment and training scripts
- queries/: JOB queries and scaled variants
- results/: experiment outputs
- figures/: plots and visualizations