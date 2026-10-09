"""Export validity model to TFLite for mobile gate."""

import argparse
import sys
from pathlib import Path

_ML_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ML_ROOT))

import tensorflow as tf


def export_validity_tflite(
    model_path: str = "checkpoints/xray_validity_model.keras",
    output_path: str = "export/xray_validity.tflite",
    use_float32: bool = True,
):
    model_path = Path(model_path)
    output_path = Path(output_path)
    if not model_path.is_absolute():
        model_path = _ML_ROOT / model_path
    if not output_path.is_absolute():
        output_path = _ML_ROOT / output_path

    if not model_path.exists():
        print("Model not found:", model_path)
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    model = tf.keras.models.load_model(str(model_path))
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    if not use_float32:
        converter.target_spec.supported_types = [tf.float16]
    tflite_model = converter.convert()
    output_path.write_bytes(tflite_model)
    print("TFLite saved to", output_path)
    return str(output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="checkpoints/xray_validity_model.keras")
    parser.add_argument("--output", default="export/xray_validity.tflite")
    parser.add_argument("--float32", action="store_true", default=True)
    args = parser.parse_args()
    export_validity_tflite(args.model, args.output, use_float32=args.float32)
