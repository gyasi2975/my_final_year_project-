"""
Prepare MURA and FracAtlas downloads into raw/train, raw/valid, raw/test.
Run from ml/ or project root:  python data/prepare_datasets.py
"""

import hashlib
import os
import shutil
import random
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
ML_DIR = SCRIPT_DIR.parent
RAW_DIR = ML_DIR / "data" / "raw"
DOWNLOADS_DIR = ML_DIR / "data" / "downloads"
MURA_DIR = DOWNLOADS_DIR / "mura"
FRACATLAS_DIR = DOWNLOADS_DIR / "fracatlas"

BODY_PARTS = ["elbow", "finger", "forearm", "hand", "humerus", "shoulder", "wrist"]
BODY_MURA_MAP = {b.upper(): b for b in BODY_PARTS}
# Official MURA v1.1 folder names (XR_ELBOW, …)
BODY_MURA_XR_MAP = {
    "XR_ELBOW": "elbow",
    "XR_FINGER": "finger",
    "XR_FOREARM": "forearm",
    "XR_HAND": "hand",
    "XR_HUMERUS": "humerus",
    "XR_SHOULDER": "shoulder",
    "XR_WRIST": "wrist",
}
FRACTURE_FOLDERS = [
    "normal",
    "fracture_simple",
    "fracture_comminuted",
    "fracture_greenstick",
    "fracture_unlabeled",  # MURA positive (abnormal) — no fracture-type label
]
TRAIN_RATIO, VAL_RATIO, TEST_RATIO = 0.8, 0.1, 0.1


def ensure_raw_dirs():
    for split in ["train", "valid", "test"]:
        for body in BODY_PARTS:
            for folder in FRACTURE_FOLDERS:
                (RAW_DIR / split / body / folder).mkdir(parents=True, exist_ok=True)


def _mura_roots():
    """Return candidate MURA dataset roots (handles MURA-v1.1 subfolder)."""
    if not MURA_DIR.exists():
        return []
    roots = [MURA_DIR]
    for name in ("MURA-v1.1", "MURA-v1.0", "mura-v1.1"):
        nested = MURA_DIR / name
        if nested.is_dir():
            roots.append(nested)
    return roots


def find_mura_images():
    """Find MURA images.

    Supports official layout:
      MURA-v1.1/train/XR_ELBOW/patient00001/study1_positive/image1.png
    and legacy positive/negative folder layouts.
    """
    images = []  # (path, body_part, is_positive)
    seen = set()

    def add(path: Path, body: str, is_pos: bool):
        key = str(path.resolve())
        if key in seen:
            return
        seen.add(key)
        images.append((str(path), body, is_pos))

    for base in _mura_roots():
        # Official v1.1: train|valid / XR_* / patient / study*_positive|negative / *.png
        for split in ("train", "valid"):
            split_dir = base / split
            if not split_dir.is_dir():
                continue
            for xr_name, body in BODY_MURA_XR_MAP.items():
                part_dir = split_dir / xr_name
                if not part_dir.is_dir():
                    continue
                for f in part_dir.rglob("*"):
                    if f.suffix.lower() not in (".png", ".jpg", ".jpeg"):
                        continue
                    path_lower = str(f).lower().replace("\\", "/")
                    if "positive" in path_lower:
                        add(f, body, True)
                    elif "negative" in path_lower:
                        add(f, body, False)

        # Legacy: train/ELBOW/positive/*.png
        for part_upper, part_lower in BODY_MURA_MAP.items():
            for split in ("train", "valid", "Train", "Valid"):
                part_dir = base / split / part_upper
                if not part_dir.is_dir():
                    part_dir = base / split / part_upper.lower()
                if not part_dir.is_dir():
                    continue
                for label_dir in ("positive", "negative", "Positive", "Negative"):
                    label_path = part_dir / label_dir
                    if not label_path.is_dir():
                        continue
                    is_pos = label_dir.lower() == "positive"
                    for ext in ("*.png", "*.jpg", "*.jpeg"):
                        for f in label_path.rglob(ext):
                            add(f, part_lower, is_pos)

    return images


def find_fracatlas_images():
    """Find FracAtlas images and map to body part + fracture type if possible."""
    images = []  # (path, body_part, fracture_folder)
    base = FRACATLAS_DIR
    if not base.exists():
        return images
    # Common FracAtlas layout: images in folder, CSV with labels
    csv_files = list(base.rglob("*.csv"))
    for csv_path in csv_files:
        try:
            import csv
            with open(csv_path, newline="", encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    path = row.get("image_path") or row.get("path") or row.get("filename") or row.get("image")
                    if not path:
                        continue
                    full = base / path if not (base / path).exists() else Path(path)
                    if not full.exists():
                        full = csv_path.parent / path
                    if not full.exists():
                        continue
                    label = (row.get("label") or row.get("fracture_type") or row.get("type") or "simple").strip().lower()
                    body = "hand"  # default if not in CSV
                    for b in BODY_PARTS:
                        if b in label or b in path.lower():
                            body = b
                            break
                    if "normal" in label or "negative" in label or "no_fracture" in label:
                        folder = "normal"
                    elif "comminuted" in label:
                        folder = "fracture_comminuted"
                    elif "greenstick" in label:
                        folder = "fracture_greenstick"
                    else:
                        folder = "fracture_simple"
                    images.append((str(full), body, folder))
        except Exception:
            pass
    seen_paths = {Path(p).resolve() for p, _, _ in images}
    for ext in ["*.png", "*.jpg", "*.jpeg"]:
        for f in base.rglob(ext):
            if f.resolve() in seen_paths:
                continue
            # No CSV row: treat as fractured with unknown type (not "simple")
            images.append((str(f), "hand", "fracture_unlabeled"))
    return images


def split_and_copy(images_by_split, is_mura=True, respect_mura_official_split=False):
    """images_by_split: list of (path, body, folder). folder is 'normal' or 'fracture_*'."""
    for path, body, folder in images_by_split:
        src = Path(path)
        if not src.exists():
            continue
        if is_mura and folder == "fracture":
            folder = "fracture_simple"
        if is_mura and folder not in FRACTURE_FOLDERS:
            folder = "fracture_simple" if folder else "normal"

        if is_mura and respect_mura_official_split:
            path_lower = str(src).lower().replace("\\", "/")
            if "/valid/" in path_lower:
                split = "valid" if random.random() < 0.5 else "test"
            else:
                split = "train"
        else:
            r = random.random()
            if r < TRAIN_RATIO:
                split = "train"
            elif r < TRAIN_RATIO + VAL_RATIO:
                split = "valid"
            else:
                split = "test"

        dest_dir = RAW_DIR / split / body / folder
        dest_dir.mkdir(parents=True, exist_ok=True)
        # Unique name (many MURA studies use image1.png, image2.png, …)
        digest = hashlib.sha1(str(src.resolve()).encode()).hexdigest()[:12]
        dest = dest_dir / f"{digest}_{src.name}"
        try:
            if dest.exists():
                continue
            if dest.resolve() == src.resolve():
                continue
            try:
                os.link(src, dest)
            except OSError:
                shutil.copy2(src, dest)
        except Exception as e:
            print("Skip", src, e)


def main():
    random.seed(42)
    ensure_raw_dirs()
    print("Raw dirs ready at", RAW_DIR, flush=True)

    # MURA
    mura_images = find_mura_images()
    if mura_images:
        print("Found", len(mura_images), "MURA images", flush=True)
        mura_by_split = []
        for path, body, is_pos in mura_images:
            # MURA provides normal/abnormal only — not simple/comminuted/greenstick
            folder = "fracture_unlabeled" if is_pos else "normal"
            mura_by_split.append((path, body, folder))
        split_and_copy(mura_by_split, is_mura=True, respect_mura_official_split=True)
    else:
        print("No MURA data found under", MURA_DIR)
        print("  Unzip MURA into data/downloads/mura/ (e.g. mura/MURA-v1.1/train/XR_ELBOW/...).")

    # FracAtlas
    frac_images = find_fracatlas_images()
    if frac_images:
        print("Found", len(frac_images), "FracAtlas images", flush=True)
        split_and_copy(frac_images, is_mura=False)
    else:
        print("No FracAtlas data found under", FRACATLAS_DIR)

    print("Done. Check", RAW_DIR, "then run: python train.py", flush=True)
    if not mura_images and not frac_images:
        print("No images were copied. Add MURA or FracAtlas under data/downloads/ and run this script again.")


if __name__ == "__main__":
    main()
