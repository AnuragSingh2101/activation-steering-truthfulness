import torch
import torch.nn.functional as F


PATH = "artifacts/vectors/truthfulness_vector.pt"


data = torch.load(
    PATH,
    map_location="cpu",
)


vector = data["truthfulness_vector"]
directions = data["directions"]


print("=" * 60)
print("TRUTHFULNESS VECTOR CHECK")
print("=" * 60)

print("Number of directions:", directions.shape[0])
print("Vector shape:", vector.shape)
print("Directions shape:", directions.shape)
print("Vector norm:", vector.norm().item())


normalized_directions = F.normalize(
    directions,
    dim=1,
)

normalized_vector = F.normalize(
    vector,
    dim=0,
)


cosines = (
    normalized_directions @ normalized_vector
)


print("\n" + "=" * 60)
print("DIRECTION <-> VECTOR COSINE")
print("=" * 60)

print("Average cosine:", cosines.mean().item())
print("Minimum cosine:", cosines.min().item())
print("Maximum cosine:", cosines.max().item())
print("Std cosine:", cosines.std().item())


pairwise = (
    normalized_directions
    @ normalized_directions.T
)


n = pairwise.shape[0]

mask = ~torch.eye(
    n,
    dtype=torch.bool,
)

pairwise_values = pairwise[mask]


print("\n" + "=" * 60)
print("PAIRWISE DIRECTION COSINE")
print("=" * 60)

print(
    "Average pairwise cosine:",
    pairwise_values.mean().item(),
)

print(
    "Minimum pairwise cosine:",
    pairwise_values.min().item(),
)

print(
    "Maximum pairwise cosine:",
    pairwise_values.max().item(),
)

print(
    "Std pairwise cosine:",
    pairwise_values.std().item(),
)


print("\n" + "=" * 60)
print("VECTOR CHECK COMPLETE")
print("=" * 60)
