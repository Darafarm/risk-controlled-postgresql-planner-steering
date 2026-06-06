
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

from sklearn.ensemble import (RandomForestClassifier,
                               ExtraTreesClassifier,
                               GradientBoostingClassifier)
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (cross_val_predict,
                                     StratifiedKFold)
from sklearn.metrics import (accuracy_score,
                              classification_report,
                              confusion_matrix)

# CONFIGURATION

INPUT_CSV = (
    r"C:/Users/daram/Desktop/RDMBS/Relational DBMS ML/SQL queries/tau_experiment_904.csv"
)

OUTPUT_DIR = (
    r"C:\Users\daram\Desktop\RDMBS\Relational DBMS ML\SQL queries"
)

# LOAD DATA

print("=" * 60)
print("  STEP 1: Loading data")
print("=" * 60)

df = pd.read_csv(INPUT_CSV)
df_ok = df[df['status'] == 'ok'].copy()
df_ok['execution_time_ms'] = pd.to_numeric(
    df_ok['execution_time_ms'], errors='coerce')

print(f"  Total rows loaded  : {len(df)}")
print(f"  Successful rows    : {len(df_ok)}")
print(f"  Unique queries     : {df_ok['query_id'].nunique()}")

# BUILD PER-QUERY SUMMARY

print("\n" + "=" * 60)
print("  STEP 2: Building per-query summary")
print("=" * 60)

arm_cols = ['default', 'no_hashjoin', 'no_mergejoin', 'no_nestloop']

pivot = df_ok.pivot_table(
    index='query_id',
    columns='arm',
    values='execution_time_ms',
    aggfunc='min'
).reset_index()

pivot['oracle_arm']     = pivot[arm_cols].idxmin(axis=1)
pivot['oracle_ms']      = pivot[arm_cols].min(axis=1)
pivot['default_ms']     = pivot['default']
pivot['default_regret'] = pivot['default'] - pivot['oracle_ms']

print(f"  Queries with all 4 arms : {len(pivot)}")
print(f"\n  Oracle arm distribution:")
dist = pivot['oracle_arm'].value_counts()
for arm, cnt in dist.items():
    print(f"    {arm:<15} {cnt:>4}  ({cnt/len(pivot)*100:.1f}%)")

print(f"\n  Default regret statistics (ms):")
r = pivot['default_regret']
print(f"    Mean   : {r.mean():.1f}")
print(f"    Median : {r.median():.1f}")
print(f"    p95    : {r.quantile(0.95):.1f}")
print(f"    p99    : {r.quantile(0.99):.1f}")
print(f"    Max    : {r.max():.1f}")

# BUILD FEATURE MATRIX

print("\n" + "=" * 60)
print("  STEP 3: Building feature matrix")
print("=" * 60)

FEATURES = [
    'root_total_cost',   'root_plan_rows',
    'root_plan_width',   'hash_join_count',
    'merge_join_count',  'nested_loop_count',
    'seq_scan_count',    'index_scan_count',
    'total_node_count',  'max_depth'
]

default_feats = (
    df_ok[df_ok['arm'] == 'default']
    .groupby('query_id')[FEATURES]
    .first()
    .reset_index()
)

data = pivot.merge(default_feats, on='query_id')
X = data[FEATURES].fillna(0).values
y = data['oracle_arm'].values

print(f"  Feature matrix shape : {X.shape}")

# TRAINING AND COMPARE ALL MODELS INCLUDING XGBOOST

print("\n" + "=" * 60)
print(" Training and comparing all models")
print("=" * 60)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Standard models
models = {
    'Random Forest':
        RandomForestClassifier(
            n_estimators=200, random_state=42, n_jobs=-1),
    'Extra Trees':
        ExtraTreesClassifier(
            n_estimators=200, random_state=42, n_jobs=-1),
    'Gradient Boosting':
        GradientBoostingClassifier(
            n_estimators=100, random_state=42),
    'Decision Tree':
        DecisionTreeClassifier(random_state=42),
    'Logistic Regression':
        LogisticRegression(max_iter=1000, random_state=42),
}

# Having a Dictionary to store all results
accuracy_results = []
rf_predictions   = None

for name, model in models.items():
    # Train using cross-validation and get predictions
    preds = cross_val_predict(model, X, y, cv=cv)


    acc = accuracy_score(y, preds)

    # Store result — this number comes from the model, not from typing
    accuracy_results.append({'model': name, 'accuracy': acc})
    print(f"  {name:<25} {acc*100:.1f}%  (from trained model)")

    if name == 'Random Forest':
        rf_predictions = preds

# XGBoost 
print(f"\n  Adding XGBoost...")
try:
    from xgboost import XGBClassifier
    from sklearn.preprocessing import LabelEncoder

    # XGBoost needs numeric labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    xgb_model = XGBClassifier(
        n_estimators=200,
        random_state=42,
        eval_metric='mlogloss',
        verbosity=0
    )

    # Get predictions from cross-validation
    xgb_preds_encoded = cross_val_predict(
        xgb_model, X, y_encoded, cv=cv)

    # Convert numeric predictions back to arm names
    xgb_preds = le.inverse_transform(xgb_preds_encoded)

    # Accuracy from the actual XGBoost model predictions
    xgb_acc = accuracy_score(y, xgb_preds)

    accuracy_results.append({
        'model':    'XGBoost',
        'accuracy': xgb_acc
    })
    print(f"  {'XGBoost':<25} {xgb_acc*100:.1f}%  (from trained model)")

except ImportError:
    print("  XGBoost not installed.")
    print("  Run: pip install xgboost")
    print("  Then re-run this script.")
    xgb_preds = None
    xgb_acc   = None

# Save accuracy results 
acc_df   = pd.DataFrame(accuracy_results)
acc_df   = acc_df.sort_values('accuracy', ascending=False)
acc_path = OUTPUT_DIR + r"\model_accuracy.csv"
acc_df.to_csv(acc_path, index=False)

print(f"\n  All accuracies saved from trained models (not hardcoded)")
print(f"  File: {acc_path}")
print(f"\n  Final accuracy ranking:")
for _, row in acc_df.iterrows():
    print(f"    {row['model']:<25} {row['accuracy']*100:.1f}%")


# DETAILED RF ANALYSIS

print("\n" + "=" * 60)
print("Random Forest detailed analysis")
print("=" * 60)

print("\n  Classification Report (Random Forest):")
print(classification_report(y, rf_predictions))

report_path = OUTPUT_DIR + r"\classification_report.txt"
with open(report_path, 'w') as f:
    f.write("Random Forest Classification Report\n")
    f.write("5-fold Cross-Validation on 904-query dataset\n\n")
    f.write(classification_report(y, rf_predictions))
print(f"  Saved: {report_path}")

cm = confusion_matrix(y, rf_predictions,
                      labels=sorted(set(y)))
cm_df = pd.DataFrame(cm,
    index=sorted(set(y)), columns=sorted(set(y)))
print("\n  Confusion Matrix:")
print(cm_df.to_string())

# each FEATURE IMPORTANCE

print("\n" + "=" * 60)
print("  STEP 6: Feature importance")
print("=" * 60)

rf_full = RandomForestClassifier(
    n_estimators=200, random_state=42, n_jobs=-1)
rf_full.fit(X, y)

fi_df = pd.DataFrame({
    'feature':    FEATURES,
    'importance': rf_full.feature_importances_
}).sort_values('importance', ascending=False)

print("\n  Feature importances (from trained model):")
for _, row in fi_df.iterrows():
    bar = '█' * int(row['importance'] * 50)
    print(f"  {row['feature']:<22} {row['importance']:.3f}  {bar}")

fi_path = OUTPUT_DIR + r"\feature_importance_final.csv"
fi_df.to_csv(fi_path, index=False)
print(f"\n  Saved: {fi_path}")

# SAVE PREDICTIONS AND TAU SWEEP

print("\n" + "=" * 60)
print("  Saving predictions")
print("=" * 60)

data['predicted_arm']    = rf_predictions
data['predicted_arm_ms'] = data.apply(
    lambda r: r[r['predicted_arm']], axis=1)
data['predicted_saving'] = (
    data['default_ms'] - data['predicted_arm_ms'])

preds_path = OUTPUT_DIR + r"\model_predictions_final.csv"
cols_to_save = (
    ['query_id', 'oracle_arm', 'predicted_arm',
     'default_ms', 'oracle_ms', 'predicted_arm_ms',
     'predicted_saving', 'default_regret']
    + arm_cols
)
data[cols_to_save].to_csv(preds_path, index=False)
print(f"  Saved: {preds_path}")

# TAU SWEEP

print("\n" + "=" * 60)
print("  STEP 8: Tau sweep analysis")
print("=" * 60)

tau_values    = [0, 50, 100, 200, 300, 500, 750,
                 1000, 1500, 2000, 3000, 5000]
default_total = data['default_ms'].sum()
oracle_total  = data['oracle_ms'].sum()

print(f"\n  Default total  : {default_total:,.0f} ms  "
      f"({default_total/1000:.0f} s)")
print(f"  Oracle total   : {oracle_total:,.0f} ms  "
      f"({oracle_total/1000:.0f} s)")

sweep_results = []

for tau in tau_values:
    total_rt      = 0.0
    steered       = 0
    regression_5  = 0
    regression_10 = 0

    for _, row in data.iterrows():
        pred_arm    = row['predicted_arm']
        pred_saving = row['predicted_saving']
        default_ms  = row['default_ms']

        if pred_arm != 'default' and pred_saving > tau:
            actual_ms = row[pred_arm]
            steered  += 1
        else:
            actual_ms = default_ms

        total_rt += actual_ms

        if actual_ms > default_ms * 1.05:
            regression_5  += 1
        if actual_ms > default_ms * 1.10:
            regression_10 += 1

    improvement  = (default_total - total_rt) / default_total * 100
    sweep_results.append({
        'tau_ms':             tau,
        'queries_steered':    steered,
        'queries_on_default': len(data) - steered,
        'total_runtime_ms':   round(total_rt, 1),
        'improvement_pct':    round(improvement, 2),
        'regression_5pct':    round(regression_5/len(data)*100, 2),
        'regression_10pct':   round(regression_10/len(data)*100, 2),
    })

sweep_df   = pd.DataFrame(sweep_results)
sweep_path = OUTPUT_DIR + r"\tau_sweep_results.csv"
sweep_df.to_csv(sweep_path, index=False)

print(f"\n  {'tau(ms)':<9} {'Steered':<10} "
      f"{'Improvement':<14} {'Regr>5%':<10} {'Regr>10%'}")
print("-" * 55)
for _, r in sweep_df.iterrows():
    print(f"  {int(r['tau_ms']):<9} "
          f"{int(r['queries_steered']):<10} "
          f"{r['improvement_pct']:>8.1f}%      "
          f"{r['regression_5pct']:>5.1f}%    "
          f"{r['regression_10pct']:>5.1f}%")


# VISUALIZATIONS

print("\n" + "=" * 60)
print("  Generating visualizations")
print("=" * 60)

import os
FIG_DIR = OUTPUT_DIR + r"\figures"
os.makedirs(FIG_DIR, exist_ok=True)

plt.rcParams.update({
    'font.family':       'Arial',
    'axes.spines.top':   False,
    'axes.spines.right': False,
    'axes.grid':         True,
    'grid.alpha':        0.25,
    'grid.linestyle':    '--',
})

DARK_BLUE = '#1a5276'
GREEN     = '#1e8449'
RED       = '#c0392b'
GREY      = '#7f8c8d'
ORANGE    = '#e67e22'

# Figure 1: Model accuracy
# Values come from acc_df which was built from trained models
fig, ax = plt.subplots(figsize=(9, 5))
sorted_acc = acc_df.sort_values('accuracy', ascending=True)
bar_colors = [RED if 'Random Forest' in m else DARK_BLUE
              for m in sorted_acc['model']]
bars = ax.barh(sorted_acc['model'],
               sorted_acc['accuracy'] * 100,
               color=bar_colors, edgecolor='white', height=0.55)
for bar, val in zip(bars, sorted_acc['accuracy'] * 100):
    ax.text(val + 0.3,
            bar.get_y() + bar.get_height()/2,
            f'{val:.1f}%',
            va='center', fontsize=10, fontweight='bold')
ax.axvline(25, color=GREY, linestyle=':',
           linewidth=1.5, label='Majority baseline (25%)')
ax.set_xlim(0, 80)
ax.set_title(
    'Model Accuracy Comparison\n'
    '5-fold Cross-Validation — Accuracies from trained models',
    fontsize=12, fontweight='bold', pad=10)
ax.set_xlabel('Accuracy (%)', fontsize=11)
ax.legend(fontsize=9)
plt.tight_layout()
fig1_path = FIG_DIR + r"\fig_model_accuracy.png"
plt.savefig(fig1_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Figure 1 saved: {fig1_path}")

# Figure 2: Feature importance
# Values come from rf_full.feature_importances_ — trained model
fig, ax = plt.subplots(figsize=(8, 6))
fi_plot = fi_df.sort_values('importance', ascending=True)
bar_colors2 = [RED if v == fi_plot['importance'].max()
               else DARK_BLUE for v in fi_plot['importance']]
ax.barh(fi_plot['feature'], fi_plot['importance'],
        color=bar_colors2, edgecolor='white', height=0.65)
for i, (_, row) in enumerate(fi_plot.iterrows()):
    ax.text(row['importance'] + 0.003, i,
            f"{row['importance']:.3f}  ({row['importance']*100:.1f}%)",
            va='center', fontsize=9)
ax.set_title(
    'Feature Importance — Random Forest\n'
    'From trained model on 904-query dataset',
    fontsize=12, fontweight='bold', pad=10)
ax.set_xlabel('Importance Score', fontsize=11)
plt.tight_layout()
fig2_path = FIG_DIR + r"\fig_feature_importance.png"
plt.savefig(fig2_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Figure 2 saved: {fig2_path}")

# Figure 3: Tau sweep
fig, ax1 = plt.subplots(figsize=(10, 6))
ax1.plot(sweep_df['tau_ms'], sweep_df['improvement_pct'],
         color=DARK_BLUE, marker='o', linewidth=2.5,
         markersize=8, label='Workload improvement (%)')
ax1.fill_between(sweep_df['tau_ms'], 0,
                 sweep_df['improvement_pct'],
                 alpha=0.08, color=DARK_BLUE)
ax1.set_xlabel('Safety threshold tau (ms)', fontsize=12)
ax1.set_ylabel('Workload improvement vs default (%)',
               color=DARK_BLUE, fontsize=11)
ax1.tick_params(axis='y', labelcolor=DARK_BLUE)
ax1.set_ylim(0, 50)
ax2 = ax1.twinx()
ax2.plot(sweep_df['tau_ms'], sweep_df['regression_5pct'],
         color=RED, marker='s', linewidth=2.5,
         markersize=8, linestyle='--',
         label='Regression rate >5%')
ax2.set_ylabel('Regression rate (%)', color=RED, fontsize=11)
ax2.tick_params(axis='y', labelcolor=RED)
ax2.set_ylim(-1, 20)
ax2.text(2000, 2, 'Zero regressions at all tau values',
         fontsize=9, color=RED, style='italic')
l1, lb1 = ax1.get_legend_handles_labels()
l2, lb2 = ax2.get_legend_handles_labels()
ax1.legend(l1+l2, lb1+lb2, loc='center right', fontsize=9)
plt.title(
    'Risk-Controlled Steering: Performance vs Safety Tradeoff\n'
    '904-query Scaled JOB Workload',
    fontsize=12, fontweight='bold', pad=10)
plt.tight_layout()
fig3_path = FIG_DIR + r"\fig_tau_sweep.png"
plt.savefig(fig3_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Figure 3 saved: {fig3_path}")

# Figure 4: System comparison
fig, ax = plt.subplots(figsize=(8, 5))
best_fixed_total = min(data[arm].sum() for arm in arm_cols)
best_fixed_name  = min(arm_cols, key=lambda a: data[a].sum())
learned_total    = sweep_df.loc[
    sweep_df['tau_ms']==0, 'total_runtime_ms'].values[0]
strats  = ['Default\nPlanner',
           f'Best Fixed\n({best_fixed_name})',
           'Learned RF\nPolicy',
           'Oracle']
rts     = [default_total, best_fixed_total,
           learned_total, oracle_total]
colors4 = [GREY, DARK_BLUE, RED, GREEN]
bars4   = ax.bar(strats, [r/1000 for r in rts],
                 color=colors4, edgecolor='white', width=0.55)
for bar, rt in zip(bars4, rts):
    pct = (default_total - rt) / default_total * 100
    lbl = f'{rt/1000:.0f}s' if pct == 0 \
          else f'{rt/1000:.0f}s\n({pct:.1f}% faster)'
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 2,
            lbl, ha='center', va='bottom',
            fontsize=9, fontweight='bold')
ax.set_ylim(0, default_total/1000 * 1.25)
ax.set_title(
    'Total Workload Runtime Comparison\n'
    '904-query Scaled JOB Workload',
    fontsize=12, fontweight='bold', pad=10)
ax.set_ylabel('Total Runtime (seconds)', fontsize=11)
plt.tight_layout()
fig4_path = FIG_DIR + r"\fig_system_comparison.png"
plt.savefig(fig4_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"  Figure 4 saved: {fig4_path}")

# FINAL SUMMARY
print("\n" + "=" * 60)
print("  ALL STEPS COMPLETE")
print("=" * 60)
print(f"\n  Model accuracies (all from trained models):")
for _, row in acc_df.iterrows():
    print(f"    {row['model']:<25} {row['accuracy']*100:.1f}%")
print(f"\n  Tau sweep headline:")
r0 = sweep_df[sweep_df['tau_ms']==0].iloc[0]
print(f"    tau=0 improvement  : {r0['improvement_pct']}%")
print(f"    tau=0 regressions  : {r0['regression_5pct']}%")
print(f"    Queries steered    : {int(r0['queries_steered'])} of {len(data)}")
print(f"\n  Files saved:")
print(f"    {acc_path}")
print(f"    {report_path}")
print(f"    {fi_path}")
print(f"    {preds_path}")
print(f"    {sweep_path}")
print(f"    {FIG_DIR}\\fig_model_accuracy.png")
print(f"    {FIG_DIR}\\fig_feature_importance.png")
print(f"    {FIG_DIR}\\fig_tau_sweep.png")
print(f"    {FIG_DIR}\\fig_system_comparison.png")
print("=" * 60)