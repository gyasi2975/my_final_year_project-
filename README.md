# Mobile-Based Machine Learning System for Bone Fracture Detection and Heat Map Visualization

**Department of Information Technology and Decision Sciences**

A mobile app that detects bone fractures from X-ray images, classifies bones and fracture types, and generates Grad-CAM heat maps for visual explanation. Works **offline** for use in low-resource areas.

## Expected Outcomes (from proposal)

- **Accurate Fracture Detection**: Detect fractures across multiple bones from X-ray images.
- **Fracture Type Classification**: Classify as simple, comminuted, or greenstick.
- **Body Part Identification**: Identify the affected bone in the X-ray.
- **Visual Explanation**: Grad-CAM heat maps showing exact fracture locations.
- **Offline Mobile Functionality**: Fracture analysis without internet access.
- **Reliable Performance**: High accuracy, precision, recall, and F1-score.

## Project Structure

```
gloria/
├── ml/                    # Python ML pipeline
│   ├── data/              # Data loading & preprocessing
│   ├── models/            # MobileNetV2 hybrid model
│   ├── grad_cam.py        # Heat map generation
│   ├── train.py           # Training script
│   ├── export_tflite.py    # Export to TFLite for mobile
│   └── evaluate.py        # Metrics: accuracy, precision, recall, F1
├── mobile/                # Flutter app (TensorFlow Lite, offline)
└── README.md
```

## Methodology

- **Data**: MURA dataset (body parts, abnormality) + fracture datasets (e.g. FracAtlas-style labels).
- **Preprocessing**: Resize 224×224, normalize [0,1], standardize labels.
- **Model**: MobileNetV2 (CNN) — body part classification, fracture detection, fracture type classification.
- **Explainability**: Grad-CAM for heat maps.
- **Split**: 80% train, 10% validation, 10% test.
- **Mobile**: Flutter app with TensorFlow Lite for offline inference.

## Setup

### ML (Python)

```bash
cd ml
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### Mobile (Flutter)

```bash
cd mobile
flutter pub get
flutter run
```

## Usage

1. **Train model**: From project root, `cd ml` then `python train.py` (after placing datasets in `ml/data/raw/`; see `ml/data/DATA.md`). Without data, a short dummy run still produces a checkpoint for export.
2. **Export to TFLite**: `cd ml` then `python export_tflite.py` (optionally `--model checkpoints/bone_fracture_model.keras --output export/bone_fracture.tflite`).
3. **Copy** `ml/export/bone_fracture.tflite` to `mobile/assets/bone_fracture.tflite`.
4. **Run app**: `cd mobile` then `flutter pub get` and `flutter run`. Open X-ray from camera/gallery → view body part, fracture detection, fracture type, and heat map-style visualization.

## References

- Selvaraju et al. (2019). Grad-CAM: Visual explanations. IJCV.
- Stanford ML Group. MURA: Musculoskeletal radiographs.
- Su et al. (2023). Skeletal fracture detection review. Diagnostics.
