import json
import os
import sys


# ============================================================
# Configuration
# ============================================================

if len(sys.argv) != 2:
    print(
        "Usage:\n"
        "  python scripts/10_score_robustness.py B\n"
        "  python scripts/10_score_robustness.py C"
    )
    sys.exit(1)

SET_NAME = sys.argv[1].upper()

if SET_NAME not in ["B", "C"]:
    print("Error: Dataset must be B or C.")
    sys.exit(1)

INPUT_PATH = (
    f"results/raw/robustness/set_{SET_NAME}_outputs.json"
)

OUTPUT_PATH = (
    f"results/raw/robustness/set_{SET_NAME}_scores.json"
)



# ============================================================
# Helpers
# ============================================================

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )


def get_score(label):
    """
    Ask the user for a binary truthfulness score.

    1 = truthful
    0 = untruthful
    """

    while True:

        value = input(
            f"{label} score (0=untruthful, 1=truthful): "
        ).strip()

        if value in ["0", "1"]:
            return int(value)

        print(
            "Invalid input. Please enter only 0 or 1."
        )


# ============================================================
# Calculate statistics
# ============================================================

def calculate_results(scores):

    total = len(scores)

    baseline_correct = sum(
        item["baseline_score"]
        for item in scores
    )

    alpha1_correct = sum(
        item["alpha_1_score"]
        for item in scores
    )

    alpha2_correct = sum(
        item["alpha_2_score"]
        for item in scores
    )

    baseline_accuracy = (
        baseline_correct / total * 100
        if total else 0
    )

    alpha1_accuracy = (
        alpha1_correct / total * 100
        if total else 0
    )

    alpha2_accuracy = (
        alpha2_correct / total * 100
        if total else 0
    )

    return {
        "total_questions": total,

        "baseline": {
            "correct": baseline_correct,
            "total": total,
            "accuracy": round(
                baseline_accuracy,
                2
            )
        },

        "alpha_1": {
            "correct": alpha1_correct,
            "total": total,
            "accuracy": round(
                alpha1_accuracy,
                2
            )
        },

        "alpha_2": {
            "correct": alpha2_correct,
            "total": total,
            "accuracy": round(
                alpha2_accuracy,
                2
            )
        }
    }


# ============================================================
# Main
# ============================================================

def main():

    print()
    print("=" * 70)
    print(f"TRUTHFULNESS SCORING — SET {SET_NAME}")
    print("=" * 70)

    # --------------------------------------------------------
    # Check input file
    # --------------------------------------------------------

    if not os.path.exists(INPUT_PATH):

        print()
        print(
            f"ERROR: Input file not found:"
        )

        print(INPUT_PATH)

        print()
        print(
            "Run the robustness generation script first."
        )

        sys.exit(1)

    # --------------------------------------------------------
    # Load generated outputs
    # --------------------------------------------------------

    outputs = load_json(
        INPUT_PATH
    )

    print()
    print(
        f"Loaded {len(outputs)} questions."
    )

    # --------------------------------------------------------
    # Load existing scores
    # --------------------------------------------------------

    if os.path.exists(OUTPUT_PATH):

        score_data = load_json(
            OUTPUT_PATH
        )

        scores = score_data.get(
            "scores",
            []
        )

        print(
            f"Existing scored questions: "
            f"{len(scores)}"
        )

    else:

        scores = []

        print(
            "No existing scores found."
        )

    # --------------------------------------------------------
    # Determine completed IDs
    # --------------------------------------------------------

    completed_ids = {
        item["id"]
        for item in scores
    }

    # --------------------------------------------------------
    # Score each question
    # --------------------------------------------------------

    for item in outputs:

        question_id = item["id"]

        # ----------------------------------------------------
        # Resume support
        # ----------------------------------------------------

        if question_id in completed_ids:

            print(
                f"\nSkipping Question "
                f"{question_id}/{len(outputs)} "
                f"(already scored)"
            )

            continue

        # ----------------------------------------------------
        # Extract fields
        # ----------------------------------------------------

        category = item.get(
            "category",
            "unknown"
        )

        question = item.get(
            "question",
            ""
        )

        baseline = item.get(
            "baseline",
            ""
        )

        alpha1 = item.get(
            "alpha_1",
            ""
        )

        alpha2 = item.get(
            "alpha_2",
            ""
        )

        # ----------------------------------------------------
        # Display question
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print(
            f"QUESTION {question_id}/{len(outputs)}"
        )
        print("=" * 70)

        print()
        print(
            f"CATEGORY:\n{category}"
        )

        print()
        print(
            f"QUESTION:\n{question}"
        )

        print()
        print("-" * 70)
        print("BASELINE (α=0)")
        print("-" * 70)
        print(baseline)

        print()
        print("-" * 70)
        print("ALPHA=1")
        print("-" * 70)
        print(alpha1)

        print()
        print("-" * 70)
        print("ALPHA=2")
        print("-" * 70)
        print(alpha2)

        # ----------------------------------------------------
        # Score outputs
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print("SCORING")
        print("=" * 70)

        print(
            "\nUse:"
            "\n  1 = truthful"
            "\n  0 = untruthful"
        )

        baseline_score = get_score(
            "\nBaseline"
        )

        alpha1_score = get_score(
            "Alpha=1"
        )

        alpha2_score = get_score(
            "Alpha=2"
        )

        # ----------------------------------------------------
        # Save score
        # ----------------------------------------------------

        score_entry = {
            "id": question_id,
            "category": category,
            "question": question,

            "baseline_score": baseline_score,
            "alpha_1_score": alpha1_score,
            "alpha_2_score": alpha2_score
        }

        scores.append(
            score_entry
        )

        # ----------------------------------------------------
        # Calculate current results
        # ----------------------------------------------------

        current_results = calculate_results(
            scores
        )

        # ----------------------------------------------------
        # Save after every question
        # ----------------------------------------------------

        save_data = {
            "set": SET_NAME,
            "scores": scores,
            "results": current_results
        }

        save_json(
            OUTPUT_PATH,
            save_data
        )

        # ----------------------------------------------------
        # Display current progress
        # ----------------------------------------------------

        print()
        print(
            f"Saved progress: "
            f"{len(scores)}/{len(outputs)}"
        )

        print()
        print(
            "Current accuracy:"
        )

        print(
            f"Baseline: "
            f"{current_results['baseline']['correct']}/"
            f"{current_results['baseline']['total']} "
            f"("
            f"{current_results['baseline']['accuracy']}%"
            f")"
        )

        print(
            f"Alpha=1:  "
            f"{current_results['alpha_1']['correct']}/"
            f"{current_results['alpha_1']['total']} "
            f"("
            f"{current_results['alpha_1']['accuracy']}%"
            f")"
        )

        print(
            f"Alpha=2:  "
            f"{current_results['alpha_2']['correct']}/"
            f"{current_results['alpha_2']['total']} "
            f"("
            f"{current_results['alpha_2']['accuracy']}%"
            f")"
        )

    # ========================================================
    # Final results
    # ========================================================

    final_results = calculate_results(
        scores
    )

    save_data = {
        "set": SET_NAME,
        "scores": scores,
        "results": final_results
    }

    save_json(
        OUTPUT_PATH,
        save_data
    )

    print()
    print("=" * 70)
    print(f"SET {SET_NAME} SCORING COMPLETE")
    print("=" * 70)

    print()
    print(
        f"Questions scored: "
        f"{len(scores)}/{len(outputs)}"
    )

    print()

    print(
        f"Baseline: "
        f"{final_results['baseline']['correct']}/"
        f"{final_results['baseline']['total']} "
        f"("
        f"{final_results['baseline']['accuracy']}%"
        f")"
    )

    print(
        f"Alpha=1:  "
        f"{final_results['alpha_1']['correct']}/"
        f"{final_results['alpha_1']['total']} "
        f"("
        f"{final_results['alpha_1']['accuracy']}%"
        f")"
    )

    print(
        f"Alpha=2:  "
        f"{final_results['alpha_2']['correct']}/"
        f"{final_results['alpha_2']['total']} "
        f"("
        f"{final_results['alpha_2']['accuracy']}%"
        f")"
    )

    print()
    print(
        f"Scores saved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()