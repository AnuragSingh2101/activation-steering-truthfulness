import json
import os
import sys
import torch

# ============================================================
# Make project root importable
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.model import load_model
from src.steering import generate_baseline, generate_steered


# ============================================================
# Configuration
# ============================================================

MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"

VECTOR_PATH = "artifacts/vectors/truthfulness_vector.pt"

TARGET_LAYER = 12

MAX_NEW_TOKENS = 60


# ============================================================
# Load questions
# ============================================================

def load_questions(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# Build prompt
# ============================================================

def build_prompt(question):
    return f"Question: {question}\nAnswer:"


# ============================================================
# Decode model output
# ============================================================

def decode_output(model, output):

    if isinstance(output, str):
        return output

    return model.to_string(output[0])


# ============================================================
# Main
# ============================================================

def main():

    # --------------------------------------------------------
    # Check command-line argument
    # --------------------------------------------------------

    if len(sys.argv) != 2:

        print(
            "Usage:\n"
            "  python scripts\\07_generate_robustness.py B\n"
            "  python scripts\\07_generate_robustness.py C"
        )

        sys.exit(1)

    dataset_name = sys.argv[1].upper()

    if dataset_name not in ["B", "C"]:

        print("Dataset must be B or C.")

        sys.exit(1)

    # --------------------------------------------------------
    # Dataset paths
    # --------------------------------------------------------

    dataset_path = (
        f"data/evaluation/set_{dataset_name}.json"
    )

    output_dir = "results/raw/robustness"

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    output_path = (
        f"{output_dir}/set_{dataset_name}_outputs.json"
    )

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        f"ROBUSTNESS GENERATION — SET {dataset_name}"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    questions = load_questions(
        dataset_path
    )

    print(
        f"Dataset: {dataset_path}"
    )

    print(
        f"Questions: {len(questions)}"
    )

    # --------------------------------------------------------
    # Load existing progress
    # --------------------------------------------------------

    if os.path.exists(output_path):

        with open(
            output_path,
            "r",
            encoding="utf-8"
        ) as f:

            results = json.load(f)

        print(
            f"Existing completed questions: "
            f"{len(results)}"
        )

    else:

        results = []

    completed_ids = {
        item["id"]
        for item in results
    }

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("LOADING MODEL")
    print("=" * 60)

    # Your existing project function handles
    # Qwen/Qwen2.5-0.5B-Instruct and CUDA.

    model = load_model()

    # --------------------------------------------------------
    # Load truthfulness vector
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("LOADING TRUTHFULNESS VECTOR")
    print("=" * 60)

    vector_data = torch.load(
        VECTOR_PATH,
        map_location="cuda"
    )

    if not isinstance(vector_data, dict):

        raise TypeError(
            "Expected the truthfulness vector file "
            "to contain a dictionary."
        )

    if "truthfulness_vector" not in vector_data:

        raise KeyError(
            "The vector file does not contain "
            "'truthfulness_vector'. "
            f"Available keys: "
            f"{list(vector_data.keys())}"
        )

    vector = (
        vector_data["truthfulness_vector"]
        .float()
        .cuda()
    )

    print()
    print(
        "Vector shape:",
        vector.shape
    )

    print(
        "Vector norm:",
        vector.norm().item()
    )

    print(
        "Vector device:",
        vector.device
    )

    print(
        "Vector dtype:",
        vector.dtype
    )

    # --------------------------------------------------------
    # Verify vector
    # --------------------------------------------------------

    if vector.ndim != 1:

        raise ValueError(
            f"Expected a 1D truthfulness vector, "
            f"but received shape {vector.shape}"
        )

    if vector.shape[0] != 896:

        print(
            "WARNING: Expected vector dimension 896, "
            f"but received {vector.shape[0]}"
        )

    # --------------------------------------------------------
    # Generate outputs
    # --------------------------------------------------------

    for index, item in enumerate(
        questions,
        start=1
    ):

        # ----------------------------------------------------
        # Extract category and question
        # ----------------------------------------------------

        if isinstance(item, dict):

            category = item.get(
                "category",
                "unknown"
            )

            question = item.get(
                "question",
                ""
            )

        else:

            category = "unknown"

            question = item

        # ----------------------------------------------------
        # Resume support
        # ----------------------------------------------------

        if index in completed_ids:

            print(
                f"Skipping Question "
                f"{index}/{len(questions)} "
                f"(already completed)"
            )

            continue

        # ----------------------------------------------------
        # Question information
        # ----------------------------------------------------

        print()
        print("-" * 70)

        print(
            f"Question {index}/{len(questions)}"
        )

        print(
            f"Category: {category}"
        )

        print(
            f"Question: {question}"
        )

        print("-" * 70)

        prompt = build_prompt(
            question
        )

        # ----------------------------------------------------
        # Baseline α = 0
        # ----------------------------------------------------

        print(
            "Generating baseline..."
        )

        baseline_tokens = generate_baseline(
            model=model,
            prompt=prompt,
            max_new_tokens=MAX_NEW_TOKENS
        )

        baseline_text = decode_output(
            model,
            baseline_tokens
        )

        # ----------------------------------------------------
        # Alpha = 1
        # ----------------------------------------------------

        print(
            "Generating alpha=1..."
        )

        alpha1_tokens = generate_steered(
            model=model,
            prompt=prompt,
            layer=TARGET_LAYER,
            truthfulness_vector=vector,
            alpha=1.0,
            max_new_tokens=MAX_NEW_TOKENS
        )

        alpha1_text = decode_output(
            model,
            alpha1_tokens
        )

        # ----------------------------------------------------
        # Alpha = 2
        # ----------------------------------------------------

        print(
            "Generating alpha=2..."
        )

        alpha2_tokens = generate_steered(
            model=model,
            prompt=prompt,
            layer=TARGET_LAYER,
            truthfulness_vector=vector,
            alpha=2.0,
            max_new_tokens=MAX_NEW_TOKENS
        )

        alpha2_text = decode_output(
            model,
            alpha2_tokens
        )

        # ----------------------------------------------------
        # Store result
        # ----------------------------------------------------

        result = {
            "id": index,
            "category": category,
            "question": question,
            "baseline": baseline_text,
            "alpha_1": alpha1_text,
            "alpha_2": alpha2_text
        }

        results.append(
            result
        )

        # ----------------------------------------------------
        # Save after EVERY question
        # ----------------------------------------------------

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                results,
                f,
                indent=2,
                ensure_ascii=False
            )

        print()
        print(
            f"Saved progress: "
            f"{len(results)}/{len(questions)}"
        )

    # --------------------------------------------------------
    # Final results
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)

    print(
        f"Completed questions: "
        f"{len(results)}/{len(questions)}"
    )

    print(
        f"Output: {output_path}"
    )

    # --------------------------------------------------------
    # GPU information
    # --------------------------------------------------------

    if torch.cuda.is_available():

        print(
            f"GPU allocated: "
            f"{torch.cuda.memory_allocated() / 1024**3:.2f} GB"
        )

        print(
            f"GPU reserved: "
            f"{torch.cuda.memory_reserved() / 1024**3:.2f} GB"
        )


if __name__ == "__main__":
    main()