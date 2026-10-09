"""Train binary classifier: extremity X-ray (related) vs unrelated images."""

import argparse
import json
import sys
from pathlib import Path

_ML_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ML_ROOT))

import config
from tensorflow import keras
from data.validity_dataset import build_validity_index, get_validity_dataset, unrelated_dir
from models.validity_model import build_validity_mobilenetv2


def main():
    parser = argparse.ArgumentParser(description="Train X-ray validity / unrelated detector")
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--related-per-split", type=int, default=150)
    parser.add_argument("--unrelated-oversample", type=int, default=5)
    parser.add_argument("--save", type=str, default="checkpoints/xray_validity_model.keras")
    parser.add_argument("--history", type=str, default="checkpoints/xray_validity_history.json")
    args = parser.parse_args()

    if unrelated_dir() is None:
        print("Missing ml/data/unrelated or ml/data/unrelated img")
        return None

    save_path = Path(args.save)
    if not save_path.is_absolute():
        save_path = _ML_ROOT / save_path
    history_path = Path(args.history)
    if not history_path.is_absolute():
        history_path = _ML_ROOT / history_path
    save_path.parent.mkdir(parents=True, exist_ok=True)

    index = build_validity_index(related_per_split=args.related_per_split)
    for split, (paths, labels) in index.items():
        n_rel = int(labels.sum())
        n_unrel = len(labels) - n_rel
        print(f"{split}: {len(paths)} images (related={n_rel}, unrelated={n_unrel})")

    train_ds, n_train = get_validity_dataset(
        "train",
        batch_size=args.batch_size,
        related_per_split=args.related_per_split,
        unrelated_oversample=args.unrelated_oversample,
    )
    val_ds, n_valid = get_validity_dataset(
        "valid",
        batch_size=args.batch_size,
        repeat=False,
        shuffle=False,
        related_per_split=args.related_per_split,
    )

    model = build_validity_mobilenetv2()
    model.summary()

    steps = max(1, n_train // args.batch_size)
    val_steps = max(1, n_valid // args.batch_size) if n_valid else None

    callbacks = [
        keras.callbacks.ModelCheckpoint(
            str(save_path),
            save_best_only=True,
            monitor="val_auc",
            mode="max",
            verbose=1,
        ),
        keras.callbacks.EarlyStopping(
            patience=5,
            restore_best_weights=True,
            monitor="val_auc",
            mode="max",
            verbose=1,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_auc",
            mode="max",
            factor=0.5,
            patience=2,
            min_lr=1e-6,
            verbose=1,
        ),
    ]

    print(f"Training validity model | steps/epoch={steps} | val_steps={val_steps}")
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.epochs,
        steps_per_epoch=steps,
        validation_steps=val_steps,
        callbacks=callbacks,
        class_weight={0: 4.0, 1: 1.0},
    )

    model.save(str(save_path))
    history_path.write_text(json.dumps(history.history, indent=2), encoding="utf-8")
    print("Saved", save_path)
    return model


if __name__ == "__main__":
    main()
