import torch
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
path = PROJECT_ROOT / "artifacts" / "checkpoint_mobilenetv3_large_100.pth"
ckpt = torch.load(path, map_location="cpu", weights_only=False)

print("Model name:", ckpt["model_name"])

state = ckpt["model_state_dict"]
keys = list(state.keys())
print("Num layers:", len(keys))
print("First 3:", keys[:3])
print("Last 3:", keys[-3:])
print("Classifier shape:", state[keys[-1]].shape)

hist = ckpt["history"]
print("History type:", type(hist))
if isinstance(hist, dict):
    print("History keys:", list(hist.keys()))