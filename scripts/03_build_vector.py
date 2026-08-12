import gc
import json
import os

import torch
from dotenv import load_dotenv

from src.model import load_model
from src.prompts import build_prompt
from src.activations import extract_direction


load_dotenv()


DATASET_PATH = (
    "data/contrastive_examples.json"
)

OUTPUT_PATH = (
    "artifacts/vectors/truthfulness_vector.pt"
)

LAYER = int(
    os.getenv(
        "STEERING_LAYER",
        "12",
    )
)


print("=" * 70)
print("TRUTHFULNESS VECTOR EXTRACTION")
print("=" * 70)

print("Layer:", LAYER)


# --------------------------------------------------
# LOAD DATASET
# --------------------------------------------------

with open(
    DATASET_PATH,
    "r",
    encoding="utf-8",
) as f:

    examples = json.load(f)


print(
    "Training examples:",
    len(examples),
)


assert len(examples) == 50


# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

model = load_model()


# --------------------------------------------------
# EXTRACT DIRECTIONS
# --------------------------------------------------

directions = []


for i, example in enumerate(examples):

    print(
        f"\nProcessing example "
        f"{i + 1}/{len(examples)}"
    )

    direction = extract_direction(
        model=model,
        question=example["question"],
        truthful=example["truthful"],
        false=example["false"],
        layer=LAYER,
        build_prompt=build_prompt,
    )

    print(
        "Direction shape:",
        direction.shape,
    )

    print(
        "Direction norm:",
        direction.norm().item(),
    )

    directions.append(direction)

    gc.collect()

    if torch.cuda.is_available():
        torch.cuda.empty_cache()


# --------------------------------------------------
# STACK DIRECTIONS
# --------------------------------------------------

directions_tensor = torch.stack(
    directions
)


print("\n" + "=" * 70)
print("DIRECTIONS COMPLETE")
print("=" * 70)

print(
    "Directions shape:",
    directions_tensor.shape,
)


# --------------------------------------------------
# BUILD MEAN VECTOR
# --------------------------------------------------

truthfulness_vector = (
    directions_tensor.mean(dim=0)
)


# --------------------------------------------------
# NORMALIZE
# --------------------------------------------------

norm = truthfulness_vector.norm()

if norm == 0:

    raise ValueError(
        "Truthfulness vector has zero norm."
    )


truthfulness_vector = (
    truthfulness_vector / norm
)


print(
    "\nTruthfulness vector shape:",
    truthfulness_vector.shape,
)

print(
    "Truthfulness vector norm:",
    truthfulness_vector.norm().item(),
)


# --------------------------------------------------
# SAVE
# --------------------------------------------------

os.makedirs(
    os.path.dirname(OUTPUT_PATH),
    exist_ok=True,
)


torch.save(
    {
        "truthfulness_vector":
            truthfulness_vector,

        "directions":
            directions_tensor,

        "layer":
            LAYER,

        "model":
            os.getenv(
                "MODEL_NAME",
                "Qwen/Qwen2.5-0.5B-Instruct",
            ),

        "num_examples":
            len(examples),
    },
    OUTPUT_PATH,
)


print("\n" + "=" * 70)
print("VECTOR SAVED")
print("=" * 70)

print(
    "File:",
    OUTPUT_PATH,
)

print(
    "Final shape:",
    truthfulness_vector.shape,
)

print(
    "Final norm:",
    truthfulness_vector.norm().item(),
)

print("\nExperiment complete.")
