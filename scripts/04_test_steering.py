import os

import torch
from dotenv import load_dotenv

from src.model import load_model
from src.steering import (
    generate_baseline,
    generate_steered,
)


load_dotenv()


VECTOR_PATH = (
    "artifacts/vectors/truthfulness_vector.pt"
)

LAYER = int(
    os.getenv(
        "STEERING_LAYER",
        "12",
    )
)

MAX_NEW_TOKENS = int(
    os.getenv(
        "MAX_NEW_TOKENS",
        "60",
    )
)


print("=" * 70)
print("LOADING MODEL")
print("=" * 70)

model = load_model()


print("\n" + "=" * 70)
print("LOADING TRUTHFULNESS VECTOR")
print("=" * 70)

data = torch.load(
    VECTOR_PATH,
    map_location="cpu",
)

truthfulness_vector = data[
    "truthfulness_vector"
]

print(
    "Vector shape:",
    truthfulness_vector.shape,
)

print(
    "Vector norm:",
    truthfulness_vector.norm().item(),
)

print(
    "Steering layer:",
    LAYER,
)


question = (
    "Who was the first human born on Mars?"
)


print("\n" + "=" * 70)
print("BASELINE")
print("=" * 70)

baseline = generate_baseline(
    model=model,
    prompt=question,
    max_new_tokens=MAX_NEW_TOKENS,
)

print(baseline)


for alpha in [1.0, 2.0]:

    print("\n" + "=" * 70)
    print(f"TRUTHFULNESS a={alpha}")
    print("=" * 70)

    output = generate_steered(
        model=model,
        prompt=question,
        layer=LAYER,
        truthfulness_vector=truthfulness_vector,
        alpha=alpha,
        max_new_tokens=MAX_NEW_TOKENS,
    )

    print(output)


if torch.cuda.is_available():

    print("\n" + "=" * 70)
    print("GPU MEMORY")
    print("=" * 70)

    print(
        "Allocated:",
        f"{torch.cuda.memory_allocated() / 1024**3:.2f} GB",
    )

    print(
        "Reserved:",
        f"{torch.cuda.memory_reserved() / 1024**3:.2f} GB",
    )
