"""Binary classifier: related extremity X-ray vs unrelated image."""

import sys
from pathlib import Path

_ML_ROOT = Path(__file__).resolve().parent.parent
if str(_ML_ROOT) not in sys.path:
    sys.path.insert(0, str(_ML_ROOT))

import config
from tensorflow import keras
from tensorflow.keras import layers


def build_validity_mobilenetv2(input_shape: tuple = config.MODEL_INPUT_SHAPE):
    """1 = related extremity X-ray, 0 = unrelated."""
    inputs = keras.Input(shape=input_shape)
    base = keras.applications.MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights="imagenet",
        pooling="avg",
    )
    base.trainable = True
    for layer in base.layers[:-30]:
        layer.trainable = False

    x = layers.Dropout(0.3)(base(inputs))
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(1, activation="sigmoid", name="related")(x)

    model = keras.Model(inputs=inputs, outputs=outputs, name="xray_validity")
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-4),
        loss="binary_crossentropy",
        metrics=["accuracy", keras.metrics.AUC(name="auc")],
    )
    return model
