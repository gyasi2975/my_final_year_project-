"""
Grad-CAM heat map generation per proposal:
"Grad-CAM heat maps highlight fracture locations, enhancing clinical trust in AI predictions."
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
import sys
from pathlib import Path

_ML_ROOT = Path(__file__).resolve().parent
if str(_ML_ROOT) not in sys.path:
    sys.path.insert(0, str(_ML_ROOT))

import config


def _find_target_layer(model):
    """Find last conv layer in base (MobileNetV2)."""
    for layer in reversed(model.layers):
        if len(layer.output_shape) == 4:
            return layer
    return None


def make_gradcam_heatmap(
    model: keras.Model,
    img_array: np.ndarray,
    pred_index: int = None,
    layer_name: str = None,
):
    """
    Generate Grad-CAM heat map for a single image.
    img_array: (H, W, 3) normalized [0, 1].
    For fracture explanation we typically use the 'fracture' head or last conv.
    """
    if len(img_array.shape) == 3:
        img_array = np.expand_dims(img_array, axis=0)

    # Build gradient model: input -> target_layer -> output (fracture logit)
    if layer_name:
        target_layer = model.get_layer(layer_name)
    else:
        target_layer = _find_target_layer(model)
    if target_layer is None:
        raise ValueError("No 4D conv layer found for Grad-CAM.")

    grad_model = keras.Model(
        inputs=model.input,
        outputs=[target_layer.output, model.get_layer("fracture").output],
    )

    with tf.GradientTape() as tape:
        conv_output, preds = grad_model(img_array)
        if pred_index is None:
            pred_index = tf.argmax(preds[0]) if preds.shape[-1] > 1 else 0
        class_channel = preds[:, pred_index]

    grads = tape.gradient(class_channel, conv_output)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    conv_output = conv_output[0]
    heatmap = conv_output @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-8)
    return heatmap.numpy()


def overlay_heatmap_on_image(heatmap: np.ndarray, img: np.ndarray, alpha: float = 0.4):
    """Overlay heatmap on image for visualization."""
    import cv2
    heatmap = np.uint8(255 * heatmap)
    heatmap = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    if img.shape[-1] == 3:
        img = (img * 255).astype(np.uint8)
    overlay = cv2.addWeighted(img, 1 - alpha, heatmap, alpha, 0)
    return overlay


def save_heatmap_image(heatmap: np.ndarray, img: np.ndarray, path: str, alpha: float = 0.4):
    """Save overlay to file."""
    import cv2
    overlay = overlay_heatmap_on_image(heatmap, img, alpha)
    cv2.imwrite(path, cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
