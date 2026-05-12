"""
Hybrid deep learning model per proposal:
- MobileNetV2 (CNN): high accuracy, low computational cost for mobile
- Three tasks: body part classification, fracture detection, fracture type classification
"""

import sys
from pathlib import Path

_ML_ROOT = Path(__file__).resolve().parent.parent
if str(_ML_ROOT) not in sys.path:
    sys.path.insert(0, str(_ML_ROOT))

import config
from tensorflow import keras
from tensorflow.keras import layers


def build_hybrid_mobilenetv2(
    num_body_parts: int = len(config.BODY_PARTS),
    num_fracture_types: int = len(config.FRACTURE_TYPES),
    input_shape: tuple = config.MODEL_INPUT_SHAPE,
):
    """
    Build hybrid MobileNetV2 with three heads:
    1. Body part classification (num_body_parts)
    2. Fracture detection (binary)
    3. Fracture type classification (simple, comminuted, greenstick)
    """
    inputs = keras.Input(shape=input_shape)

    base = keras.applications.MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights="imagenet",
        pooling="avg",
    )
    base.trainable = True
    # Fine-tune from later layers for better adaptation
    for layer in base.layers[:-30]:
        layer.trainable = False

    x = base(inputs)
    x = layers.Dropout(0.3)(x)

    # Head 1: Body part
    body_out = layers.Dense(num_body_parts, activation="softmax", name="body_part")(x)

    # Head 2: Fracture (binary)
    fracture_out = layers.Dense(1, activation="sigmoid", name="fracture")(x)

    # Head 3: Fracture type (only meaningful when fracture=1)
    fracture_type_out = layers.Dense(
        num_fracture_types, activation="softmax", name="fracture_type"
    )(x)

    model = keras.Model(
        inputs=inputs,
        outputs={
            "body_part": body_out,
            "fracture": fracture_out,
            "fracture_type": fracture_type_out,
        },
        name="bone_fracture_hybrid",
    )

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-4),
        loss={
            "body_part": "sparse_categorical_crossentropy",
            "fracture": "binary_crossentropy",
            "fracture_type": "sparse_categorical_crossentropy",
        },
        loss_weights={
            "body_part": 1.0,
            "fracture": 1.5,
            "fracture_type": 1.0,
        },
        metrics={
            "body_part": ["accuracy"],
            "fracture": ["accuracy"],
            "fracture_type": ["accuracy"],
        },
    )
    return model
