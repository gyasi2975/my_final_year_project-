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
    loss_weights: dict | None = None,
    learning_rate: float = 1e-4,
):
    """
    Build hybrid MobileNetV2 with three heads:
    1. Body part classification (deeper dedicated branch)
    2. Fracture detection (binary)
    3. Fracture type classification (simple, comminuted, greenstick)
    """
    if loss_weights is None:
        loss_weights = config.LOSS_WEIGHTS

    inputs = keras.Input(shape=input_shape)

    base = keras.applications.MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights="imagenet",
        pooling="avg",
    )
    base.trainable = True
    for layer in base.layers[:-40]:
        layer.trainable = False

    features = base(inputs)

    # Dedicated body-part branch (more capacity than a single shared Dense)
    body_x = layers.Dense(
        config.BODY_PART_BRANCH_UNITS, activation="relu", name="body_part_dense"
    )(features)
    body_x = layers.Dropout(0.4)(body_x)
    body_out = layers.Dense(num_body_parts, activation="softmax", name="body_part")(body_x)

    # Fracture heads share a lighter branch
    task_x = layers.Dropout(0.3)(features)
    fracture_out = layers.Dense(1, activation="sigmoid", name="fracture")(task_x)
    fracture_type_out = layers.Dense(
        num_fracture_types, activation="softmax", name="fracture_type"
    )(task_x)

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
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss={
            "body_part": "sparse_categorical_crossentropy",
            "fracture": "binary_crossentropy",
            "fracture_type": "sparse_categorical_crossentropy",
        },
        loss_weights=loss_weights,
        metrics={
            "body_part": ["accuracy"],
            "fracture": ["accuracy"],
            "fracture_type": ["accuracy"],
        },
    )
    return model
