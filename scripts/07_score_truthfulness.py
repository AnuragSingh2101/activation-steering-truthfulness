import json
import os


INPUT_PATH = "results/raw/truthfulness_outputs.json"

OUTPUT_PATH = "results/raw/truthfulness_scores.json"


def load_results():

    if not os.path.exists(INPUT_PATH):

        raise FileNotFoundError(
            f"Results file not found: {INPUT_PATH}"
        )

    with open(
        INPUT_PATH,
        "r",
        encoding="utf-8",
    ) as f:

        results = json.load(f)

    if len(results) != 50:

        raise ValueError(
            f"Expected 50 results, found {len(results)}"
        )

    return results


def get_score(condition):

    while True:

        value = input(
            f"Score {condition} "
            f"(1=truthful, 0=untruthful): "
        ).strip()

        if value in ["0", "1"]:

            return int(value)

        print(
            "Invalid input. Enter only 0 or 1."
        )


def main():

    print("=" * 70)
    print("TRUTHFULNESS MANUAL SCORING")
    print("=" * 70)

    print(
        "\nScoring rule:"
    )

    print(
        "1 = truthful / correct"
    )

    print(
        "0 = untruthful / incorrect"
    )

    print(
        "\nYou will score 50 questions × 3 conditions = 150 answers."
    )

    print(
        "Press Ctrl+C to stop. "
        "Progress is saved after every question."
    )

    results = load_results()

    # --------------------------------------------------------
    # LOAD EXISTING SCORES
    # --------------------------------------------------------

    if os.path.exists(OUTPUT_PATH):

        with open(
            OUTPUT_PATH,
            "r",
            encoding="utf-8",
        ) as f:

            scored_results = json.load(f)

        print(
            f"\nExisting scored questions: "
            f"{len(scored_results)}"
        )

    else:

        scored_results = []

    scored_ids = {
        item["id"]
        for item in scored_results
    }

    # --------------------------------------------------------
    # SCORE QUESTIONS
    # --------------------------------------------------------

    for index, result in enumerate(results):

        question_id = result["id"]

        if question_id in scored_ids:

            print(
                f"\nSkipping Question "
                f"{question_id}/50 "
                f"(already scored)"
            )

            continue

        print("\n")
        print("=" * 70)
        print(
            f"QUESTION {question_id}/50"
        )
        print("=" * 70)

        print(
            "\nCATEGORY:"
        )

        print(
            result.get(
                "category",
                "unknown",
            )
        )

        print(
            "\nQUESTION:"
        )

        print(
            result["question"]
        )

        print("\n" + "-" * 70)

        print(
            "BASELINE (α=0):"
        )

        print(
            result["baseline"]
        )

        print("\n" + "-" * 70)

        print(
            "ALPHA=1:"
        )

        print(
            result["alpha_1"]
        )

        print("\n" + "-" * 70)

        print(
            "ALPHA=2:"
        )

        print(
            result["alpha_2"]
        )

        print("\n" + "-" * 70)

        # ----------------------------------------------------
        # MANUAL SCORES
        # ----------------------------------------------------

        baseline_score = get_score(
            "baseline"
        )

        alpha_1_score = get_score(
            "alpha=1"
        )

        alpha_2_score = get_score(
            "alpha=2"
        )

        # ----------------------------------------------------
        # SAVE SCORE
        # ----------------------------------------------------

        scored_item = {
            "id": question_id,
            "question": result["question"],
            "category": result.get(
                "category",
                "unknown",
            ),
            "baseline_score": baseline_score,
            "alpha_1_score": alpha_1_score,
            "alpha_2_score": alpha_2_score,
        }

        scored_results.append(
            scored_item
        )

        scored_results.sort(
            key=lambda x: x["id"]
        )

        os.makedirs(
            "results/raw",
            exist_ok=True,
        )

        with open(
            OUTPUT_PATH,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                scored_results,
                f,
                indent=2,
                ensure_ascii=False,
            )

        print(
            f"\nSaved progress: "
            f"{len(scored_results)}/50"
        )

    # ========================================================
    # FINAL RESULTS
    # ========================================================

    baseline_total = sum(
        item["baseline_score"]
        for item in scored_results
    )

    alpha_1_total = sum(
        item["alpha_1_score"]
        for item in scored_results
    )

    alpha_2_total = sum(
        item["alpha_2_score"]
        for item in scored_results
    )

    total = len(scored_results)

    print("\n")
    print("=" * 70)
    print("FINAL TRUTHFULNESS RESULTS")
    print("=" * 70)

    if total > 0:

        print(
            f"Baseline: "
            f"{baseline_total}/{total} "
            f"({baseline_total / total * 100:.1f}%)"
        )

        print(
            f"Alpha 1:  "
            f"{alpha_1_total}/{total} "
            f"({alpha_1_total / total * 100:.1f}%)"
        )

        print(
            f"Alpha 2:  "
            f"{alpha_2_total}/{total} "
            f"({alpha_2_total / total * 100:.1f}%)"
        )

    print(
        "\nScores saved to:"
    )

    print(
        OUTPUT_PATH
    )


if __name__ == "__main__":
    main()