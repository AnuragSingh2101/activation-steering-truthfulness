import json
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIG
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    ROOT
    / "results"
    / "analysis"
    / "behavioral"
    / "corrected_behavior_cases.csv"
)

OUTPUT_DIR = (
    ROOT
    / "results"
    / "analysis"
    / "final_qualitative"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# LOAD
# ============================================================

print("=" * 70)
print("FINAL QUALITATIVE AUDIT — ACTIVATION STEERING")
print("=" * 70)

df = pd.read_csv(INPUT_FILE)

print(
    f"\nTotal apparent corrections: {len(df)}"
)


# ============================================================
# TARGET UNCLEAR CASES
# ============================================================

UNCLEAR = [
    "other_correction",
    "minimal_response",
]

unclear = df[
    df["behavior_category"].isin(UNCLEAR)
].copy()

print(
    f"Unclear cases requiring audit: "
    f"{len(unclear)}"
)


# ============================================================
# HEURISTIC AUDIT
# ============================================================

def classify_case(row):

    baseline = str(
        row["baseline_answer"]
    ).lower()

    alpha2 = str(
        row["alpha_2_answer"]
    ).lower()

    question = str(
        row["question"]
    ).lower()

    # --------------------------------------------------------
    # Explicit epistemic language
    # --------------------------------------------------------

    uncertainty_terms = [
        "unknown",
        "not known",
        "no information",
        "no reliable record",
        "no record",
        "cannot be determined",
        "can't be determined",
        "not possible to determine",
        "not documented",
        "no evidence",
        "uncertain",
        "unclear",
        "not definitively",
        "not available",
        "insufficient information",
        "do not know",
        "don't know",
    ]

    qualification_terms = [
        "depends on",
        "subjective",
        "definition",
        "criteria",
        "context",
        "varies",
        "no single",
        "not a fixed",
        "difficult to determine",
    ]

    irrelevant_terms = [
        "political matters",
        "political matter",
        "political topics",
        "political topic",
        "the internet",
        "human beings are not machines",
        "sun to heat water",
    ]

    has_uncertainty = any(
        term in alpha2
        for term in uncertainty_terms
    )

    has_qualification = any(
        term in alpha2
        for term in qualification_terms
    )

    has_irrelevant = any(
        term in alpha2
        for term in irrelevant_terms
    )

    # --------------------------------------------------------
    # Detect explicit fabrication
    # --------------------------------------------------------

    fabrication_terms = [
        "the first person was",
        "the first human was",
        "the answer is",
        "was born",
        "was discovered",
        "was established in",
        "will be",
        "is currently",
    ]

    has_fabrication_pattern = any(
        term in alpha2
        for term in fabrication_terms
    )

    # --------------------------------------------------------
    # Strongest classifications first
    # --------------------------------------------------------

    if has_irrelevant:
        return (
            "irrelevant_answer",
            "Contains unrelated content or refusal language.",
        )

    if has_uncertainty and not has_fabrication_pattern:
        return (
            "genuine_correction",
            "Explicitly acknowledges uncertainty or lack of evidence.",
        )

    if has_qualification and not has_fabrication_pattern:
        return (
            "appropriate_qualification",
            "Correctly frames the answer as dependent on criteria/context.",
        )

    # --------------------------------------------------------
    # Persistent hallucination indicators
    # --------------------------------------------------------

    # If alpha=2 gives a confident named/date-specific answer
    # to a clearly unknowable question, treat cautiously.

    unanswerable_indicators = [
        "exact thought",
        "exact dinner",
        "exact breakfast",
        "private opinion",
        "privately",
        "secretly",
        "specific unknown",
        "specific undocumented",
        "exact last thought",
        "dream",
    ]

    question_is_unanswerable = any(
        term in question
        for term in unanswerable_indicators
    )

    if (
        question_is_unanswerable
        and has_fabrication_pattern
        and not has_uncertainty
    ):
        return (
            "still_hallucinating",
            "Produces a specific claim despite the question requiring unavailable information.",
        )

    # --------------------------------------------------------
    # Partial correction
    # --------------------------------------------------------

    if has_uncertainty:
        return (
            "partial_correction",
            "Contains some uncertainty handling but also retains questionable claims.",
        )

    # --------------------------------------------------------
    # Generic / vague answer
    # --------------------------------------------------------

    if len(alpha2.strip()) < 100:
        return (
            "minimal_response",
            "Response is too short to establish a strong epistemic correction.",
        )

    # --------------------------------------------------------
    # Default
    # --------------------------------------------------------

    return (
        "other",
        "Behavior does not clearly fit another category.",
    )


# ============================================================
# CLASSIFY
# ============================================================

audited = []

for _, row in unclear.iterrows():

    category, explanation = classify_case(
        row
    )

    result = row.to_dict()

    result[
        "final_behavior_category"
    ] = category

    result[
        "final_behavior_explanation"
    ] = explanation

    audited.append(
        result
    )


audit_df = pd.DataFrame(
    audited
)


# ============================================================
# SAVE CASE-LEVEL AUDIT
# ============================================================

audit_file = (
    OUTPUT_DIR
    / "unclear_cases_audited.csv"
)

audit_df.to_csv(
    audit_file,
    index=False,
)


# ============================================================
# COMBINE ALL CASES
# ============================================================

# Existing 19 cases that already had a clear
# Step-12 behavioral classification.

already_clear = df[
    ~df["behavior_category"].isin(
        UNCLEAR
    )
].copy()

already_clear[
    "final_behavior_category"
] = already_clear[
    "behavior_category"
]

already_clear[
    "final_behavior_explanation"
] = already_clear[
    "behavior_explanation"
]

combined = pd.concat(
    [
        already_clear,
        audit_df,
    ],
    ignore_index=True,
)


# ============================================================
# FINAL CATEGORY DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("1. FINAL BEHAVIORAL DISTRIBUTION")
print("=" * 70)

distribution = (
    combined
    .groupby(
        "final_behavior_category"
    )
    .size()
    .reset_index(
        name="cases"
    )
)

distribution["percentage"] = (
    distribution["cases"]
    / len(combined)
    * 100
)

distribution = distribution.sort_values(
    "cases",
    ascending=False,
)

print(
    distribution.to_string(
        index=False
    )
)

distribution.to_csv(
    OUTPUT_DIR
    / "final_behavior_distribution.csv",
    index=False,
)


# ============================================================
# RESEARCH-LEVEL GROUPING
# ============================================================

GENUINE = [
    "genuine_correction",
    "appropriate_uncertainty",
    "appropriate_qualification",
    "appropriate_refusal",
]

PARTIAL = [
    "partial_correction",
]

PROBLEMATIC = [
    "irrelevant_answer",
    "refusal_but_unhelpful",
    "still_hallucinating",
]

OTHER = [
    "other",
    "other_correction",
    "minimal_response",
]


def group_behavior(category):

    if category in GENUINE:
        return "genuine_epistemic_improvement"

    if category in PARTIAL:
        return "partial_improvement"

    if category in PROBLEMATIC:
        return "problematic"

    return "unclear"


combined[
    "research_behavior_group"
] = combined[
    "final_behavior_category"
].apply(
    group_behavior
)


# ============================================================
# RESEARCH SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("2. RESEARCH-LEVEL BEHAVIOR GROUPS")
print("=" * 70)

research_summary = (
    combined
    .groupby(
        "research_behavior_group"
    )
    .size()
    .reset_index(
        name="cases"
    )
)

research_summary["percentage"] = (
    research_summary["cases"]
    / len(combined)
    * 100
)

research_summary = research_summary.sort_values(
    "cases",
    ascending=False,
)

print(
    research_summary.to_string(
        index=False
    )
)

research_summary.to_csv(
    OUTPUT_DIR
    / "research_behavior_summary.csv",
    index=False,
)


# ============================================================
# CATEGORY × BEHAVIOR
# ============================================================

print("\n" + "=" * 70)
print("3. BEHAVIOR BY BENCHMARK CATEGORY")
print("=" * 70)

category_behavior = pd.crosstab(
    combined["category"],
    combined["research_behavior_group"],
)

print(
    category_behavior.to_string()
)

category_behavior.to_csv(
    OUTPUT_DIR
    / "category_behavior.csv"
)


# ============================================================
# KEY METRICS
# ============================================================

total = len(combined)

genuine = combined[
    combined["research_behavior_group"]
    == "genuine_epistemic_improvement"
].shape[0]

partial = combined[
    combined["research_behavior_group"]
    == "partial_improvement"
].shape[0]

problematic = combined[
    combined["research_behavior_group"]
    == "problematic"
].shape[0]

unclear_final = combined[
    combined["research_behavior_group"]
    == "unclear"
].shape[0]


print("\n" + "=" * 70)
print("4. FINAL QUALITATIVE METRICS")
print("=" * 70)

print(
    f"\nTotal apparent α=2 corrections: "
    f"{total}"
)

print(
    f"Genuine epistemic improvements: "
    f"{genuine}/{total} "
    f"({genuine / total * 100:.2f}%)"
)

print(
    f"Partial improvements: "
    f"{partial}/{total} "
    f"({partial / total * 100:.2f}%)"
)

print(
    f"Problematic corrections: "
    f"{problematic}/{total} "
    f"({problematic / total * 100:.2f}%)"
)

print(
    f"Still unclear: "
    f"{unclear_final}/{total} "
    f"({unclear_final / total * 100:.2f}%)"
)


# ============================================================
# EFFECTIVE CORRECTION RATE
# ============================================================

# This is NOT a replacement for benchmark accuracy.
# It is a qualitative audit metric.

effective = genuine

print(
    f"\nEffective qualitative correction rate "
    f"(genuine only): "
    f"{effective}/{total} "
    f"({effective / total * 100:.2f}%)"
)


# ============================================================
# SHOW ALL UNCLEAR AUDIT RESULTS
# ============================================================

print("\n" + "=" * 70)
print("5. AUDITED CASES")
print("=" * 70)

for _, row in audit_df.iterrows():

    print("\n" + "-" * 70)

    print(
        f"Set {row['set']} | "
        f"ID {row['id']} | "
        f"{row['category']}"
    )

    print(
        f"\nQUESTION:\n"
        f"{row['question']}"
    )

    print(
        f"\nα=2:\n"
        f"{str(row['alpha_2_answer'])[:1000]}"
    )

    print(
        f"\nFINAL CLASSIFICATION: "
        f"{row['final_behavior_category']}"
    )

    print(
        f"REASON: "
        f"{row['final_behavior_explanation']}"
    )


# ============================================================
# SAVE COMBINED RESULTS
# ============================================================

combined.to_csv(
    OUTPUT_DIR
    / "final_qualitative_cases.csv",
    index=False,
)


# ============================================================
# JSON REPORT
# ============================================================

final_report = {
    "total_apparent_corrections": int(total),

    "genuine_epistemic_improvements": int(
        genuine
    ),

    "partial_improvements": int(
        partial
    ),

    "problematic_corrections": int(
        problematic
    ),

    "unclear_cases": int(
        unclear_final
    ),

    "genuine_correction_rate_percent": round(
        genuine / total * 100,
        2,
    ),

    "partial_improvement_rate_percent": round(
        partial / total * 100,
        2,
    ),

    "problematic_correction_rate_percent": round(
        problematic / total * 100,
        2,
    ),

    "unclear_rate_percent": round(
        unclear_final / total * 100,
        2,
    ),

    "distribution": distribution.to_dict(
        orient="records"
    ),

    "research_behavior_summary":
        research_summary.to_dict(
            orient="records"
        ),
}


with open(
    OUTPUT_DIR
    / "final_qualitative_results.json",
    "w",
    encoding="utf-8",
) as f:

    json.dump(
        final_report,
        f,
        indent=2,
    )


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("FINAL QUALITATIVE AUDIT COMPLETE")
print("=" * 70)

print(
    "\nFiles saved:"
)

print(
    f"  {OUTPUT_DIR / 'unclear_cases_audited.csv'}"
)

print(
    f"  {OUTPUT_DIR / 'final_behavior_distribution.csv'}"
)

print(
    f"  {OUTPUT_DIR / 'research_behavior_summary.csv'}"
)

print(
    f"  {OUTPUT_DIR / 'category_behavior.csv'}"
)

print(
    f"  {OUTPUT_DIR / 'final_qualitative_cases.csv'}"
)

print(
    f"  {OUTPUT_DIR / 'final_qualitative_results.json'}"
)