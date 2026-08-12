import json

from src.prompts import build_prompt


with open(
    "data/contrastive_examples.json",
    "r",
    encoding="utf-8",
) as f:
    examples = json.load(f)


print("=" * 60)
print("DATASET CHECK")
print("=" * 60)

print("Total examples:", len(examples))


example = examples[0]

print("\nQUESTION:")
print(example["question"])

print("\nTRUTHFUL PROMPT:")
print(
    build_prompt(
        example["question"],
        example["truthful"],
    )
)

print("\nFALSE PROMPT:")
print(
    build_prompt(
        example["question"],
        example["false"],
    )
)
