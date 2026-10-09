"""
Fine-tune an existing checkpoint to improve body-part classification.

Loads the saved model, recompiles with higher body-part loss weight, freezes
fracture/type heads, and trains with class-balanced sampling.
"""

import argparse
import json
import sys
from pathlib import Path

_ML_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ML_ROOT))

import config
from tensorflow import keras
from data.dataset import get_multitask_dataset, count_split_images, RAW_DIR


def _freeze_non_body_layers(model: keras.Model) -> None:
    """Train backbone tail + body-part head; keep fracture heads stable."""
    for layer in model.layers:
        layer.trainable = False

    for layer in model.layers:
        name = layer.name
        if name in ("body_part", "body_part_dense"):
            layer.trainable = True
        if name.startswith("mobilenet"):
            for sub in layer.layers[-50:]:
                sub.trainable = True


def main():
    parser = argparse.ArgumentParser(description="Fine-tune body-part classification")
    parser.add_argument(
        "--model",
        type=str,
        default="checkpoints/bone_fracture_model.keras",
        help="Starting checkpoint",
    )
    parser.add_argument(
        "--save",
        type=str,
        default="checkpoints/bone_fracture_model.keras",
        help="Output checkpoint (overwrites by default)",
    )
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=config.BATCH_SIZE)
    parser.add_argument("--lr", type=float, default=5e-5)
    parser.add_argument(
        "--history",
        type=str,
        default="checkpoints/body_part_finetune_history.json",
    )
    args = parser.parse_args()

    model_path = Path(args.model)
    if not model_path.is_absolute():
        model_path = _ML_ROOT / model_path
    save_path = Path(args.save)
    if not save_path.is_absolute():
        save_path = _ML_ROOT / save_path
    history_path = Path(args.history)
    if not history_path.is_absolute():
        history_path = _ML_ROOT / history_path

    if not model_path.exists():
        print(f"Model not found: {model_path}")
        return None

    n_train = count_split_images("train")
    if n_train == 0:
        print(f"No training data under {RAW_DIR / 'train'}")
        return None

    print(f"Loading {model_path}")
    model = keras.models.load_model(str(model_path))

    loss_weights = {
        "body_part": 4.0,
        "fracture": 0.5,
        "fracture_type": 0.25,
    }
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=args.lr),
        loss={
            "body_part": "sparse_categorical_crossentropy",
            "fracture": "binary_crossentropy",
            "fracture_type": "sparse_categorical_crossentropy",
        },
        loss_weights=loss_weights,
        metrics={
            "body_part": ["accuracy"],
            "fracture": ["accuracy"],
            "fracture_type": ["accuracy"],
        },
    )

    _freeze_non_body_layers(model)
    trainable = sum(int(w.shape.num_elements()) for w in model.trainable_weights)
    print(f"Trainable parameters: {trainable:,}")
    print(f"Loss weights: {loss_weights}")

    train_ds = get_multitask_dataset(
        "train",
        batch_size=args.batch_size,
        include_sample_weights=True,
        augment=True,
        balance_body_parts=True,
    )
    val_ds = get_multitask_dataset("valid", batch_size=args.batch_size, repeat=False, shuffle=False)

    steps_per_epoch = max(1, n_train // args.batch_size)
    n_valid = count_split_images("valid")
    val_steps = max(1, n_valid // args.batch_size) if val_ds and n_valid > 0 else None

    monitor = "val_body_part_accuracy" if val_ds else "body_part_accuracy"
    callbacks = [
        keras.callbacks.ModelCheckpoint(
            str(save_path),
            save_best_only=True,
            monitor=monitor,
            mode="max",
            verbose=1,
        ),
        keras.callbacks.EarlyStopping(
            patience=4,
            restore_best_weights=True,
            monitor=monitor,
            mode="max",
            verbose=1,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor=monitor,
            mode="max",
            factor=0.5,
            patience=2,
            min_lr=1e-6,
            verbose=1,
        ),
    ]

    save_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Fine-tuning for body part | monitor={monitor} | epochs={args.epochs}")

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
            epochs=args.epochs,
            steps_per_epoch=steps_per_epoch,
            callbacks=callbacks,
        )

    model.save(str(save_path))
    history_path.write_text(json.dumps(history.history, indent=2), encoding="utf-8")
    print("Fine-tune done. Model saved to", save_path)
    return model


if __name__ == "__main__":
    main()
