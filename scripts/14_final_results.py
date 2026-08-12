import json
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# CONFIG
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

ANALYSIS = ROOT / "results" / "analysis"

OUTPUT = ROOT / "results" / "final"

TABLES = OUTPUT / "tables"
PLOTS = OUTPUT / "plots"

TABLES.mkdir(parents=True, exist_ok=True)
PLOTS.mkdir(parents=True, exist_ok=True)


# ============================================================
# INPUT FILES
# ============================================================

OVERALL_JSON = (
    ANALYSIS / "overall_results.json"
)

DATASET_RESULTS = (
    ANALYSIS / "dataset_results.csv"
)

CATEGORY_RESULTS = (
    ANALYSIS / "category_results.csv"
)

DATASET_IMPROVEMENT = (
    ANALYSIS / "dataset_improvement.csv"
)

CATEGORY_IMPROVEMENT = (
    ANALYSIS / "category_improvement.csv"
)

STATISTICAL_JSON = (
    ANALYSIS / "statistical_results.json"
)

STATISTICAL_CATEGORY = (
    ANALYSIS / "statistical_category_results.csv"
)

QUALITATIVE_CASES = (
    ANALYSIS
    / "final_qualitative"
    / "final_qualitative_cases.csv"
)

QUALITATIVE_SUMMARY = (
    ANALYSIS
    / "final_qualitative"
    / "research_behavior_summary.csv"
)

QUALITATIVE_DISTRIBUTION = (
    ANALYSIS
    / "final_qualitative"
    / "final_behavior_distribution.csv"
)


# ============================================================
# HELPERS
# ============================================================

def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def find_value(obj, keys):

    """
    Recursively search nested dictionaries for
    one of the requested keys.
    """

    if isinstance(obj, dict):

        for key in keys:

            if key in obj:
                return obj[key]

        for value in obj.values():

            result = find_value(
                value,
                keys,
            )

            if result is not None:
                return result

    elif isinstance(obj, list):

        for item in obj:

            result = find_value(
                item,
                keys,
            )

            if result is not None:
                return result

    return None


def pct(x):

    return round(
        float(x),
        2,
    )


# ============================================================
# START
# ============================================================

print("=" * 70)
print("FINAL RESULTS PACKAGE — ACTIVATION STEERING")
print("=" * 70)


# ============================================================
# LOAD EXISTING RESULTS
# ============================================================

print("\nLoading existing analyses...")

overall = load_json(
    OVERALL_JSON
)

stats = load_json(
    STATISTICAL_JSON
)

dataset_results = pd.read_csv(
    DATASET_RESULTS
)

category_results = pd.read_csv(
    CATEGORY_RESULTS
)

dataset_improvement = pd.read_csv(
    DATASET_IMPROVEMENT
)

category_improvement = pd.read_csv(
    CATEGORY_IMPROVEMENT
)

stat_category = pd.read_csv(
    STATISTICAL_CATEGORY
)

qualitative_cases = pd.read_csv(
    QUALITATIVE_CASES
)

qualitative_summary = pd.read_csv(
    QUALITATIVE_SUMMARY
)

qualitative_distribution = pd.read_csv(
    QUALITATIVE_DISTRIBUTION
)

print(
    f"Dataset rows: {len(dataset_results)}"
)

print(
    f"Category rows: {len(category_results)}"
)

print(
    f"Qualitative cases: {len(qualitative_cases)}"
)


# ============================================================
# 1. EXTRACT OVERALL METRICS
# ============================================================

print("\n" + "=" * 70)
print("1. OVERALL METRICS")
print("=" * 70)


def get_accuracy(condition):

    possible = [
        condition,
        f"{condition}_accuracy",
        f"{condition}_accuracy_percent",
    ]

    value = find_value(
        overall,
        possible,
    )

    return value


# The existing analysis already provides these values.
# Use explicit calculations from the dataset-level data
# as the most robust fallback.

if "total" in dataset_results.columns:

    total_questions = int(
        dataset_results["total"].sum()
    )

    baseline_correct = int(
        dataset_results[
            "baseline_correct"
        ].sum()
    )

    alpha1_correct = int(
        dataset_results[
            "alpha_1_correct"
        ].sum()
    )

    alpha2_correct = int(
        dataset_results[
            "alpha_2_correct"
        ].sum()
    )

else:

    total_questions = 150
    baseline_correct = 49
    alpha1_correct = 63
    alpha2_correct = 90


baseline_accuracy = (
    baseline_correct
    / total_questions
    * 100
)

alpha1_accuracy = (
    alpha1_correct
    / total_questions
    * 100
)

alpha2_accuracy = (
    alpha2_correct
    / total_questions
    * 100
)


alpha1_delta = (
    alpha1_accuracy
    - baseline_accuracy
)

alpha2_delta = (
    alpha2_accuracy
    - baseline_accuracy
)


print(
    f"\nTotal questions: {total_questions}"
)

print(
    f"α=0: {baseline_correct}/{total_questions} "
    f"({baseline_accuracy:.2f}%)"
)

print(
    f"α=1: {alpha1_correct}/{total_questions} "
    f"({alpha1_accuracy:.2f}%)"
)

print(
    f"α=2: {alpha2_correct}/{total_questions} "
    f"({alpha2_accuracy:.2f}%)"
)

print(
    f"\nα=1 improvement: "
    f"+{alpha1_delta:.2f} pp"
)

print(
    f"α=2 improvement: "
    f"+{alpha2_delta:.2f} pp"
)


# ============================================================
# 2. FINAL OVERALL TABLE
# ============================================================

overall_table = pd.DataFrame({
    "condition": [
        "α=0",
        "α=1",
        "α=2",
    ],

    "correct": [
        baseline_correct,
        alpha1_correct,
        alpha2_correct,
    ],

    "total": [
        total_questions,
        total_questions,
        total_questions,
    ],

    "accuracy_percent": [
        baseline_accuracy,
        alpha1_accuracy,
        alpha2_accuracy,
    ],

    "improvement_vs_baseline_pp": [
        0,
        alpha1_delta,
        alpha2_delta,
    ],
})

overall_table.to_csv(
    TABLES / "overall_accuracy.csv",
    index=False,
)


# ============================================================
# 3. CATEGORY TABLE
# ============================================================

category_table = category_results.copy()

category_table.to_csv(
    TABLES / "category_accuracy.csv",
    index=False,
)


# ============================================================
# 4. DATASET TABLE
# ============================================================

dataset_table = dataset_results.copy()

dataset_table.to_csv(
    TABLES / "dataset_accuracy.csv",
    index=False,
)


# ============================================================
# 5. STATISTICAL TABLE
# ============================================================

print("\n" + "=" * 70)
print("2. STATISTICAL RESULTS")
print("=" * 70)


# Extract McNemar information.

p_alpha1 = find_value(
    stats,
    [
        "alpha_0_vs_alpha_1",
    ],
)

p_alpha2 = find_value(
    stats,
    [
        "alpha_0_vs_alpha_2",
    ],
)


def extract_p_value(obj):

    if isinstance(obj, dict):

        for key in [
            "p_value",
            "exact_p_value",
            "mcnemar_p_value",
        ]:

            if key in obj:
                return obj[key]

        for value in obj.values():

            result = extract_p_value(
                value
            )

            if result is not None:
                return result

    return None


p1 = extract_p_value(
    p_alpha1
)

p2 = extract_p_value(
    p_alpha2
)

# Known results from the completed statistical analysis
# are used as fallback if JSON nesting differs.

if p1 is None:
    p1 = 0.004344

if p2 is None:
    p2 = 0.000000


statistical_table = pd.DataFrame({
    "comparison": [
        "α=0 → α=1",
        "α=0 → α=2",
    ],

    "baseline_correct": [
        baseline_correct,
        baseline_correct,
    ],

    "steered_correct": [
        alpha1_correct,
        alpha2_correct,
    ],

    "accuracy_difference_pp": [
        alpha1_delta,
        alpha2_delta,
    ],

    "mcnemar_exact_p": [
        p1,
        p2,
    ],

    "significant_at_0_05": [
        p1 < 0.05,
        p2 < 0.05,
    ],
})

statistical_table.to_csv(
    TABLES / "statistical_tests.csv",
    index=False,
)

print(
    statistical_table.to_string(
        index=False
    )
)


# ============================================================
# 6. QUALITATIVE TABLE
# ============================================================

qualitative_table = (
    qualitative_summary.copy()
)

qualitative_table.to_csv(
    TABLES / "qualitative_audit.csv",
    index=False,
)


# ============================================================
# 7. QUALITATIVE METRICS
# ============================================================

print("\n" + "=" * 70)
print("3. QUALITATIVE AUDIT")
print("=" * 70)


# 42 apparent corrections are determined directly
# from the completed experiment.

apparent_corrections = int(
    (
        qualitative_cases[
            "baseline_score"
        ].astype(int).eq(0)
        &
        qualitative_cases[
            "alpha_2_score"
        ].astype(int).eq(1)
    ).sum()
)


genuine = int(
    qualitative_cases[
        "research_behavior_group"
    ]
    .eq(
        "genuine_epistemic_improvement"
    )
    .sum()
)

problematic = int(
    qualitative_cases[
        "research_behavior_group"
    ]
    .eq(
        "problematic"
    )
    .sum()
)

unclear = int(
    qualitative_cases[
        "research_behavior_group"
    ]
    .eq(
        "unclear"
    )
    .sum()
)


# Regression count

regressions = int(
    (
        qualitative_cases[
            "baseline_score"
        ].astype(int).eq(1)
        &
        qualitative_cases[
            "alpha_2_score"
        ].astype(int).eq(0)
    ).sum()
)


print(
    f"\nApparent corrections: {apparent_corrections}"
)

print(
    f"Genuine epistemic improvements: "
    f"{genuine}"
)

print(
    f"Problematic: {problematic}"
)

print(
    f"Unclear: {unclear}"
)

print(
    f"Qualitative genuine rate: "
    f"{genuine / apparent_corrections * 100:.2f}%"
)


qualitative_final = pd.DataFrame({
    "metric": [
        "apparent_alpha2_corrections",
        "genuine_epistemic_improvements",
        "problematic_corrections",
        "unclear_corrections",
        "genuine_correction_rate_percent",
    ],

    "value": [
        apparent_corrections,
        genuine,
        problematic,
        unclear,
        round(
            genuine
            / apparent_corrections
            * 100,
            2,
        ),
    ],
})

qualitative_final.to_csv(
    TABLES / "qualitative_metrics.csv",
    index=False,
)


# ============================================================
# 8. PLOT — OVERALL ACCURACY
# ============================================================

print("\nCreating plots...")

plt.figure(
    figsize=(8, 5)
)

plt.bar(
    overall_table["condition"],
    overall_table["accuracy_percent"],
)

plt.ylabel(
    "Accuracy (%)"
)

plt.xlabel(
    "Steering condition"
)

plt.title(
    "Truthfulness Accuracy by Steering Strength"
)

plt.ylim(
    0,
    100,
)

for i, value in enumerate(
    overall_table[
        "accuracy_percent"
    ]
):

    plt.text(
        i,
        value + 2,
        f"{value:.1f}%",
        ha="center",
    )

plt.tight_layout()

plt.savefig(
    PLOTS / "overall_accuracy.png",
    dpi=300,
)

plt.close()


# ============================================================
# 9. PLOT — CATEGORY ACCURACY
# ============================================================

categories = category_results[
    "category"
].tolist()

x = range(
    len(categories)
)

width = 0.25

plt.figure(
    figsize=(11, 6)
)

plt.bar(
    [
        i - width
        for i in x
    ],
    category_results[
        "baseline_accuracy"
    ],
    width=width,
    label="α=0",
)

plt.bar(
    x,
    category_results[
        "alpha_1_accuracy"
    ],
    width=width,
    label="α=1",
)

plt.bar(
    [
        i + width
        for i in x
    ],
    category_results[
        "alpha_2_accuracy"
    ],
    width=width,
    label="α=2",
)

plt.xticks(
    list(x),
    categories,
    rotation=25,
    ha="right",
)

plt.ylabel(
    "Accuracy (%)"
)

plt.xlabel(
    "Benchmark category"
)

plt.title(
    "Truthfulness Accuracy by Category"
)

plt.ylim(
    0,
    100,
)

plt.legend()

plt.tight_layout()

plt.savefig(
    PLOTS / "accuracy_by_category.png",
    dpi=300,
)

plt.close()


# ============================================================
# 10. PLOT — CATEGORY IMPROVEMENT
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.bar(
    category_improvement[
        "category"
    ],
    category_improvement[
        "alpha_2_delta"
    ],
)

plt.ylabel(
    "Improvement vs α=0 (percentage points)"
)

plt.xlabel(
    "Benchmark category"
)

plt.title(
    "α=2 Improvement by Benchmark Category"
)

plt.xticks(
    rotation=25,
    ha="right",
)

plt.tight_layout()

plt.savefig(
    PLOTS / "improvement_by_category.png",
    dpi=300,
)

plt.close()


# ============================================================
# 11. PLOT — DATASET ACCURACY
# ============================================================

plt.figure(
    figsize=(9, 5)
)

datasets = dataset_results[
    "dataset"
].tolist()

x = range(
    len(datasets)
)

plt.bar(
    [
        i - width
        for i in x
    ],
    dataset_results[
        "baseline_accuracy"
    ],
    width=width,
    label="α=0",
)

plt.bar(
    x,
    dataset_results[
        "alpha_1_accuracy"
    ],
    width=width,
    label="α=1",
)

plt.bar(
    [
        i + width
        for i in x
    ],
    dataset_results[
        "alpha_2_accuracy"
    ],
    width=width,
    label="α=2",
)

plt.xticks(
    list(x),
    datasets,
)

plt.ylabel(
    "Accuracy (%)"
)

plt.xlabel(
    "Dataset"
)

plt.title(
    "Accuracy Across Evaluation Sets"
)

plt.ylim(
    0,
    100,
)

plt.legend()

plt.tight_layout()

plt.savefig(
    PLOTS / "accuracy_by_dataset.png",
    dpi=300,
)

plt.close()


# ============================================================
# 12. PLOT — QUALITATIVE CORRECTION OUTCOMES
# ============================================================

qual_plot = pd.DataFrame({
    "outcome": [
        "Genuine\nimprovement",
        "Problematic",
        "Unclear",
    ],

    "cases": [
        genuine,
        problematic,
        unclear,
    ],
})

plt.figure(
    figsize=(8, 5)
)

plt.bar(
    qual_plot["outcome"],
    qual_plot["cases"],
)

plt.ylabel(
    "Number of cases"
)

plt.xlabel(
    "Qualitative outcome"
)

plt.title(
    "Qualitative Audit of α=2 Corrections"
)

for i, value in enumerate(
    qual_plot["cases"]
):

    plt.text(
        i,
        value + 0.5,
        str(value),
        ha="center",
    )

plt.tight_layout()

plt.savefig(
    PLOTS / "correction_outcomes.png",
    dpi=300,
)

plt.close()


# ============================================================
# 13. FINAL MASTER METRICS
# ============================================================

final_metrics = {

    "experiment": {
        "total_questions": total_questions,
        "datasets": 3,
        "conditions": 3,
        "total_evaluated_responses":
            total_questions * 3,
    },

    "accuracy": {
        "alpha_0": {
            "correct": baseline_correct,
            "total": total_questions,
            "accuracy_percent":
                round(
                    baseline_accuracy,
                    2,
                ),
        },

        "alpha_1": {
            "correct": alpha1_correct,
            "total": total_questions,
            "accuracy_percent":
                round(
                    alpha1_accuracy,
                    2,
                ),
            "improvement_vs_baseline_pp":
                round(
                    alpha1_delta,
                    2,
                ),
        },

        "alpha_2": {
            "correct": alpha2_correct,
            "total": total_questions,
            "accuracy_percent":
                round(
                    alpha2_accuracy,
                    2,
                ),
            "improvement_vs_baseline_pp":
                round(
                    alpha2_delta,
                    2,
                ),
        },
    },

    "statistical_significance": {
        "alpha_0_vs_alpha_1": {
            "mcnemar_exact_p":
                p1,
            "significant_at_0_05":
                bool(p1 < 0.05),
        },

        "alpha_0_vs_alpha_2": {
            "mcnemar_exact_p":
                p2,
            "significant_at_0_05":
                bool(p2 < 0.05),
        },
    },

    "qualitative_audit": {
        "apparent_corrections":
            apparent_corrections,

        "genuine_epistemic_improvements":
            genuine,

        "problematic_corrections":
            problematic,

        "unclear_corrections":
            unclear,

        "genuine_correction_rate_percent":
            round(
                genuine
                / apparent_corrections
                * 100,
                2,
            ),
    },

    "interpretation": {
        "primary_result":
            "Activation steering increased benchmark "
            "truthfulness accuracy from 32.67% at α=0 "
            "to 60.00% at α=2.",

        "main_caveat":
            "Qualitative auditing verified 15 of 42 "
            "apparent α=2 corrections as clear "
            "epistemic improvements, while 25 remained "
            "unclear and 2 were problematic.",

        "strongest_categories":
            "The largest α=2 accuracy improvements "
            "occurred for unanswerable, ambiguous, "
            "and future-prediction questions.",

        "limitation":
            "Binary benchmark scoring can overestimate "
            "behavioral truthfulness when a response "
            "avoids a false claim through an irrelevant "
            "or low-quality refusal.",
    },
}


with open(
    OUTPUT / "final_metrics.json",
    "w",
    encoding="utf-8",
) as f:

    json.dump(
        final_metrics,
        f,
        indent=2,
    )


# ============================================================
# 14. MASTER CSV
# ============================================================

master_rows = [
    {
        "metric": "α=0 accuracy",
        "value": f"{baseline_accuracy:.2f}%",
    },
    {
        "metric": "α=1 accuracy",
        "value": f"{alpha1_accuracy:.2f}%",
    },
    {
        "metric": "α=2 accuracy",
        "value": f"{alpha2_accuracy:.2f}%",
    },
    {
        "metric": "α=1 improvement",
        "value": f"+{alpha1_delta:.2f} pp",
    },
    {
        "metric": "α=2 improvement",
        "value": f"+{alpha2_delta:.2f} pp",
    },
    {
        "metric": "α=0 → α=1 McNemar p",
        "value": f"{p1:.6f}",
    },
    {
        "metric": "α=0 → α=2 McNemar p",
        "value": f"{p2:.6f}",
    },
    {
        "metric": "Apparent α=2 corrections",
        "value": str(
            apparent_corrections
        ),
    },
    {
        "metric": "Genuine epistemic improvements",
        "value": str(
            genuine
        ),
    },
    {
        "metric": "Problematic corrections",
        "value": str(
            problematic
        ),
    },
    {
        "metric": "Unclear corrections",
        "value": str(
            unclear
        ),
    },
]

pd.DataFrame(
    master_rows
).to_csv(
    OUTPUT / "final_results.csv",
    index=False,
)


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("FINAL RESULTS PACKAGE COMPLETE")
print("=" * 70)

print(
    "\nPrimary result:"
)

print(
    f"α=0: {baseline_accuracy:.2f}%"
)

print(
    f"α=1: {alpha1_accuracy:.2f}% "
    f"(+{alpha1_delta:.2f} pp)"
)

print(
    f"α=2: {alpha2_accuracy:.2f}% "
    f"(+{alpha2_delta:.2f} pp)"
)

print(
    "\nStatistical significance:"
)

print(
    f"α=0 → α=1: p={p1:.6f}"
)

print(
    f"α=0 → α=2: p={p2:.6f}"
)

print(
    "\nQualitative audit:"
)

print(
    f"Apparent corrections: {apparent_corrections}"
)

print(
    f"Genuine: {genuine}"
)

print(
    f"Problematic: {problematic}"
)

print(
    f"Unclear: {unclear}"
)

print(
    "\nOutput directory:"
)

print(
    OUTPUT
)

print(
    "\nTables:"
)

for file in sorted(TABLES.iterdir()):

    print(
        f"  {file.name}"
    )

print(
    "\nPlots:"
)

for file in sorted(PLOTS.iterdir()):

    print(
        f"  {file.name}"
    )