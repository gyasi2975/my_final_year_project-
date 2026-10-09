"""
Grad-CAM heat map generation per proposal:
"Grad-CAM heat maps highlight fracture locations, enhancing clinical trust in AI predictions."
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

_ML_ROOT = Path(__file__).resolve().parent
if str(_ML_ROOT) not in sys.path:
    sys.path.insert(0, str(_ML_ROOT))

import config

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}


def find_mobilenet_backbone(model: keras.Model) -> keras.Model:
    for layer in model.layers:
        if isinstance(layer, keras.Model) and "mobilenet" in layer.name.lower():
            return layer
    raise ValueError("MobileNetV2 backbone not found in model.")


def find_last_conv_layer(model: keras.Model) -> layers.Layer:
    """Find last Conv2D in MobileNetV2 (typically 7×7×1280)."""
    backbone = find_mobilenet_backbone(model)
    conv_layers = [layer for layer in backbone.layers if isinstance(layer, layers.Conv2D)]
    if not conv_layers:
        raise ValueError("No Conv2D layer found in MobileNetV2 backbone.")
    return conv_layers[-1]


def _load_image(path: str) -> np.ndarray:
    from PIL import Image

    with open(path, "rb") as f:
        img = Image.open(f).convert("RGB")
    img = img.resize((config.IMG_SIZE, config.IMG_SIZE))
    return np.array(img, dtype=np.float32) * config.NORMALIZE_SCALE


def make_gradcam_heatmap(
    model: keras.Model,
    img_array: np.ndarray,
    pred_index: int | None = None,
    layer_name: str | None = None,
) -> np.ndarray:
    """
    Generate Grad-CAM heat map for a single image.
    img_array: (H, W, 3) normalized [0, 1].
    Uses the fracture head output by default.
    """
    if len(img_array.shape) == 3:
        img_array = np.expand_dims(img_array, axis=0)

    if layer_name:
        target_layer = model.get_layer(layer_name)
    else:
        target_layer = find_last_conv_layer(model)

    grad_model = keras.Model(
        inputs=model.input,
        outputs=[target_layer.output, model.get_layer("fracture").output],
    )

    with tf.GradientTape() as tape:
        conv_output, preds = grad_model(img_array, training=False)
        if pred_index is None:
            pred_index = 0
        class_channel = preds[:, pred_index]

    grads = tape.gradient(class_channel, conv_output)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    conv_output = conv_output[0]
    heatmap = conv_output @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-8)
    return heatmap.numpy()


def compute_avg_gradcam_weights(
    model: keras.Model,
    image_paths: list[str],
    max_samples: int = 80,
) -> np.ndarray:
    """Average Grad-CAM channel weights across sample images."""
    target_layer = find_last_conv_layer(model)
    grad_model = keras.Model(
        inputs=model.input,
        outputs=[target_layer.output, model.get_layer("fracture").output],
    )

    weights_sum: np.ndarray | None = None
    used = 0
    for path in image_paths[:max_samples]:
        try:
            img = _load_image(path)
        except OSError:
            continue
        img_batch = np.expand_dims(img, axis=0)
        with tf.GradientTape() as tape:
            conv_output, preds = grad_model(img_batch, training=False)
            class_channel = preds[:, 0]
        grads = tape.gradient(class_channel, conv_output)
        if grads is None:
            continue
        pooled = tf.reduce_mean(grads, axis=(0, 1, 2)).numpy()
        weights_sum = pooled if weights_sum is None else weights_sum + pooled
        used += 1

    if weights_sum is None or used == 0:
        raise ValueError("Could not compute Grad-CAM weights (no valid images).")
    return weights_sum / used


def list_fracture_sample_paths(raw_dir: Path | None = None, max_paths: int = 120) -> list[str]:
    """Collect fracture-positive images from the training split."""
    raw_dir = raw_dir or (_ML_ROOT / "data" / "raw" / "train")
    paths: list[str] = []
    if not raw_dir.exists():
        return paths
    for body_dir in sorted(raw_dir.iterdir()):
        if not body_dir.is_dir():
            continue
        for label_dir in sorted(body_dir.iterdir()):
            if not label_dir.is_dir():
                continue
            name = label_dir.name.lower()
            if name == "normal":
                continue
            if not (name.startswith("fracture") or "fracture" in name):
                continue
            for img_path in sorted(label_dir.rglob("*")):
                if img_path.suffix.lower() in IMAGE_EXTS:
                    paths.append(str(img_path))
                    if len(paths) >= max_paths:
                        return paths
    return paths


def build_heatmap_model(model: keras.Model, channel_weights: np.ndarray) -> keras.Model:
    """Build a forward-only model: input image -> 7×7 normalized heatmap."""
    target_layer = find_last_conv_layer(model)
    conv_model = keras.Model(model.input, target_layer.output, name="conv_features")
    weights = tf.constant(channel_weights, dtype=tf.float32)

    inputs = keras.Input(shape=config.MODEL_INPUT_SHAPE, name="heatmap_input")
    conv_out = conv_model(inputs)
    heatmap = tf.reduce_sum(conv_out * weights, axis=-1)
    heatmap = tf.maximum(heatmap, 0)
    heatmap = heatmap / (tf.reduce_max(heatmap) + 1e-8)
    heatmap = tf.expand_dims(heatmap, axis=-1, name="heatmap")
    return keras.Model(inputs, heatmap, name="fracture_heatmap")


def overlay_heatmap_on_image(heatmap: np.ndarray, img: np.ndarray, alpha: float = 0.4):
    """Overlay heatmap on image for visualization."""
    import cv2

    heatmap = np.uint8(255 * heatmap)
    heatmap = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    if img.shape[-1] == 3:
        img = (img * 255).astype(np.uint8) if img.max() <= 1.0 else img.astype(np.uint8)
    overlay = cv2.addWeighted(img, 1 - alpha, heatmap, alpha, 0)
    return overlay


def save_heatmap_image(heatmap: np.ndarray, img: np.ndarray, path: str, alpha: float = 0.4):
    """Save overlay to file."""
    import cv2

    overlay = overlay_heatmap_on_image(heatmap, img, alpha)
    cv2.imwrite(path, cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
