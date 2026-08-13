import json
import os
import torch

from src.model import load_model
from src.steering import (
    generate_baseline,
    generate_steered,
)


# CONFIGURATION

DATASET_PATH = "data/evaluation/set_A.json"

VECTOR_PATH = "artifacts/vectors/truthfulness_vector.pt"

OUTPUT_PATH = "results/raw/truthfulness_outputs.json"

STEERING_LAYER = 12

MAX_NEW_TOKENS = 60


# LOAD DATASET

def load_dataset():

    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as f:

        data = json.load(f)

    if len(data) != 50:
        raise ValueError(
            f"Expected 50 questions, found {len(data)}"
        )

    return data


# LOAD EXISTING RESULTS

def load_existing_results():

    if not os.path.exists(OUTPUT_PATH):
        return []

    try:

        with open(
            OUTPUT_PATH,
            "r",
            encoding="utf-8",
        ) as f:

            results = json.load(f)

        if not isinstance(results, list):
            print(
                "Existing results file is not a list."
            )
            return []

        return results

    except Exception as e:

        print(
            "Could not load existing results:",
            e,
        )

        return []


# LOAD VECTOR

def load_truthfulness_vector():

    if not os.path.exists(VECTOR_PATH):

        raise FileNotFoundError(
            f"Vector not found: {VECTOR_PATH}"
        )

    data = torch.load(
        VECTOR_PATH,
        map_location="cpu",
    )

    # Support both possible saved formats.
    if isinstance(data, dict):

        if "truthfulness_vector" in data:
            vector = data["truthfulness_vector"]

        elif "vector" in data:
            vector = data["vector"]

        else:
            raise KeyError(
                "Could not find truthfulness_vector "
                "or vector in saved file."
            )

    else:

        vector = data

    vector = vector.float()

    if vector.shape != torch.Size([896]):

        raise ValueError(
            f"Expected vector shape [896], "
            f"found {vector.shape}"
        )

    return vector


# SAVE RESULTS

def save_results(results):

    os.makedirs(
        os.path.dirname(OUTPUT_PATH),
        exist_ok=True,
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False,
        )


# MAIN

def main():

    print("=" * 70)
    print("TRUTHFULNESS GENERATION")
    print("=" * 70)

    # DATASET

    questions = load_dataset()

    print(
        f"Dataset loaded: {len(questions)} questions"
    )

    # EXISTING RESULTS

    results = load_existing_results()

    completed_ids = {
        item.get("id")
        for item in results
        if item.get("id") is not None
    }

    print(
        f"Existing completed questions: "
        f"{len(completed_ids)}"
    )

    if completed_ids:

        print(
            "Completed IDs:",
            sorted(completed_ids),
        )

    # CHECK FOR ALREADY COMPLETE

    if len(completed_ids) >= len(questions):

        print("\nAll 50 questions are already complete.")

        print(
            f"Results file: {OUTPUT_PATH}"
        )

        return

    # MODEL

    print("\n" + "=" * 70)
    print("LOADING MODEL")
    print("=" * 70)

    model = load_model()

    # VECTOR

    print("\n" + "=" * 70)
    print("LOADING TRUTHFULNESS VECTOR")
    print("=" * 70)

    truthfulness_vector = (
        load_truthfulness_vector()
    )

    print(
        "Vector shape:",
        truthfulness_vector.shape,
    )

    print(
        "Vector norm:",
        truthfulness_vector.norm().item(),
    )

    # PREPARE VECTOR ON MODEL DEVICE ONCE

    model_device = next(
        model.parameters()
    ).device

    model_dtype = next(
        model.parameters()
    ).dtype

    truthfulness_vector = (
        truthfulness_vector
        .to(
            device=model_device,
            dtype=model_dtype,
        )
        .contiguous()
    )

    print(
        "Vector device:",
        truthfulness_vector.device,
    )

    print(
        "Vector dtype:",
        truthfulness_vector.dtype,
    )

    # GENERATE MISSING QUESTIONS

    for index, item in enumerate(questions):

        question_id = index + 1

        # Already completed?
        if question_id in completed_ids:

            print(
                f"\nSkipping Question "
                f"{question_id}/50 "
                f"(already completed)"
            )

            continue

        question = item["question"]

        category = item.get(
            "category",
            "unknown",
        )

        print("\n" + "-" * 70)

        print(
            f"Question {question_id}/50"
        )

        print(
            f"Category: {category}"
        )

        print(
            f"Question: {question}"
        )

        result = {
            "id": question_id,
            "question": question,
            "category": category,
        }

        # BASELINE

        print("Generating baseline...")

        baseline = generate_baseline(
            model=model,
            prompt=question,
            max_new_tokens=MAX_NEW_TOKENS,
        )

        result["baseline"] = baseline

        # ALPHA 1

        print("Generating alpha=1...")

        alpha_1 = generate_steered(
            model=model,
            prompt=question,
            layer=STEERING_LAYER,
            truthfulness_vector=truthfulness_vector,
            alpha=1.0,
            max_new_tokens=MAX_NEW_TOKENS,
        )

        result["alpha_1"] = alpha_1

        # ALPHA 2

        print("Generating alpha=2...")

        alpha_2 = generate_steered(
            model=model,
            prompt=question,
            layer=STEERING_LAYER,
            truthfulness_vector=truthfulness_vector,
            alpha=2.0,
            max_new_tokens=MAX_NEW_TOKENS,
        )

        result["alpha_2"] = alpha_2

        # APPEND

        results.append(result)

        completed_ids.add(question_id)

        # SAVE IMMEDIATELY

        save_results(results)

        print(
            f"Saved progress: "
            f"{len(completed_ids)}/50 questions"
        )

        # CLEAR CUDA CACHE

        if torch.cuda.is_available():

            torch.cuda.empty_cache()

    # FINAL

    print("\n" + "=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)

    print(
        f"Completed questions: "
        f"{len(completed_ids)}/50"
    )

    print(
        "Output:",
        OUTPUT_PATH,
    )

    if torch.cuda.is_available():

        print(
            "GPU allocated:",
            f"{torch.cuda.memory_allocated() / 1024**3:.2f} GB",
        )

        print(
            "GPU reserved:",
            f"{torch.cuda.memory_reserved() / 1024**3:.2f} GB",
        )


if __name__ == "__main__":
    main()