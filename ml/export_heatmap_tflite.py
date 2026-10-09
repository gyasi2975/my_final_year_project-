"""Export on-device fracture heatmap TFLite model (Grad-CAM weights baked in)."""

import argparse
import json
import sys
from pathlib import Path

_ML_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ML_ROOT))

import tensorflow as tf
from grad_cam import (
    build_heatmap_model,
    compute_avg_gradcam_weights,
    list_fracture_sample_paths,
)


def export_heatmap_tflite(
    model_path: str = "checkpoints/bone_fracture_model.keras",
    output_path: str = "export/fracture_heatmap.tflite",
    weights_path: str = "export/heatmap_channel_weights.json",
    max_samples: int = 80,
    use_float32: bool = True,
):
    model_path = Path(model_path)
    output_path = Path(output_path)
    weights_path = Path(weights_path)
    if not model_path.is_absolute():
        model_path = _ML_ROOT / model_path
    if not output_path.is_absolute():
        output_path = _ML_ROOT / output_path
    if not weights_path.is_absolute():
        weights_path = _ML_ROOT / weights_path

    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    model = tf.keras.models.load_model(str(model_path))

    sample_paths = list_fracture_sample_paths(max_paths=max_samples)
    if len(sample_paths) < 5:
        raise RuntimeError(
            "Not enough fracture training images to compute Grad-CAM weights. "
            "Expected images under ml/data/raw/train/*/fracture_*"
        )

    print(f"Computing Grad-CAM weights from {len(sample_paths)} fracture images...")
    channel_weights = compute_avg_gradcam_weights(model, sample_paths, max_samples=max_samples)
    weights_path.write_text(
        json.dumps({"channels": int(channel_weights.shape[0]), "weights": channel_weights.tolist()}),
        encoding="utf-8",
    )
    print("Saved channel weights to", weights_path)

    heatmap_model = build_heatmap_model(model, channel_weights)
    heatmap_model.summary()

    converter = tf.lite.TFLiteConverter.from_keras_model(heatmap_model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    if use_float32:
        pass
    else:
        converter.target_spec.supported_types = [tf.float16]

    tflite_model = converter.convert()
    output_path.write_bytes(tflite_model)
    print("TFLite heatmap model saved to", output_path)
    return str(output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export fracture heatmap TFLite model")
    parser.add_argument("--model", default="checkpoints/bone_fracture_model.keras")
    parser.add_argument("--output", default="export/fracture_heatmap.tflite")
    parser.add_argument("--weights", default="export/heatmap_channel_weights.json")
    parser.add_argument("--max-samples", type=int, default=80)
    parser.add_argument("--float32", action="store_true", default=True)
    args = parser.parse_args()
    export_heatmap_tflite(
        model_path=args.model,
        output_path=args.output,
        weights_path=args.weights,
        max_samples=args.max_samples,
        use_float32=args.float32,
    )
