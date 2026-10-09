"""
Data loading and preprocessing per proposal:
- Data from MURA (body parts, abnormality) and FracAtlas-style (fracture types)
- Resize 224x224, normalize 0-1, standardize labels
"""

import os
import sys
import numpy as np
from pathlib import Path

# Allow running from repo root or ml/
_ML_ROOT = Path(__file__).resolve().parent.parent
if str(_ML_ROOT) not in sys.path:
    sys.path.insert(0, str(_ML_ROOT))

from tensorflow.keras.utils import image_dataset_from_directory
import config

# Default paths (create and use raw/ for MURA/FracAtlas data)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


def _ensure_dirs():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / "train").mkdir(exist_ok=True)
    (RAW_DIR / "valid").mkdir(exist_ok=True)
    (RAW_DIR / "test").mkdir(exist_ok=True)


def load_image(path: str, size: int = config.IMG_SIZE) -> np.ndarray:
    """Load single image, resize to size x size, normalize [0, 1]."""
    from PIL import Image
    img = Image.open(path).convert("RGB")
    img = img.resize((size, size))
    arr = np.array(img, dtype=np.float32) * config.NORMALIZE_SCALE
    return arr


def get_dataset_from_folders(
    split: str,
    batch_size: int = config.BATCH_SIZE,
    image_size: int = config.IMG_SIZE,
    label_mode: str = "categorical",
    seed: int = 42,
):
    """
    Load dataset from folder structure:
      raw/{split}/{body_part}/{fracture_type}/  or
      raw/{split}/{class_name}/
    Returns tf.data.Dataset.
    """
    from tensorflow import keras
    split_dir = RAW_DIR / split
    if not split_dir.exists():
        _ensure_dirs()
        return None
    ds = image_dataset_from_directory(
        str(split_dir),
        labels="inferred",
        label_mode=label_mode,
        image_size=(image_size, image_size),
        batch_size=batch_size,
        shuffle=(split == "train"),
        seed=seed,
    )
    # Normalize to [0,1] per proposal
    normalize = keras.layers.Rescaling(scale=config.NORMALIZE_SCALE)
    ds = ds.map(lambda x, y: (normalize(x), y))
    return ds


def count_split_images(split: str) -> int:
    """Number of image files in raw/{split}/."""
    split_dir = RAW_DIR / split
    if not split_dir.exists():
        return 0
    return sum(
        1
        for f in split_dir.rglob("*.*")
        if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".bmp")
    )


def index_multitask_split(split: str):
    """
    Build deterministic label index for a split.
    Returns (image_paths, body_labels, fracture_labels, fracture_type_labels, type_labeled).
    """
    split_dir = RAW_DIR / split
    if not split_dir.exists():
        return None

    image_paths = []
    body_labels = []
    fracture_labels = []
    fracture_type_labels = []
    type_labeled = []

    body_to_idx = {b: i for i, b in enumerate(config.BODY_PARTS)}
    type_to_idx = {t: i for i, t in enumerate(config.FRACTURE_TYPES)}

    for body_part in sorted(split_dir.iterdir()):
        if not body_part.is_dir():
            continue
        body_idx = body_to_idx.get(body_part.name.lower(), -1)
        if body_idx < 0:
            continue
        for label_dir in sorted(body_part.iterdir()):
            if not label_dir.is_dir():
                continue
            name = label_dir.name.lower()
            if name == "fracture_unlabeled":
                has_fracture = True
                fracture_type_idx = 0
                labeled_type = False
            else:
                has_fracture = name.startswith("fracture_") or (
                    name != "normal" and "fracture" in name
                )
                labeled_type = False
                fracture_type_idx = 0
                if has_fracture:
                    for ft in config.FRACTURE_TYPES:
                        if ft in name:
                            fracture_type_idx = type_to_idx[ft]
                            labeled_type = True
                            break
            fracture_idx = 1 if has_fracture else 0

            for f in sorted(label_dir.glob("*.*")):
                if f.suffix.lower() not in (".png", ".jpg", ".jpeg", ".bmp"):
                    continue
                image_paths.append(str(f))
                body_labels.append(body_idx)
                fracture_labels.append(fracture_idx)
                fracture_type_labels.append(fracture_type_idx)
                type_labeled.append(labeled_type)

    if not image_paths:
        return None

    return (
        image_paths,
        np.array(body_labels, dtype=np.int32),
        np.array(fracture_labels, dtype=np.int32),
        np.array(fracture_type_labels, dtype=np.int32),
        np.array(type_labeled, dtype=bool),
    )


def body_part_class_weights(split: str = "train") -> dict[int, float]:
    """Balanced class weights for imbalanced body parts (e.g. humerus vs hand)."""
    from sklearn.utils.class_weight import compute_class_weight

    indexed = index_multitask_split(split)
    if indexed is None:
        return {}
    body_labels = indexed[1]
    classes = np.unique(body_labels)
    weights = compute_class_weight("balanced", classes=classes, y=body_labels)
    return {int(c): float(w) for c, w in zip(classes, weights)}


def _augment_image(arr: np.ndarray) -> np.ndarray:
    """Augmentation tuned for anatomical body-part recognition."""
    import random

    # Skip horizontal flip — similar joints look mirrored and confuse body-part classes.
    if random.random() < 0.5:
        factor = random.uniform(0.85, 1.15)
        arr = np.clip(arr * factor, 0.0, 1.0)
    if random.random() < 0.4:
        delta = random.uniform(-0.08, 0.08)
        arr = np.clip(arr + delta, 0.0, 1.0)
    if random.random() < 0.2:
        # Small in-plane rotation via PIL (±8°)
        from PIL import Image

        angle = random.uniform(-8, 8)
        img = Image.fromarray((arr * 255).astype(np.uint8))
        img = img.rotate(angle, resample=Image.BILINEAR)
        arr = np.array(img, dtype=np.float32) * config.NORMALIZE_SCALE
    return arr


def get_multitask_dataset(
    split: str,
    batch_size: int = config.BATCH_SIZE,
    repeat: bool = True,
    shuffle: bool | None = None,
    augment: bool | None = None,
    include_sample_weights: bool = False,
    balance_body_parts: bool = False,
):
    """
    Multi-task dataset: body part + fracture (binary) + fracture type.
    Expects structure: raw/{split}/{body_part}/fracture_{type}/image.png
    or raw/{split}/{body_part}/normal/image.png
    """
    import tensorflow as tf

    indexed = index_multitask_split(split)
    if indexed is None:
        return None
    image_paths, body_labels, fracture_labels, fracture_type_labels, type_labeled = indexed

    body_weights = body_part_class_weights(split) if balance_body_parts else {}

    if augment is None:
        augment = split == "train"

    def load_and_preprocess(path):
        """Load image in Python so we can catch corrupt files; return numpy array."""
        try:
            from PIL import Image
            with open(path, "rb") as f:
                img = Image.open(f).convert("RGB")
            img = img.resize((config.IMG_SIZE, config.IMG_SIZE))
            arr = np.array(img, dtype=np.float32) * config.NORMALIZE_SCALE
            return arr
        except Exception:
            return np.zeros((config.IMG_SIZE, config.IMG_SIZE, 3), dtype=np.float32)

    def gen():
        for i in range(len(image_paths)):
            x = load_and_preprocess(image_paths[i])
            if augment:
                x = _augment_image(x)
            y = {
                "body_part": int(body_labels[i]),
                "fracture": int(fracture_labels[i]),
                "fracture_type": int(fracture_type_labels[i]),
            }
            if include_sample_weights:
                sw = {
                    "body_part": body_weights.get(int(body_labels[i]), 1.0),
                    "fracture": 1.0,
                    "fracture_type": 1.0 if type_labeled[i] else 0.0,
                }
                yield x, y, sw
            else:
                yield x, y

    if shuffle is None:
        shuffle = split == "train"

    y_spec = {
        "body_part": tf.TensorSpec(shape=(), dtype=tf.int32),
        "fracture": tf.TensorSpec(shape=(), dtype=tf.int32),
        "fracture_type": tf.TensorSpec(shape=(), dtype=tf.int32),
    }
    if include_sample_weights:
        output_signature = (
            tf.TensorSpec(shape=(config.IMG_SIZE, config.IMG_SIZE, 3), dtype=tf.float32),
            y_spec,
            {
                "body_part": tf.TensorSpec(shape=(), dtype=tf.float32),
                "fracture": tf.TensorSpec(shape=(), dtype=tf.float32),
                "fracture_type": tf.TensorSpec(shape=(), dtype=tf.float32),
            },
        )
    else:
        output_signature = (
            tf.TensorSpec(shape=(config.IMG_SIZE, config.IMG_SIZE, 3), dtype=tf.float32),
            y_spec,
        )

    ds = tf.data.Dataset.from_generator(gen, output_signature=output_signature)
    if shuffle:
        buf = min(2000, len(image_paths))
        ds = ds.shuffle(buffer_size=buf, seed=42, reshuffle_each_iteration=True)
    ds = ds.batch(batch_size)
    if repeat:
        ds = ds.repeat()
    ds = ds.prefetch(tf.data.AUTOTUNE)
    return ds
