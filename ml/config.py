"""Configuration aligned with proposal: 224x224, 80/10/10 split, metrics."""

# Image preprocessing (proposal: resize 224x224, normalize 0-1)
IMG_SIZE = 224
NORMALIZE_SCALE = 1.0 / 255.0

# Data split (proposal: 80% train, 10% validation, 10% test)
TRAIN_RATIO = 0.8
VAL_RATIO = 0.1
TEST_RATIO = 0.1

# Body parts (MURA-style: multiple body parts)
BODY_PARTS = [
    "elbow",
    "finger",
    "forearm",
    "hand",
    "humerus",
    "shoulder",
    "wrist",
]

# Fracture types (proposal: simple, comminuted, greenstick)
FRACTURE_TYPES = ["simple", "comminuted", "greenstick"]

# Model
MODEL_INPUT_SHAPE = (IMG_SIZE, IMG_SIZE, 3)
BATCH_SIZE = 32
EPOCHS = 20

# Evaluation metrics (proposal: accuracy, precision, recall, F1-score)
METRICS = ["accuracy", "precision", "recall", "f1"]
