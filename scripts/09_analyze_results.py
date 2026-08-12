import json
from pathlib import Path
from collections import defaultdict

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# CONFIG
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

SET_A_PATH = ROOT / "results" / "raw" / "truthfulness_scores.json"
SET_B_PATH = ROOT / "results" / "raw" / "robustness" / "set_B_scores.json"
SET_C_PATH = ROOT / "results" / "raw" / "robustness" / "set_C_scores.json"

OUTPUT_DIR = ROOT / "results" / "analysis"
PLOTS_DIR = OUTPUT_DIR / "plots"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# HELPERS
# ============================================================

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_category(record):
    """
    Set B has:
        category = "unknown"
        question.category = "false_premise"

    Set C has:
        category = "false_premise"

    Use the actual question category whenever available.
    """

    question = record.get("question")

    if isinstance(question, dict):
        category = question.get("category")
        if category:
            return category

    category = record.get("category")

    if category:
        return category

    return "unknown"


def extract_scores(record):
    return {
        "baseline": int(record.get("baseline_score", 0)),
        "alpha_1": int(record.get("alpha_1_score", 0)),
        "alpha_2": int(record.get("alpha_2_score", 0)),
    }


def load_set_a(path):
    """
    Set A may have a different structure from robustness sets.
    Try to locate the list of question-level records.
    """

    data = load_json(path)

    if isinstance(data, list):
        records = data

    elif isinstance(data, dict):
        if isinstance(data.get("scores"), list):
            records = data["scores"]

        elif isinstance(data.get("results"), list):
            records = data["results"]

        else:
            # Search top-level values for a list of records
            records = None

            for value in data.values():
                if isinstance(value, list) and value:
                    if isinstance(value[0], dict):
                        records = value
                        break

            if records is None:
                raise ValueError(
                    f"Could not locate question-level records in {path}"
                )

    else:
        raise ValueError(f"Unsupported JSON structure in {path}")

    normalized = []

    for i, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            continue

        scores = extract_scores(record)

        normalized.append({
            "set": "A",
            "id": record.get("id", i),
            "category": normalize_category(record),
            "question": (
                record.get("question")
                if isinstance(record.get("question"), str)
                else record.get("question", {}).get("question", "")
                if isinstance(record.get("question"), dict)
                else ""
            ),
            **scores,
        })

    return normalized


def load_robustness_set(path, set_name):
    data = load_json(path)

    if not isinstance(data, dict):
        raise ValueError(f"{path} should contain a JSON object.")

    records = data.get("scores")

    if not isinstance(records, list):
        raise ValueError(
            f"Could not find question-level 'scores' list in {path}"
        )

    normalized = []

    for i, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            continue

        question_data = record.get("question")

        if isinstance(question_data, dict):
            question_text = question_data.get("question", "")
        else:
            question_text = question_data or ""

        scores = extract_scores(record)

        normalized.append({
            "set": set_name,
            "id": record.get("id", i),
            "category": normalize_category(record),
            "question": question_text,
            **scores,
        })

    return normalized


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("ACTIVATION STEERING — FINAL EXPERIMENT ANALYSIS")
print("=" * 70)

print("\nLoading score files...")

set_a = load_set_a(SET_A_PATH)
set_b = load_robustness_set(SET_B_PATH, "B")
set_c = load_robustness_set(SET_C_PATH, "C")

all_records = set_a + set_b + set_c

print(f"\nSet A: {len(set_a)} questions")
print(f"Set B: {len(set_b)} questions")
print(f"Set C: {len(set_c)} questions")
print(f"Total: {len(all_records)} questions")

if len(set_a) != 50:
    print(f"WARNING: Set A contains {len(set_a)} questions.")

if len(set_b) != 50:
    print(f"WARNING: Set B contains {len(set_b)} questions.")

if len(set_c) != 50:
    print(f"WARNING: Set C contains {len(set_c)} questions.")

if len(all_records) != 150:
    print("WARNING: Expected exactly 150 questions.")


# ============================================================
# DATAFRAME
# ============================================================

df = pd.DataFrame(all_records)

conditions = ["baseline", "alpha_1", "alpha_2"]

display_names = {
    "baseline": "α=0",
    "alpha_1": "α=1",
    "alpha_2": "α=2",
}


# ============================================================
# 1. OVERALL ACCURACY
# ============================================================

print("\n" + "=" * 70)
print("1. OVERALL ACCURACY")
print("=" * 70)

overall_rows = []

for condition in conditions:
    correct = int(df[condition].sum())
    total = len(df)
    accuracy = correct / total * 100

    overall_rows.append({
        "condition": display_names[condition],
        "correct": correct,
        "total": total,
        "accuracy_percent": accuracy,
    })

overall_df = pd.DataFrame(overall_rows)

print("\n")
print(overall_df.to_string(index=False))

baseline_acc = overall_df.loc[
    overall_df["condition"] == "α=0", "accuracy_percent"
].iloc[0]

alpha1_acc = overall_df.loc[
    overall_df["condition"] == "α=1", "accuracy_percent"
].iloc[0]

alpha2_acc = overall_df.loc[
    overall_df["condition"] == "α=2", "accuracy_percent"
].iloc[0]

print("\nImprovement:")
print(f"α=1 vs α=0: {alpha1_acc - baseline_acc:+.2f} percentage points")
print(f"α=2 vs α=0: {alpha2_acc - baseline_acc:+.2f} percentage points")

if baseline_acc > 0:
    print(
        f"Relative improvement α=1: "
        f"{((alpha1_acc - baseline_acc) / baseline_acc) * 100:+.2f}%"
    )

    print(
        f"Relative improvement α=2: "
        f"{((alpha2_acc - baseline_acc) / baseline_acc) * 100:+.2f}%"
    )


# ============================================================
# 2. DATASET ACCURACY
# ============================================================

print("\n" + "=" * 70)
print("2. DATASET ACCURACY")
print("=" * 70)

dataset_rows = []

for dataset, group in df.groupby("set"):
    row = {
        "dataset": dataset,
        "questions": len(group),
    }

    for condition in conditions:
        row[f"{condition}_correct"] = int(group[condition].sum())
        row[f"{condition}_accuracy"] = (
            group[condition].mean() * 100
        )

    dataset_rows.append(row)

dataset_df = pd.DataFrame(dataset_rows)

print("\n")
print(dataset_df.to_string(index=False))

dataset_csv = OUTPUT_DIR / "dataset_results.csv"
dataset_df.to_csv(dataset_csv, index=False)


# ============================================================
# 3. CATEGORY ACCURACY
# ============================================================

print("\n" + "=" * 70)
print("3. CATEGORY ACCURACY")
print("=" * 70)

category_rows = []

for category, group in df.groupby("category"):
    row = {
        "category": category,
        "questions": len(group),
    }

    for condition in conditions:
        row[f"{condition}_correct"] = int(group[condition].sum())
        row[f"{condition}_accuracy"] = (
            group[condition].mean() * 100
        )

    category_rows.append(row)

category_df = pd.DataFrame(category_rows)

print("\n")
print(category_df.to_string(index=False))

category_csv = OUTPUT_DIR / "category_results.csv"
category_df.to_csv(category_csv, index=False)


# ============================================================
# 4. QUESTION-LEVEL TRANSITIONS
# ============================================================

print("\n" + "=" * 70)
print("4. QUESTION-LEVEL TRANSITIONS")
print("=" * 70)


def transition_stats(before, after):
    """
    Scores are binary:
        0 = incorrect
        1 = correct
    """

    before_values = df[before]
    after_values = df[after]

    improved = int(((before_values == 0) & (after_values == 1)).sum())
    degraded = int(((before_values == 1) & (after_values == 0)).sum())
    stayed_correct = int(
        ((before_values == 1) & (after_values == 1)).sum()
    )
    stayed_wrong = int(
        ((before_values == 0) & (after_values == 0)).sum()
    )

    return {
        "improved": improved,
        "degraded": degraded,
        "stayed_correct": stayed_correct,
        "stayed_wrong": stayed_wrong,
    }


transition_01 = transition_stats("baseline", "alpha_1")
transition_02 = transition_stats("baseline", "alpha_2")

transition_df = pd.DataFrame([
    {
        "comparison": "α=0 → α=1",
        **transition_01,
    },
    {
        "comparison": "α=0 → α=2",
        **transition_02,
    },
])

print("\n")
print(transition_df.to_string(index=False))

transition_json = OUTPUT_DIR / "transition_results.json"

with open(transition_json, "w", encoding="utf-8") as f:
    json.dump(
        {
            "alpha_0_to_alpha_1": transition_01,
            "alpha_0_to_alpha_2": transition_02,
        },
        f,
        indent=2,
    )


# ============================================================
# 5. CATEGORY-LEVEL IMPROVEMENT
# ============================================================

print("\n" + "=" * 70)
print("5. CATEGORY-LEVEL IMPROVEMENT")
print("=" * 70)

category_improvement_rows = []

for category, group in df.groupby("category"):

    baseline = group["baseline"].mean() * 100
    alpha1 = group["alpha_1"].mean() * 100
    alpha2 = group["alpha_2"].mean() * 100

    category_improvement_rows.append({
        "category": category,
        "questions": len(group),
        "alpha_0_accuracy": baseline,
        "alpha_1_accuracy": alpha1,
        "alpha_2_accuracy": alpha2,
        "alpha_1_delta": alpha1 - baseline,
        "alpha_2_delta": alpha2 - baseline,
    })

category_improvement_df = pd.DataFrame(category_improvement_rows)

print("\n")
print(category_improvement_df.to_string(index=False))

category_improvement_df.to_csv(
    OUTPUT_DIR / "category_improvement.csv",
    index=False,
)


# ============================================================
# 6. DATASET-LEVEL IMPROVEMENT
# ============================================================

dataset_improvement_rows = []

for dataset, group in df.groupby("set"):

    baseline = group["baseline"].mean() * 100
    alpha1 = group["alpha_1"].mean() * 100
    alpha2 = group["alpha_2"].mean() * 100

    dataset_improvement_rows.append({
        "dataset": dataset,
        "questions": len(group),
        "alpha_0_accuracy": baseline,
        "alpha_1_accuracy": alpha1,
        "alpha_2_accuracy": alpha2,
        "alpha_1_delta": alpha1 - baseline,
        "alpha_2_delta": alpha2 - baseline,
    })

dataset_improvement_df = pd.DataFrame(dataset_improvement_rows)

dataset_improvement_df.to_csv(
    OUTPUT_DIR / "dataset_improvement.csv",
    index=False,
)


# ============================================================
# 7. MOST IMPROVED / MOST DEGRADED CATEGORIES
# ============================================================

print("\n" + "=" * 70)
print("6. BEST / WORST CATEGORY CHANGES")
print("=" * 70)

best_alpha2 = category_improvement_df.sort_values(
    "alpha_2_delta",
    ascending=False,
)

print("\nLargest α=2 improvements:")
print(
    best_alpha2[
        [
            "category",
            "alpha_0_accuracy",
            "alpha_2_accuracy",
            "alpha_2_delta",
        ]
    ].head(10).to_string(index=False)
)

print("\n")


# ============================================================
# 8. OVERALL ACCURACY PLOT
# ============================================================

plt.figure(figsize=(8, 5))

plt.bar(
    overall_df["condition"],
    overall_df["accuracy_percent"],
)

plt.ylabel("Accuracy (%)")
plt.xlabel("Steering strength")
plt.title("Overall Truthfulness Accuracy")
plt.ylim(0, 100)

for i, value in enumerate(overall_df["accuracy_percent"]):
    plt.text(
        i,
        value + 1,
        f"{value:.1f}%",
        ha="center",
    )

plt.tight_layout()

overall_plot = PLOTS_DIR / "overall_accuracy.png"
plt.savefig(overall_plot, dpi=300)
plt.close()


# ============================================================
# 9. DATASET PLOT
# ============================================================

plt.figure(figsize=(9, 5))

x = range(len(dataset_df))
width = 0.25

plt.bar(
    [i - width for i in x],
    dataset_df["baseline_accuracy"],
    width,
    label="α=0",
)

plt.bar(
    x,
    dataset_df["alpha_1_accuracy"],
    width,
    label="α=1",
)

plt.bar(
    [i + width for i in x],
    dataset_df["alpha_2_accuracy"],
    width,
    label="α=2",
)

plt.xticks(
    list(x),
    dataset_df["dataset"],
)

plt.ylabel("Accuracy (%)")
plt.xlabel("Dataset")
plt.title("Accuracy Across Evaluation Sets")
plt.ylim(0, 100)
plt.legend()

plt.tight_layout()

dataset_plot = PLOTS_DIR / "dataset_accuracy.png"
plt.savefig(dataset_plot, dpi=300)
plt.close()


# ============================================================
# 10. CATEGORY PLOT
# ============================================================

category_plot_df = category_df.copy()

plt.figure(figsize=(12, 6))

x = range(len(category_plot_df))
width = 0.25

plt.bar(
    [i - width for i in x],
    category_plot_df["baseline_accuracy"],
    width,
    label="α=0",
)

plt.bar(
    x,
    category_plot_df["alpha_1_accuracy"],
    width,
    label="α=1",
)

plt.bar(
    [i + width for i in x],
    category_plot_df["alpha_2_accuracy"],
    width,
    label="α=2",
)

plt.xticks(
    list(x),
    category_plot_df["category"],
    rotation=30,
    ha="right",
)

plt.ylabel("Accuracy (%)")
plt.xlabel("Category")
plt.title("Truthfulness Accuracy by Question Category")
plt.ylim(0, 100)
plt.legend()

plt.tight_layout()

category_plot = PLOTS_DIR / "category_accuracy.png"
plt.savefig(category_plot, dpi=300)
plt.close()


# ============================================================
# 11. FINAL SUMMARY JSON
# ============================================================

summary = {
    "total_questions": len(df),
    "datasets": {
        "A": len(set_a),
        "B": len(set_b),
        "C": len(set_c),
    },
    "overall_accuracy": {
        "alpha_0": {
            "correct": int(df["baseline"].sum()),
            "total": len(df),
            "accuracy_percent": float(df["baseline"].mean() * 100),
        },
        "alpha_1": {
            "correct": int(df["alpha_1"].sum()),
            "total": len(df),
            "accuracy_percent": float(df["alpha_1"].mean() * 100),
        },
        "alpha_2": {
            "correct": int(df["alpha_2"].sum()),
            "total": len(df),
            "accuracy_percent": float(df["alpha_2"].mean() * 100),
        },
    },
    "improvement": {
        "alpha_1_minus_alpha_0": float(alpha1_acc - baseline_acc),
        "alpha_2_minus_alpha_0": float(alpha2_acc - baseline_acc),
    },
    "transitions": {
        "alpha_0_to_alpha_1": transition_01,
        "alpha_0_to_alpha_2": transition_02,
    },
}

summary_path = OUTPUT_DIR / "overall_results.json"

with open(summary_path, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)


# ============================================================
# 12. SAVE COMBINED QUESTION-LEVEL DATA
# ============================================================

combined_path = OUTPUT_DIR / "combined_question_results.csv"

df.to_csv(
    combined_path,
    index=False,
)


# ============================================================
# FINAL OUTPUT
# ============================================================

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)

print("\nFINAL OVERALL RESULTS")

for _, row in overall_df.iterrows():
    print(
        f"{row['condition']}: "
        f"{int(row['correct'])}/{int(row['total'])} "
        f"({row['accuracy_percent']:.2f}%)"
    )

print("\nImprovement:")
print(f"α=1 vs α=0: {alpha1_acc - baseline_acc:+.2f} pp")
print(f"α=2 vs α=0: {alpha2_acc - baseline_acc:+.2f} pp")

print("\nFiles created:")
print(f"  {summary_path}")
print(f"  {dataset_csv}")
print(f"  {category_csv}")
print(f"  {OUTPUT_DIR / 'category_improvement.csv'}")
print(f"  {OUTPUT_DIR / 'dataset_improvement.csv'}")
print(f"  {transition_json}")
print(f"  {combined_path}")

print("\nPlots:")
print(f"  {overall_plot}")
print(f"  {dataset_plot}")
print(f"  {category_plot}")

print("\n" + "=" * 70)