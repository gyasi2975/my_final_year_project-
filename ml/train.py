"""
Training script per proposal:
- Data collection & preprocessing (MURA & FracAtlas-style)
- Hybrid MobileNetV2, 80/10/10 split
- Evaluation: accuracy, precision, recall, F1-score
"""

import json
import sys
import argparse
from pathlib import Path

_ML_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ML_ROOT))

import config
from tensorflow import keras
from data.dataset import get_multitask_dataset, count_split_images, RAW_DIR
from models.hybrid_model import build_hybrid_mobilenetv2


def main():
    parser = argparse.ArgumentParser(description="Train bone fracture detection model")
    parser.add_argument("--epochs", type=int, default=config.EPOCHS)
    parser.add_argument("--batch-size", type=int, default=config.BATCH_SIZE)
    parser.add_argument("--save", type=str, default="checkpoints/bone_fracture_model.keras")
    parser.add_argument("--history", type=str, default="checkpoints/training_history.json")
    parser.add_argument(
        "--monitor",
        type=str,
        default="val_fracture_accuracy",
        choices=[
            "val_fracture_accuracy",
            "val_body_part_accuracy",
            "fracture_accuracy",
            "body_part_accuracy",
        ],
        help="Metric for checkpointing and early stopping",
    )
    parser.add_argument(
        "--balance-body-parts",
        action="store_true",
        help="Use class-balanced sample weights for body-part head",
    )
    args = parser.parse_args()

    save_path = Path(args.save)
    if not save_path.is_absolute():
        save_path = _ML_ROOT / save_path
    args.save = str(save_path)

    history_path = Path(args.history)
    if not history_path.is_absolute():
        history_path = _ML_ROOT / history_path

    save_path.parent.mkdir(parents=True, exist_ok=True)

    n_train = count_split_images("train")
    if n_train == 0:
        print(
            "No training data found. Please add data under:\n"
            f"  {RAW_DIR / 'train'}\n"
            "Structure: train/{body_part}/normal/ or train/{body_part}/fracture_{type}/"
        )
        return None

    train_ds = get_multitask_dataset(
        "train",
        batch_size=args.batch_size,
        include_sample_weights=True,
        augment=True,
        balance_body_parts=args.balance_body_parts,
    )
    val_ds = get_multitask_dataset("valid", batch_size=args.batch_size, repeat=False, shuffle=False)
    if val_ds is None:
        val_ds = get_multitask_dataset("validation", batch_size=args.batch_size, repeat=False, shuffle=False)

    model = build_hybrid_mobilenetv2()
    model.summary()

    steps_per_epoch = max(1, n_train // args.batch_size)
    val_steps = None
    n_valid = count_split_images("valid")
    if val_ds and n_valid > 0:
        val_steps = max(1, n_valid // args.batch_size)

    monitor = args.monitor
    if val_ds is None and monitor.startswith("val_"):
        monitor = monitor.replace("val_", "")
        print(f"No validation set — monitoring {monitor} instead.")

    callbacks = [
        keras.callbacks.ModelCheckpoint(
            args.save,
            save_best_only=True,
            monitor=monitor,
            mode="max",
            verbose=1,
        ),
        keras.callbacks.EarlyStopping(
            patience=7,
            restore_best_weights=True,
            monitor=monitor,
            mode="max",
            verbose=1,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor=monitor,
            mode="max",
            factor=0.5,
            patience=3,
            min_lr=1e-6,
            verbose=1,
        ),
    ]

    print(f"Training images: {n_train} | Validation images: {n_valid}")
    print(f"Steps/epoch: {steps_per_epoch} | Val steps: {val_steps} | Monitor: {monitor}")

    if val_ds:
        history = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=args.epochs,
            steps_per_epoch=steps_per_epoch,
            validation_steps=val_steps,
            callbacks=callbacks,
        )
    else:
        print("Warning: no validation set — training without validation.")
        history = model.fit(
            train_ds,
            epochs=args.epochs,
            steps_per_epoch=steps_per_epoch,
            callbacks=callbacks,
        )

    model.save(args.save)
    history_path.write_text(json.dumps(history.history, indent=2), encoding="utf-8")
    print("Training done. Model saved to", args.save)
    print("History saved to", history_path)
    return model


if __name__ == "__main__":
    main()
