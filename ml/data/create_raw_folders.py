"""Create data/raw folder structure. Run from ml/:  python data/create_raw_folders.py"""
from pathlib import Path

RAW = Path(__file__).resolve().parent / "raw"
splits = ["train", "valid", "test"]
bodies = ["elbow", "finger", "forearm", "hand", "humerus", "shoulder", "wrist"]
types = ["normal", "fracture_simple", "fracture_comminuted", "fracture_greenstick"]

for split in splits:
    for body in bodies:
        for t in types:
            (RAW / split / body / t).mkdir(parents=True, exist_ok=True)
print("Created:", RAW)
print("Folders: train/valid/test, each with", len(bodies), "body parts x 4 labels")
