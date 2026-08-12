import os

import torch
from dotenv import load_dotenv
from transformer_lens import HookedTransformer


load_dotenv()


MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "Qwen/Qwen2.5-0.5B-Instruct",
)


def get_device():
    return (
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )


def load_model():

    device = get_device()

    print("=" * 60)
    print("LOADING MODEL")
    print("=" * 60)

    print("Model:", MODEL_NAME)
    print("Device:", device)

    model = HookedTransformer.from_pretrained(
        MODEL_NAME,
        device=device,
    )

    model.eval()

    print("\nModel loaded!")

    print(
        "Number of layers:",
        model.cfg.n_layers,
    )

    print(
        "Model dimension:",
        model.cfg.d_model,
    )

    print(
        "Device:",
        model.cfg.device,
    )

    return model