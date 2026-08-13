import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2
from scipy.stats import binomtest


# CONFIG

ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "results" / "analysis" / "combined_question_results.csv"
OUTPUT_DIR = ROOT / "results" / "analysis"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# LOAD DATA

print("=" * 70)
print("STATISTICAL ANALYSIS — ACTIVATION STEERING")
print("=" * 70)

df = pd.read_csv(INPUT)

print(f"\nQuestions loaded: {len(df)}")

required = ["baseline", "alpha_1", "alpha_2"]

for col in required:
    if col not in df.columns:
        raise ValueError(f"Missing required column: {col}")


# MCNEMAR'S TEST

def mcnemar_test(before, after):
    """
    McNemar test for paired binary predictions.

    b = baseline correct, steered incorrect
    c = baseline incorrect, steered correct

    We use the exact binomial version because the number
    of discordant pairs may be relatively small.
    """

    before_values = df[before].astype(int)
    after_values = df[after].astype(int)

    b = int(((before_values == 1) & (after_values == 0)).sum())
    c = int(((before_values == 0) & (after_values == 1)).sum())

    discordant = b + c

    if discordant == 0:
        p_value = 1.0
    else:
        result = binomtest(
            c,
            discordant,
            p=0.5,
            alternative="two-sided",
        )
        p_value = result.pvalue

    return {
        "baseline_correct_steered_wrong": b,
        "baseline_wrong_steered_correct": c,
        "discordant_pairs": discordant,
        "p_value": float(p_value),
        "significant_at_0.05": bool(p_value < 0.05),
    }


# RUN TESTS

print("\n" + "=" * 70)
print("1. MCNEMAR TESTS")
print("=" * 70)

test_01 = mcnemar_test("baseline", "alpha_1")
test_02 = mcnemar_test("baseline", "alpha_2")

results = {
    "alpha_0_vs_alpha_1": test_01,
    "alpha_0_vs_alpha_2": test_02,
}

for comparison, result in results.items():

    print(f"\n{comparison}")
    print("-" * 40)

    print(
        "Baseline correct → steered wrong:",
        result["baseline_correct_steered_wrong"],
    )

    print(
        "Baseline wrong → steered correct:",
        result["baseline_wrong_steered_correct"],
    )

    print(
        "Discordant pairs:",
        result["discordant_pairs"],
    )

    print(
        f"Exact McNemar p-value: {result['p_value']:.6f}"
    )

    print(
        "Significant at α=0.05:",
        result["significant_at_0.05"],
    )


# EFFECT SIZE

print("\n" + "=" * 70)
print("2. PAIRED IMPROVEMENT")
print("=" * 70)

total = len(df)

for condition in ["alpha_1", "alpha_2"]:

    baseline_correct = int(df["baseline"].sum())
    steered_correct = int(df[condition].sum())

    improved = int(
        ((df["baseline"] == 0) & (df[condition] == 1)).sum()
    )

    degraded = int(
        ((df["baseline"] == 1) & (df[condition] == 0)).sum()
    )

    net_change = improved - degraded

    print(f"\nBaseline → {condition}")
    print(f"Baseline correct: {baseline_correct}/{total}")
    print(f"Steered correct:  {steered_correct}/{total}")
    print(f"Improved:         {improved}")
    print(f"Degraded:         {degraded}")
    print(f"Net change:       {net_change:+d}")


# BOOTSTRAP CONFIDENCE INTERVAL

print("\n" + "=" * 70)
print("3. BOOTSTRAP CONFIDENCE INTERVALS")
print("=" * 70)

rng = np.random.default_rng(42)


def bootstrap_accuracy_difference(
    before,
    after,
    n_bootstrap=10000,
):
    before_values = df[before].to_numpy()
    after_values = df[after].to_numpy()

    differences = after_values - before_values

    bootstrap_means = []

    for _ in range(n_bootstrap):

        sample = rng.choice(
            differences,
            size=len(differences),
            replace=True,
        )

        bootstrap_means.append(sample.mean())

    bootstrap_means = np.array(bootstrap_means)

    lower = np.percentile(bootstrap_means, 2.5)
    upper = np.percentile(bootstrap_means, 97.5)

    observed = differences.mean()

    return {
        "observed_difference": float(observed),
        "ci_lower": float(lower),
        "ci_upper": float(upper),
    }


bootstrap_01 = bootstrap_accuracy_difference(
    "baseline",
    "alpha_1",
)

bootstrap_02 = bootstrap_accuracy_difference(
    "baseline",
    "alpha_2",
)

for name, result in [
    ("α=0 → α=1", bootstrap_01),
    ("α=0 → α=2", bootstrap_02),
]:

    print(f"\n{name}")

    print(
        f"Observed accuracy difference: "
        f"{result['observed_difference'] * 100:+.2f} pp"
    )

    print(
        f"95% bootstrap CI: "
        f"[{result['ci_lower'] * 100:+.2f}, "
        f"{result['ci_upper'] * 100:+.2f}] pp"
    )


# CATEGORY-LEVEL MCNEMAR TESTS

print("\n" + "=" * 70)
print("4. CATEGORY-LEVEL α=2 TESTS")
print("=" * 70)

category_results = []

for category in sorted(df["category"].unique()):

    subset = df[df["category"] == category].copy()

    before = subset["baseline"].astype(int)
    after = subset["alpha_2"].astype(int)

    b = int(((before == 1) & (after == 0)).sum())
    c = int(((before == 0) & (after == 1)).sum())

    discordant = b + c

    if discordant == 0:
        p_value = 1.0
    else:
        p_value = binomtest(
            c,
            discordant,
            p=0.5,
            alternative="two-sided",
        ).pvalue

    baseline_acc = before.mean() * 100
    alpha2_acc = after.mean() * 100

    category_results.append({
        "category": category,
        "n": int(len(subset)),
        "baseline_accuracy": baseline_acc,
        "alpha_2_accuracy": alpha2_acc,
        "improved": c,
        "degraded": b,
        "net_change": c - b,
        "p_value": p_value,
        "significant_at_0.05": bool(p_value < 0.05),
    })


category_df = pd.DataFrame(category_results)

print(
    category_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}",
    )
)

category_df.to_csv(
    OUTPUT_DIR / "statistical_category_results.csv",
    index=False,
)


# SAVE RESULTS

final_results = {
    "n_questions": total,
    "mcnemar": results,
    "bootstrap": {
        "alpha_0_vs_alpha_1": bootstrap_01,
        "alpha_0_vs_alpha_2": bootstrap_02,
    },
    "category_results": category_results,
}

output_path = OUTPUT_DIR / "statistical_results.json"

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(
        final_results,
        f,
        indent=2,
    )


# FINAL SUMMARY

print("\n" + "=" * 70)
print("STATISTICAL ANALYSIS COMPLETE")
print("=" * 70)

print("\nKey result:")

print(
    f"α=0 → α=1: "
    f"p={test_01['p_value']:.6f}"
)

print(
    f"α=0 → α=2: "
    f"p={test_02['p_value']:.6f}"
)

print(
    f"\nResults saved to:\n"
    f"{output_path}"
)

print(
    f"\nCategory results saved to:\n"
    f"{OUTPUT_DIR / 'statistical_category_results.csv'}"
)