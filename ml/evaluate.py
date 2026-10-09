"""
Evaluation per proposal: accuracy, precision, recall, F1-score.
"""

import sys
from pathlib import Path

_ML_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ML_ROOT))

import numpy as np
import tensorflow as tf
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import config
from data.dataset import index_multitask_split, count_split_images, RAW_DIR


def evaluate_metrics(y_true: np.ndarray, y_pred: np.ndarray, task: str = "binary"):
    """Compute accuracy, precision, recall, F1 per proposal."""
    if task == "binary":
        y_pred = (y_pred > 0.5).astype(int).flatten()
    else:
        y_pred = np.argmax(y_pred, axis=-1) if y_pred.ndim > 1 else y_pred
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average="weighted", zero_division=0)
    rec = recall_score(y_true, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    return {
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1": round(float(f1), 4),
    }


def _load_batch_images(paths, start, end):
    from PIL import Image

    batch = []
    for path in paths[start:end]:
        try:
            with open(path, "rb") as f:
                img = Image.open(f).convert("RGB")
            img = img.resize((config.IMG_SIZE, config.IMG_SIZE))
            arr = np.array(img, dtype=np.float32) * config.NORMALIZE_SCALE
            batch.append(arr)
        except Exception:
            batch.append(np.zeros((config.IMG_SIZE, config.IMG_SIZE, 3), dtype=np.float32))
    return np.stack(batch, axis=0)


def run_evaluation(model_path: str = "checkpoints/bone_fracture_model.keras"):
    """Run evaluation on test set and print metrics."""
    model_path = Path(model_path)
    if not model_path.is_absolute():
        model_path = _ML_ROOT / model_path

    model = tf.keras.models.load_model(str(model_path))
    indexed = index_multitask_split("test")
    if indexed is None:
        print("No test set found. Add data under data/raw/test/")
        return

    image_paths, body_labels, fracture_labels, type_labels, type_labeled = indexed
    n = len(image_paths)
    batch_size = config.BATCH_SIZE

    body_pred, fracture_pred, type_pred = [], [], []

    for start in range(0, n, batch_size):
        end = min(start + batch_size, n)
        x = _load_batch_images(image_paths, start, end)
        out = model(x, training=False)
        body_pred.append(np.argmax(out["body_part"].numpy(), axis=-1))
        fracture_pred.append(out["fracture"].numpy().flatten())
        type_pred.append(np.argmax(out["fracture_type"].numpy(), axis=-1))

    body_pred = np.concatenate(body_pred)
    fracture_pred = np.concatenate(fracture_pred)
    type_pred = np.concatenate(type_pred)

    print(f"Test images: {n}")
    print("=== Body part identification ===")
    body_metrics = evaluate_metrics(body_labels, body_pred, "multiclass")
    print(body_metrics)
    print(f"  Accuracy: {body_metrics['accuracy'] * 100:.2f}%")
    print("  Per-class accuracy:")
    for i, name in enumerate(config.BODY_PARTS):
        mask = body_labels == i
        if mask.sum() == 0:
            continue
        acc = (body_pred[mask] == i).mean()
        print(f"    {name:10} {acc * 100:5.1f}%  ({mask.sum()} images)")

    print("=== Fracture detection ===")
    frac_metrics = evaluate_metrics(fracture_labels, fracture_pred, "binary")
    print(frac_metrics)
    print(f"  Accuracy: {frac_metrics['accuracy'] * 100:.2f}%")

    labeled_mask = type_labeled.astype(bool)
    n_labeled = int(labeled_mask.sum())
    print(f"=== Fracture type classification (labeled samples only: {n_labeled}) ===")
    if n_labeled > 0:
        type_metrics = evaluate_metrics(type_labels[labeled_mask], type_pred[labeled_mask], "multiclass")
        print(type_metrics)
        print(f"  Accuracy: {type_metrics['accuracy'] * 100:.2f}%")
    else:
        print("No fracture-type labels in test set.")

    return {
        "body_part": body_metrics,
        "fracture": frac_metrics,
    }


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--model", default="checkpoints/bone_fracture_model.keras")
    args = p.parse_args()
    run_evaluation(args.model)
