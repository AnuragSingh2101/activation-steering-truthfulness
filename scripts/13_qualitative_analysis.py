import json
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIG
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

ANALYSIS_DIR = ROOT / "results" / "analysis"
RAW_DIR = ROOT / "results" / "raw"

OUTPUT_DIR = ANALYSIS_DIR / "qualitative"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COMBINED_SCORES = ANALYSIS_DIR / "combined_question_results.csv"

SET_A_OUTPUTS = RAW_DIR / "truthfulness_outputs.json"
SET_B_OUTPUTS = RAW_DIR / "robustness" / "set_B_outputs.json"
SET_C_OUTPUTS = RAW_DIR / "robustness" / "set_C_outputs.json"


# ============================================================
# HELPERS
# ============================================================

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_output_records(data):
    """Handle common JSON output structures."""

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        for key in ["outputs", "results", "questions"]:
            if isinstance(data.get(key), list):
                return data[key]

        for value in data.values():
            if isinstance(value, list) and value:
                if isinstance(value[0], dict):
                    return value

    raise ValueError(
        "Could not locate question-level output records."
    )


def get_question_text(record):
    question = record.get("question")

    if isinstance(question, str):
        return question

    if isinstance(question, dict):
        return question.get("question", "")

    return ""


def get_category(record):
    question = record.get("question")

    if isinstance(question, dict):
        category = question.get("category")
        if category:
            return category

    return record.get("category", "unknown")


def get_answer(record, condition):
    """
    Supports Set A:
        baseline
        alpha_1
        alpha_2

    Also supports possible B/C field names.
    """

    possible_names = {
        "baseline": [
            "baseline",
            "baseline_answer",
            "answer_baseline",
            "alpha_0_answer",
            "alpha_0",
        ],
        "alpha_1": [
            "alpha_1",
            "alpha_1_answer",
            "answer_alpha_1",
        ],
        "alpha_2": [
            "alpha_2",
            "alpha_2_answer",
            "answer_alpha_2",
        ],
    }

    for key in possible_names[condition]:

        if key in record:

            value = record[key]

            if isinstance(value, str):
                return value

            if value is not None:
                return str(value)

    return ""


# ============================================================
# LOAD SCORES
# ============================================================

print("=" * 70)
print("QUALITATIVE ANALYSIS — ACTIVATION STEERING")
print("=" * 70)

scores_df = pd.read_csv(COMBINED_SCORES)

print(f"\nLoaded scored questions: {len(scores_df)}")


# ============================================================
# LOAD ALL RAW OUTPUTS
# ============================================================

print("\nLoading raw model outputs...")

set_a_outputs = extract_output_records(
    load_json(SET_A_OUTPUTS)
)

set_b_outputs = extract_output_records(
    load_json(SET_B_OUTPUTS)
)

set_c_outputs = extract_output_records(
    load_json(SET_C_OUTPUTS)
)

print(f"Set A output records: {len(set_a_outputs)}")
print(f"Set B output records: {len(set_b_outputs)}")
print(f"Set C output records: {len(set_c_outputs)}")


# ============================================================
# CREATE LOOKUP
# ============================================================

output_lookup = {}


for dataset, records in [
    ("A", set_a_outputs),
    ("B", set_b_outputs),
    ("C", set_c_outputs),
]:

    for i, record in enumerate(records, start=1):

        record_id = record.get("id", i)

        output_lookup[(dataset, int(record_id))] = {
            "question": get_question_text(record),
            "category": get_category(record),
            "baseline_answer": get_answer(
                record,
                "baseline",
            ),
            "alpha_1_answer": get_answer(
                record,
                "alpha_1",
            ),
            "alpha_2_answer": get_answer(
                record,
                "alpha_2",
            ),
        }


# ============================================================
# VERIFY LOOKUP
# ============================================================

print("\nOutput lookup entries:", len(output_lookup))

expected_outputs = 150

if len(output_lookup) != expected_outputs:
    print(
        f"WARNING: Expected {expected_outputs} output records "
        f"but found {len(output_lookup)}."
    )


# ============================================================
# COMBINE SCORES + OUTPUTS
# ============================================================

qualitative_rows = []

missing_answers = []

for _, row in scores_df.iterrows():

    dataset = str(row["set"])
    record_id = int(row["id"])

    output = output_lookup.get(
        (dataset, record_id),
        {},
    )

    baseline_answer = output.get(
        "baseline_answer",
        "",
    )

    alpha_1_answer = output.get(
        "alpha_1_answer",
        "",
    )

    alpha_2_answer = output.get(
        "alpha_2_answer",
        "",
    )

    if not baseline_answer or not alpha_2_answer:
        missing_answers.append(
            (dataset, record_id)
        )

    qualitative_rows.append({
        "set": dataset,
        "id": record_id,
        "category": row["category"],
        "question": row["question"],

        "baseline_score": int(
            row["baseline"]
        ),

        "alpha_1_score": int(
            row["alpha_1"]
        ),

        "alpha_2_score": int(
            row["alpha_2"]
        ),

        "baseline_answer": baseline_answer,
        "alpha_1_answer": alpha_1_answer,
        "alpha_2_answer": alpha_2_answer,
    })


qual_df = pd.DataFrame(
    qualitative_rows
)


# ============================================================
# OUTPUT RETRIEVAL CHECK
# ============================================================

print("\n" + "=" * 70)
print("OUTPUT RETRIEVAL CHECK")
print("=" * 70)

print(
    f"\nQuestions with missing baseline/α=2 output: "
    f"{len(missing_answers)}"
)

if missing_answers:

    print("\nMissing entries:")

    for dataset, record_id in missing_answers[:20]:

        print(
            f"  Set {dataset} | ID {record_id}"
        )

else:

    print(
        "\nAll 150 questions have baseline and α=2 outputs."
    )


# ============================================================
# 1. CORRECTED ANSWERS
# ============================================================

corrected = qual_df[
    (qual_df["baseline_score"] == 0)
    & (qual_df["alpha_2_score"] == 1)
].copy()

print("\n" + "=" * 70)
print("1. CORRECTED ANSWERS")
print("=" * 70)

print(
    f"\nBaseline incorrect → α=2 correct: "
    f"{len(corrected)}"
)

corrected.to_csv(
    OUTPUT_DIR / "corrected_answers.csv",
    index=False,
)


# ============================================================
# 2. REGRESSIONS
# ============================================================

regressions = qual_df[
    (qual_df["baseline_score"] == 1)
    & (qual_df["alpha_2_score"] == 0)
].copy()

print("\n" + "=" * 70)
print("2. REGRESSIONS")
print("=" * 70)

print(
    f"\nBaseline correct → α=2 incorrect: "
    f"{len(regressions)}"
)

regressions.to_csv(
    OUTPUT_DIR / "regressions.csv",
    index=False,
)


# ============================================================
# 3. PERSISTENT FAILURES
# ============================================================

persistent_failures = qual_df[
    (qual_df["baseline_score"] == 0)
    & (qual_df["alpha_2_score"] == 0)
].copy()

print("\n" + "=" * 70)
print("3. PERSISTENT FAILURES")
print("=" * 70)

print(
    f"\nBaseline incorrect → α=2 still incorrect: "
    f"{len(persistent_failures)}"
)

persistent_failures.to_csv(
    OUTPUT_DIR / "persistent_failures.csv",
    index=False,
)


# ============================================================
# 4. α=1 → α=2 CORRECTIONS
# ============================================================

alpha1_to_alpha2 = qual_df[
    (qual_df["alpha_1_score"] == 0)
    & (qual_df["alpha_2_score"] == 1)
].copy()

print("\n" + "=" * 70)
print("4. α=1 → α=2 ADDITIONAL CORRECTIONS")
print("=" * 70)

print(
    f"\nα=1 incorrect → α=2 correct: "
    f"{len(alpha1_to_alpha2)}"
)

alpha1_to_alpha2.to_csv(
    OUTPUT_DIR / "alpha1_to_alpha2_corrections.csv",
    index=False,
)


# ============================================================
# 5. CORRECTIONS BY CATEGORY
# ============================================================

print("\n" + "=" * 70)
print("5. CORRECTIONS BY CATEGORY")
print("=" * 70)

correction_by_category = (
    corrected
    .groupby("category")
    .size()
    .reset_index(
        name="corrections"
    )
)

category_totals = (
    qual_df
    .groupby("category")
    .size()
    .reset_index(
        name="total_questions"
    )
)

category_summary = category_totals.merge(
    correction_by_category,
    on="category",
    how="left",
)

category_summary["corrections"] = (
    category_summary["corrections"]
    .fillna(0)
    .astype(int)
)

category_summary["correction_rate"] = (
    category_summary["corrections"]
    / category_summary["total_questions"]
    * 100
)

print(
    category_summary.to_string(
        index=False
    )
)

category_summary.to_csv(
    OUTPUT_DIR / "corrections_by_category.csv",
    index=False,
)


# ============================================================
# 6. CORRECTIONS BY DATASET
# ============================================================

print("\n" + "=" * 70)
print("6. CORRECTIONS BY DATASET")
print("=" * 70)

dataset_summary = (
    corrected
    .groupby("set")
    .size()
    .reset_index(
        name="corrections"
    )
)

dataset_totals = (
    qual_df
    .groupby("set")
    .size()
    .reset_index(
        name="total_questions"
    )
)

dataset_summary = dataset_totals.merge(
    dataset_summary,
    on="set",
    how="left",
)

dataset_summary["corrections"] = (
    dataset_summary["corrections"]
    .fillna(0)
    .astype(int)
)

dataset_summary["correction_rate"] = (
    dataset_summary["corrections"]
    / dataset_summary["total_questions"]
    * 100
)

print(
    dataset_summary.to_string(
        index=False
    )
)

dataset_summary.to_csv(
    OUTPUT_DIR / "corrections_by_dataset.csv",
    index=False,
)


# ============================================================
# 7. REPRESENTATIVE CORRECTED CASES
# ============================================================

print("\n" + "=" * 70)
print("7. REPRESENTATIVE CORRECTED CASES")
print("=" * 70)

sample_count = min(
    10,
    len(corrected)
)

for _, row in corrected.head(
    sample_count
).iterrows():

    print("\n" + "-" * 70)

    print(
        f"Set {row['set']} | "
        f"ID {row['id']} | "
        f"Category: {row['category']}"
    )

    print(
        f"\nQUESTION:\n"
        f"{row['question']}"
    )

    print(
        f"\nBASELINE:\n"
        f"{row['baseline_answer'][:1200]}"
    )

    print(
        f"\nα=2:\n"
        f"{row['alpha_2_answer'][:1200]}"
    )


# ============================================================
# 8. REGRESSIONS
# ============================================================

print("\n" + "=" * 70)
print("8. REGRESSIONS")
print("=" * 70)

if len(regressions) == 0:

    print("\nNo regressions found.")

else:

    for _, row in regressions.iterrows():

        print("\n" + "-" * 70)

        print(
            f"Set {row['set']} | "
            f"ID {row['id']} | "
            f"Category: {row['category']}"
        )

        print(
            f"\nQUESTION:\n"
            f"{row['question']}"
        )

        print(
            f"\nBASELINE:\n"
            f"{row['baseline_answer'][:1500]}"
        )

        print(
            f"\nα=2:\n"
            f"{row['alpha_2_answer'][:1500]}"
        )


# ============================================================
# 9. SAVE HUMAN-READABLE REPORT
# ============================================================

report_path = (
    OUTPUT_DIR / "qualitative_report.md"
)

with open(
    report_path,
    "w",
    encoding="utf-8",
) as f:

    f.write(
        "# Qualitative Activation-Steering Analysis\n\n"
    )

    f.write(
        f"Total evaluated questions: "
        f"**{len(qual_df)}**\n\n"
    )

    f.write(
        f"Baseline → α=2 corrected: "
        f"**{len(corrected)}**\n\n"
    )

    f.write(
        f"Baseline → α=2 regressions: "
        f"**{len(regressions)}**\n\n"
    )

    f.write(
        f"Persistent failures: "
        f"**{len(persistent_failures)}**\n\n"
    )

    f.write(
        "## Corrected Answers\n\n"
    )

    for _, row in corrected.iterrows():

        f.write("---\n\n")

        f.write(
            f"### Set {row['set']} — "
            f"Question {row['id']}\n\n"
        )

        f.write(
            f"**Category:** "
            f"{row['category']}\n\n"
        )

        f.write(
            f"**Question:** "
            f"{row['question']}\n\n"
        )

        f.write(
            "#### Baseline (α=0)\n\n"
        )

        f.write(
            f"{row['baseline_answer']}\n\n"
        )

        f.write(
            "#### α=2\n\n"
        )

        f.write(
            f"{row['alpha_2_answer']}\n\n"
        )

    f.write(
        "\n## Regressions\n\n"
    )

    if len(regressions) == 0:

        f.write(
            "No baseline-correct → "
            "α=2-incorrect regressions were found.\n"
        )

    else:

        for _, row in regressions.iterrows():

            f.write("---\n\n")

            f.write(
                f"### Set {row['set']} — "
                f"Question {row['id']}\n\n"
            )

            f.write(
                f"**Category:** "
                f"{row['category']}\n\n"
            )

            f.write(
                f"**Question:** "
                f"{row['question']}\n\n"
            )

            f.write(
                "#### Baseline (α=0)\n\n"
            )

            f.write(
                f"{row['baseline_answer']}\n\n"
            )

            f.write(
                "#### α=2\n\n"
            )

            f.write(
                f"{row['alpha_2_answer']}\n\n"
            )


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("QUALITATIVE ANALYSIS COMPLETE")
print("=" * 70)

print(
    f"\nCorrected cases:          "
    f"{len(corrected)}"
)

print(
    f"Regressions:              "
    f"{len(regressions)}"
)

print(
    f"Persistent failures:      "
    f"{len(persistent_failures)}"
)

print(
    f"α=1 → α=2 corrections:    "
    f"{len(alpha1_to_alpha2)}"
)

print("\nFiles saved:")

print(
    f"  {OUTPUT_DIR / 'corrected_answers.csv'}"
)

print(
    f"  {OUTPUT_DIR / 'regressions.csv'}"
)

print(
    f"  {OUTPUT_DIR / 'persistent_failures.csv'}"
)

print(
    f"  {OUTPUT_DIR / 'alpha1_to_alpha2_corrections.csv'}"
)

print(
    f"  {OUTPUT_DIR / 'corrections_by_category.csv'}"
)

print(
    f"  {OUTPUT_DIR / 'corrections_by_dataset.csv'}"
)

print(
    f"  {report_path}"
)