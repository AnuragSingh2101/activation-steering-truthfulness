"""
Environment Check Diagnostic Script

Verifies the installed libraries, PyTorch setup, CUDA device status,
and model cache accessibility.
"""

import sys
import os
import torch
import transformers
import transformer_lens


def main():
    print("=" * 60)
    print("ENVIRONMENT CHECK DIAGNOSTIC")
    print("=" * 60)

    # 1. Python & OS info
    print(f"Python Version:   {sys.version}")
    print(f"Operating System: {sys.platform}")

    # 2. Package Versions
    print(f"PyTorch Version:  {torch.__version__}")
    print(f"Transformers:     {transformers.__version__}")
    print(f"TransformerLens:  {transformer_lens.__version__}")

    # 3. CUDA & GPU Devices
    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available:   {cuda_available}")

    if cuda_available:
        device_count = torch.cuda.device_count()
        print(f"CUDA Devices:     {device_count}")
        for i in range(device_count):
            name = torch.cuda.get_device_name(i)
            capability = torch.cuda.get_device_capability(i)
            print(f"  Device [{i}]: {name} (Compute Capability {capability})")
        print(f"Current Device:   {torch.cuda.current_device()}")
    else:
        print("Running on CPU only.")

    # 4. Cache directory check
    hf_home = os.getenv("HF_HOME", ".cache/huggingface")
    print(f"HF Cache Path:    {hf_home}")
    
    # Try to verify write access
    try:
        os.makedirs(hf_home, exist_ok=True)
        test_file = os.path.join(hf_home, ".env_check_temp")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        print("HF Cache Write:   OK")
    except Exception as e:
        print(f"HF Cache Write:   FAILED (Error: {e})")

    print("=" * 60)
    print("Diagnostic complete.")


if __name__ == "__main__":
    main()
