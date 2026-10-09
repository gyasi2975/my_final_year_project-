"""Evaluate validity classifier on held-out test split."""

import sys
from pathlib import Path

_ML_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ML_ROOT))

import numpy as np
import tensorflow as tf
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from data.validity_dataset import build_validity_index, _load_image


def run_evaluation(model_path: str = "checkpoints/xray_validity_model.keras", related_per_split: int = 400):
    model_path = Path(model_path)
    if not model_path.is_absolute():
        model_path = _ML_ROOT / model_path

    model = tf.keras.models.load_model(str(model_path))
    index = build_validity_index(related_per_split=related_per_split)
    paths, labels = index.get("test", ([], np.array([])))
    if not paths:
        print("No test split")
        return

    preds, probs = [], []
    batch_size = 32
    for start in range(0, len(paths), batch_size):
        batch_paths = paths[start : start + batch_size]
        x = np.stack([_load_image(p) for p in batch_paths], axis=0)
        p = model(x, training=False).numpy().flatten()
        probs.extend(p.tolist())
        preds.extend((p >= 0.5).astype(int).tolist())

    y_true = labels
    y_pred = np.array(preds)
    print(f"Test images: {len(paths)}")
    print(f"  Accuracy:  {accuracy_score(y_true, y_pred):.4f}")
    print(f"  Precision: {precision_score(y_true, y_pred, zero_division=0):.4f}")
    print(f"  Recall:    {recall_score(y_true, y_pred, zero_division=0):.4f}")
    print(f"  F1:        {f1_score(y_true, y_pred, zero_division=0):.4f}")

    unrelated_mask = y_true == 0
    if unrelated_mask.any():
        unr_acc = (y_pred[unrelated_mask] == 0).mean()
        print(f"  Unrelated detected correctly: {unr_acc * 100:.1f}% ({unrelated_mask.sum()} images)")


if __name__ == "__main__":
    run_evaluation()
