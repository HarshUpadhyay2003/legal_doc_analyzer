import torch
import subprocess
import sys

print("=== GPU Availability Check ===")

# Check nvidia-smi
try:
    result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ NVIDIA drivers installed")
    else:
        print("✗ NVIDIA drivers not found")
except FileNotFoundError:
    print("✗ nvidia-smi not found")

# Check PyTorch
print(f"\nPyTorch CUDA Support:")
print(f"  Available: {torch.cuda.is_available()}")
print(f"  Version: {torch.version.cuda}")
print(f"  Device Count: {torch.cuda.device_count()}")

if torch.cuda.is_available():
    print(f"  GPU Name: {torch.cuda.get_device_name(0)}")
    print(f"  Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
else:
    print("  No GPU available for PyTorch")