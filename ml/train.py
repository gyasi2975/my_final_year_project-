"""
Training script per proposal:
- Data collection & preprocessing (MURA & FracAtlas-style)
- Hybrid MobileNetV2, 80/10/10 split
- Evaluation: accuracy, precision, recall, F1-score
"""

import sys
import argparse
from pathlib import Path

_ML_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ML_ROOT))

import config
from tensorflow import keras
from data.dataset import get_multitask_dataset, RAW_DIR
from models.hybrid_model import build_hybrid_mobilenetv2


def main():
    parser = argparse.ArgumentParser(description="Train bone fracture detection model")
    parser.add_argument("--epochs", type=int, default=config.EPOCHS)
    parser.add_argument("--batch-size", type=int, default=config.BATCH_SIZE)
    parser.add_argument("--save", type=str, default="checkpoints/bone_fracture_model.keras")
    args = parser.parse_args()
    save_path = Path(args.save)
    if not save_path.is_absolute():
        save_path = _ML_ROOT / save_path
    args.save = str(save_path)

    train_ds = get_multitask_dataset("train", batch_size=args.batch_size)
    if train_ds is None:
        print(
            "No training data found. Please add data under:\n"
            f"  {RAW_DIR / 'train'}\n"
            "Structure: train/{body_part}/normal/ or train/{body_part}/fracture_{type}/"
        )
        # Create minimal dummy data for structure demo / CI
        import tensorflow as tf
        import numpy as np
        n = 64
        train_ds = tf.data.Dataset.from_tensor_slices((
            np.random.rand(n, config.IMG_SIZE, config.IMG_SIZE, 3).astype(np.float32) * 0.5,
            {
                "body_part": np.random.randint(0, len(config.BODY_PARTS), size=n),
                "fracture": np.random.randint(0, 2, size=n).astype(np.float32),
                "fracture_type": np.random.randint(0, len(config.FRACTURE_TYPES), size=n),
            },
        )).batch(args.batch_size).prefetch(1)
        val_ds = None
    else:
        val_ds = get_multitask_dataset("valid", batch_size=args.batch_size)
        if val_ds is None:
            val_ds = get_multitask_dataset("validation", batch_size=args.batch_size)

    model = build_hybrid_mobilenetv2()
    model.summary()

    # With repeat(), set steps per epoch so training doesn't run forever
    train_dir = RAW_DIR / "train"
    n_train = sum(1 for _ in train_dir.rglob("*.*") if _.suffix.lower() in (".png", ".jpg", ".jpeg", ".bmp")) if train_dir.exists() else 3271
    steps_per_epoch = max(1, n_train // args.batch_size)
    val_steps = None
    if val_ds:
        valid_dir = RAW_DIR / "valid"
        n_valid = sum(1 for _ in valid_dir.rglob("*.*") if _.suffix.lower() in (".png", ".jpg", ".jpeg", ".bmp")) if valid_dir.exists() else 411
        val_steps = max(1, n_valid // args.batch_size)

    monitor = "val_fracture_accuracy" if val_ds else "fracture_accuracy"
    callbacks = [
        keras.callbacks.ModelCheckpoint(
            args.save,
            save_best_only=True,
            monitor=monitor,
            mode="max",
        ),
        keras.callbacks.EarlyStopping(
            patience=5,
            restore_best_weights=True,
            monitor=monitor,
            mode="max",
        ),
    ]
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
        history = model.fit(
            train_ds,
            epochs=min(2, args.epochs),
            steps_per_epoch=steps_per_epoch,
            callbacks=callbacks,
        )
    # Always save final weights (checkpoint may only have saved "best" so far)
    model.save(args.save)
    print("Training done. Model saved to", args.save)
    return model


if __name__ == "__main__":
    main()
