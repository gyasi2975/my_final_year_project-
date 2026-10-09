"""Dataset for extremity X-ray vs unrelated image binary classification."""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

_ML_ROOT = Path(__file__).resolve().parent.parent
if str(_ML_ROOT) not in sys.path:
    sys.path.insert(0, str(_ML_ROOT))

import config

DATA_DIR = Path(__file__).resolve().parent
RAW_DIR = DATA_DIR / "raw"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}

# User folder may be "unrelated" or "unrelated img"
UNRELATED_DIRS = [DATA_DIR / "unrelated", DATA_DIR / "unrelated img"]


def unrelated_dir() -> Path | None:
    for d in UNRELATED_DIRS:
        if d.exists():
            return d
    return None


def _list_images(root: Path) -> list[str]:
    if not root.exists():
        return []
    return sorted(
        str(p)
        for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    )


def _list_extremity_images(split: str) -> list[str]:
    return _list_images(RAW_DIR / split)


def build_validity_index(
    related_per_split: int | None = None,
    seed: int = 42,
) -> dict[str, tuple[list[str], np.ndarray]]:
    """
    Returns split -> (paths, labels). Label 1 = related extremity X-ray, 0 = unrelated.
    """
    rng = random.Random(seed)
    unrelated_root = unrelated_dir()
    if unrelated_root is None:
        raise FileNotFoundError(
            "No unrelated folder found. Expected ml/data/unrelated or ml/data/unrelated img"
        )

    unrelated_paths = _list_images(unrelated_root)
    if not unrelated_paths:
        raise FileNotFoundError(f"No images in {unrelated_root}")

    rng.shuffle(unrelated_paths)
    n = len(unrelated_paths)
    n_train = max(1, int(n * config.TRAIN_RATIO))
    n_val = max(1, int(n * config.VAL_RATIO))
    n_test = max(1, n - n_train - n_val)
    if n_train + n_val + n_test > n:
        n_test = n - n_train - n_val

    splits_unrelated = {
        "train": unrelated_paths[:n_train],
        "valid": unrelated_paths[n_train : n_train + n_val],
        "test": unrelated_paths[n_train + n_val : n_train + n_val + n_test],
    }

    related_splits = {}
    for split in ("train", "valid", "test"):
        paths = _list_extremity_images(split)
        if not paths:
            continue
        rng.shuffle(paths)
        cap = related_per_split
        if cap is None:
            cap = max(len(splits_unrelated.get(split, [])), 1) * 8
        related_splits[split] = paths[: min(cap, len(paths))]

    out: dict[str, tuple[list[str], np.ndarray]] = {}
    for split in ("train", "valid", "test"):
        neg = splits_unrelated.get(split, [])
        pos = related_splits.get(split, [])
        if not neg and not pos:
            continue
        paths = neg + pos
        labels = np.array([0] * len(neg) + [1] * len(pos), dtype=np.int32)
        combined = list(zip(paths, labels.tolist()))
        rng.shuffle(combined)
        paths, labels = zip(*combined) if combined else ([], [])
        out[split] = (list(paths), np.array(labels, dtype=np.int32))
    return out


def _augment(arr: np.ndarray) -> np.ndarray:
    import random

    if random.random() < 0.5:
        arr = arr[:, ::-1, :].copy()
    if random.random() < 0.5:
        factor = random.uniform(0.85, 1.15)
        arr = np.clip(arr * factor, 0.0, 1.0)
    if random.random() < 0.3:
        delta = random.uniform(-0.08, 0.08)
        arr = np.clip(arr + delta, 0.0, 1.0)
    return arr


def _load_image(path: str) -> np.ndarray:
    from PIL import Image

    try:
        with open(path, "rb") as f:
            img = Image.open(f).convert("RGB")
        img = img.resize((config.IMG_SIZE, config.IMG_SIZE))
        return np.array(img, dtype=np.float32) * config.NORMALIZE_SCALE
    except Exception:
        return np.zeros((config.IMG_SIZE, config.IMG_SIZE, 3), dtype=np.float32)


def get_validity_dataset(
    split: str,
    batch_size: int = config.BATCH_SIZE,
    augment: bool | None = None,
    repeat: bool = True,
    shuffle: bool | None = None,
    related_per_split: int | None = None,
    unrelated_oversample: int = 1,
):
    import tensorflow as tf

    indexed = build_validity_index(related_per_split=related_per_split)
    if split not in indexed:
        return None
    paths, labels = indexed[split]
    if augment is None:
        augment = split == "train"
    if shuffle is None:
        shuffle = split == "train"

    if split == "train" and unrelated_oversample > 1:
        expanded_paths: list[str] = []
        expanded_labels: list[int] = []
        for path, label in zip(paths, labels):
            repeats = unrelated_oversample if label == 0 else 1
            expanded_paths.extend([path] * repeats)
            expanded_labels.extend([label] * repeats)
        paths = expanded_paths
        labels = np.array(expanded_labels, dtype=np.int32)

    def gen():
        for path, label in zip(paths, labels):
            x = _load_image(path)
            if augment:
                x = _augment(x)
            yield x, int(label)

    ds = tf.data.Dataset.from_generator(
        gen,
        output_signature=(
            tf.TensorSpec(shape=(config.IMG_SIZE, config.IMG_SIZE, 3), dtype=tf.float32),
            tf.TensorSpec(shape=(), dtype=tf.int32),
        ),
    )
    if shuffle:
        buf = min(500, len(paths))
        ds = ds.shuffle(buf, seed=42, reshuffle_each_iteration=True)
    ds = ds.batch(batch_size)
    if repeat:
        ds = ds.repeat()
    ds = ds.prefetch(tf.data.AUTOTUNE)
    return ds, len(paths)
