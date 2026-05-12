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
from data.dataset import get_multitask_dataset


def evaluate_metrics(y_true: np.ndarray, y_pred: np.ndarray, task: str = "binary"):
    """Compute accuracy, precision, recall, F1 per proposal."""
    if task == "binary":
        y_pred = (y_pred > 0.5).astype(int).flatten()
    else:
        y_pred = np.argmax(y_pred, axis=-1)
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average="weighted", zero_division=0)
    rec = recall_score(y_true, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    return {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1}


def run_evaluation(model_path: str = "checkpoints/bone_fracture_model.keras"):
    """Run evaluation on test set and print metrics."""
    model = tf.keras.models.load_model(model_path)
    test_ds = get_multitask_dataset("test", batch_size=config.BATCH_SIZE)
    if test_ds is None:
        print("No test set found. Add data under data/raw/test/")
        return

    body_true, fracture_true, type_true = [], [], []
    body_pred, fracture_pred, type_pred = [], [], []

    for batch in test_ds:
        x, y = batch
        body_true.append(y["body_part"].numpy())
        fracture_true.append(y["fracture"].numpy())
        type_true.append(y["fracture_type"].numpy())
        out = model(x)
        body_pred.append(np.argmax(out["body_part"].numpy(), axis=-1))
        fracture_pred.append(out["fracture"].numpy())
        type_pred.append(np.argmax(out["fracture_type"].numpy(), axis=-1))

    body_true = np.concatenate(body_true)
    fracture_true = np.concatenate(fracture_true)
    type_true = np.concatenate(type_true)
    body_pred = np.concatenate(body_pred)
    fracture_pred = np.concatenate(fracture_pred).flatten()
    type_pred = np.concatenate(type_pred)

    print("=== Body part identification ===")
    print(evaluate_metrics(body_true, body_pred, "multiclass"))
    print("=== Fracture detection ===")
    print(evaluate_metrics(fracture_true, fracture_pred, "binary"))
    print("=== Fracture type classification ===")
    print(evaluate_metrics(type_true, type_pred, "multiclass"))


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="checkpoints/bone_fracture_model.keras")
    args = p.parse_args()
    run_evaluation(args.model)
