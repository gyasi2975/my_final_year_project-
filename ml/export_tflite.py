"""
Export trained model to TensorFlow Lite for mobile (offline) deployment.
Proposal: "Deploy on mobile app for offline use" with TensorFlow Lite (TFLite).
"""

import sys
import argparse
from pathlib import Path

_ML_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ML_ROOT))

import tensorflow as tf
import config


def export_to_tflite(
    model_path: str = "checkpoints/bone_fracture_model.keras",
    output_path: str = "export/bone_fracture.tflite",
    use_float32: bool = False,
):
    """Convert Keras model to TFLite for mobile.
    use_float32=True: better device compatibility (avoids CONV_2D failed to prepare on some phones).
    use_float32=False: smaller model with float16, may fail on some devices.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    model = tf.keras.models.load_model(model_path)

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    if not use_float32:
        converter.target_spec.supported_types = [tf.float16]
    # else: keep float32 for max compatibility
    tflite_model = converter.convert()
    with open(output_path, "wb") as f:
        f.write(tflite_model)
    print("TFLite model saved to", output_path)
    return output_path


def export_saved_model_for_gradcam(model_path: str, export_dir: str = "export/saved_model"):
    """Export SavedModel so mobile or server can run Grad-CAM if needed."""
    model = tf.keras.models.load_model(model_path)
    Path(export_dir).mkdir(parents=True, exist_ok=True)
    model.save(export_dir, save_format="tf")
    print("SavedModel for Grad-CAM export at", export_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="checkpoints/bone_fracture_model.keras")
    parser.add_argument("--output", default="export/bone_fracture.tflite")
    parser.add_argument("--float32", action="store_true", help="Export float32 for device compatibility (if CONV_2D fails on device)")
    args = parser.parse_args()
    model_path = Path(args.model)
    output_path = Path(args.output)
    if not model_path.is_absolute():
        model_path = _ML_ROOT / model_path
    if not output_path.is_absolute():
        output_path = _ML_ROOT / output_path
    if not model_path.exists():
        print("Error: Model not found at", model_path)
        print("Run training first: python train.py --epochs 20")
        sys.exit(1)
    export_to_tflite(str(model_path), str(output_path), use_float32=args.float32)
