import torch

from src.model import load_model


model = load_model()

prompt = "What is the capital of France?"

print("\n" + "=" * 60)
print("PROMPT")
print("=" * 60)

print(prompt)

print("\n" + "=" * 60)
print("GENERATING")
print("=" * 60)

with torch.no_grad():

    output = model.generate(
        prompt,
        max_new_tokens=30,
        do_sample=False,
    )

print("\n" + "=" * 60)
print("OUTPUT")
print("=" * 60)

print(output)

if torch.cuda.is_available():

    print("\n" + "=" * 60)
    print("GPU MEMORY")
    print("=" * 60)

    allocated = (
        torch.cuda.memory_allocated()
        / 1024**3
    )

    reserved = (
        torch.cuda.memory_reserved()
        / 1024**3
    )

    print(f"Allocated: {allocated:.2f} GB")
    print(f"Reserved:  {reserved:.2f} GB")