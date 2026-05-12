# Thesis Reference Document
## Mobile-Based Machine Learning System for Bone Fracture Detection and Heat Map Visualization from X-Ray Images

**Institution:** Department of Information Technology and Decision Sciences, University of Energy and Natural Resources (UENR), Sunyani, Ghana  
**Document type:** Compiled reference for thesis/documentation writing  
**Date compiled:** April 2026

---

## TABLE OF CONTENTS

1. [Project Identity](#1-project-identity)
2. [Background and Context](#2-background-and-context)
3. [Problem Statement](#3-problem-statement)
4. [Objectives](#4-objectives)
5. [Significance of the Study](#5-significance-of-the-study)
6. [Scope and Limitations](#6-scope-and-limitations)
7. [Literature Review Summary](#7-literature-review-summary)
8. [Theoretical Frameworks](#8-theoretical-frameworks)
9. [Related Work and Existing Systems](#9-related-work-and-existing-systems)
10. [Technology Stack and Justifications](#10-technology-stack-and-justifications)
11. [Research Methodology](#11-research-methodology)
12. [Data Sources and Preprocessing](#12-data-sources-and-preprocessing)
13. [Model Architecture (Implementation)](#13-model-architecture-implementation)
14. [Grad-CAM Implementation](#14-grad-cam-implementation)
15. [Mobile Application (Implementation)](#15-mobile-application-implementation)
16. [Evaluation Framework](#16-evaluation-framework)
17. [Implementation Status vs. Requirements](#17-implementation-status-vs-requirements)
18. [Ethical Considerations](#18-ethical-considerations)
19. [Project Timeline](#19-project-timeline)
20. [References](#20-references)

---

## 1. Project Identity

| Field | Value |
|-------|-------|
| **Full title** | Mobile-Based Machine Learning System for Bone Fracture Detection and Heat Map Visualization from X-Ray Images |
| **Short title** | Bone Fracture Detection Mobile App |
| **App name** | "Smarter Health Better You" / `bone_fracture_app` |
| **App version** | 1.0.0+1 |
| **Department** | Information Technology and Decision Sciences |
| **Institution** | University of Energy and Natural Resources (UENR), Sunyani, Ghana |
| **Primary language (ML)** | Python 3.9+ |
| **Primary language (Mobile)** | Dart 2.19+ (Flutter 3.10+) |
| **Repository structure** | `ml/` (Python ML pipeline) + `mobile/` (Flutter app) |

---

## 2. Background and Context

### Key Facts for Writing

- **Medical imaging context:** X-ray radiography is the most widely used and accessible technique for evaluating musculoskeletal injuries. Bones appear white (radiopaque) due to calcium content; fractures appear as linear lucencies disrupting bone continuity.
- **Global burden:** WHO (2021) classifies musculoskeletal conditions, including fractures, as among the leading causes of disability worldwide.
- **Ghana-specific context:** Shortage of specialized radiologists; high radiologist-to-patient ratio inadequacy leads to prolonged wait times and diagnostic errors due to fatigue.
- **Diagnostic error rates:** Miss rates for fractures in emergency departments range from 3%–15%, varying by anatomical site and clinician expertise.
- **AI/CNN context:** CNNs have demonstrated performance comparable to or exceeding human experts in specific medical imaging domains. X-ray fracture detection has evolved from traditional computer vision (hand-crafted features) to deep learning (2015–present).
- **Explainability barrier:** Most deep learning fracture models operate as "black boxes," limiting clinical trust and adoption.
- **Mobile opportunity:** TensorFlow Lite enables sophisticated ML models on smartphones; offline deployment democratizes access in underserved, low-connectivity areas.
- **Grad-CAM:** Generates heat maps highlighting the regions influencing a model's prediction — bridges the explainability gap.

---

## 3. Problem Statement

Seven interconnected problems motivate this project:

| # | Problem | Key Detail |
|---|---------|------------|
| 1 | **Limitations of manual interpretation** | Radiologist shortage in Ghana; fatigue; subtle fractures (hairline, non-displaced) easily missed |
| 2 | **Fragmentation of AI solutions** | Current ML systems are single-anatomical-region; cannot generalize across bone types without retraining |
| 3 | **Lack of explainability** | Black-box predictions; clinicians cannot verify AI reasoning; adoption is limited |
| 4 | **Inaccessibility in low-resource settings** | High-performance computing + stable internet required; rural Ghana facilities lack this |
| 5 | **Limited fracture type classification** | Most systems do binary classification only; fracture type (simple, comminuted, greenstick) has treatment implications |
| 6 | **Data scarcity and generalization** | Public datasets have limited demographic/equipment diversity; models may not generalize |
| 7 | **Gap in offline mobile deployment** | No existing system combines multi-bone detection + fracture type + heat maps + offline mobile capability |

---

## 4. Objectives

### 4.1 General Objective

> Develop a mobile-based machine learning system capable of detecting bone fractures, classifying affected bones and fracture types, and generating Grad-CAM heat maps for visual explanation from X-ray images.

### 4.2 Specific Objectives

| # | Objective | Summary |
|---|-----------|---------|
| SO1 | **Data Acquisition and Preparation** | Collect, preprocess, and curate X-ray images from MURA and FracAtlas datasets; ensure proper labeling and formatting |
| SO2 | **Hybrid Deep Learning Model Development** | Design and implement MobileNetV2-based model performing three concurrent tasks: body part ID, fracture detection, fracture type classification |
| SO3 | **Explainability Integration** | Implement Grad-CAM to generate heat maps highlighting fracture regions; provide interpretable, trustworthy outputs |
| SO4 | **Mobile Application Deployment** | Deploy trained model via TensorFlow Lite + Flutter; enable fully offline fracture analysis on Android |
| SO5 | **System Performance Evaluation** | Evaluate accuracy, precision, recall, F1-score on held-out test set; qualitative review of heat map clinical relevance |

---

## 5. Significance of the Study

| Stakeholder | Impact |
|-------------|--------|
| **Healthcare delivery / patients** | Rapid, accurate detection as decision support; reduces missed fractures; heat map visualization for clinician verification |
| **Underserved / remote communities** | Offline mobile capability enables deployment in rural clinics without specialists or internet |
| **Ghanaian healthcare system** | Cost-effective augmentation of limited radiology workforce; proof-of-concept for AI in Ghana |
| **Clinical education** | Heat maps serve as educational tools for medical students/residents; second-opinion tool for practicing clinicians |
| **Academic research** | Contributes to literature on multi-bone detection, fracture type classification, offline mobile deployment |
| **Technology transfer** | Template for similar innovations in other diagnostic domains across Ghana and Africa |

---

## 6. Scope and Limitations

### 6.1 In Scope

| Area | Detail |
|------|--------|
| **Geographical/institutional** | Academic: UENR, Sunyani; intended for broader healthcare application; no direct patient interaction or clinical trials |
| **Datasets** | MURA (Stanford ML Group, 2018): 40,561 images, 7 upper body parts; FracAtlas (Hardalaç et al., 2022): 4,083 images with fracture type annotations |
| **Body parts** | Shoulder, elbow, forearm, hand, wrist, humerus, finger (7 classes) |
| **Fracture types** | Simple (closed), Comminuted, Greenstick (3 classes) |
| **ML tasks** | Body part classification, fracture detection (binary), fracture type classification |
| **Mobile platform** | Android (Flutter + TensorFlow Lite); offline inference |
| **Evaluation metrics** | Accuracy, Precision, Recall, F1-score |

### 6.2 Out of Scope

- Other imaging modalities: CT, MRI, ultrasound
- Real-time video or fluoroscopic imaging
- Hospital information systems / EMR integration
- Clinical validation with live patients
- iOS deployment (Android prevalence in Ghanaian market)
- Pathological, stress, avulsion fracture types
- Data collection from patients or healthcare facilities

---

## 7. Literature Review Summary

### Key Findings from Literature

1. **CNNs outperform traditional methods** — Accuracies 83%–98% depending on anatomical site (Su et al., 2023, systematic review of 87 studies)
2. **Single-site dominance** — Wrist and hip fractures most studied; multi-bone systems rare
3. **MURA benchmark** — Best model: 82.4% accuracy across 7 upper extremity regions (Rajpurkar et al., 2018)
4. **Multi-task learning advantage** — Sharing representations across body part + fracture tasks improves performance vs. separate models (Oberije et al., 2020)
5. **Fracture type classification is harder** — Lower accuracy than binary detection; requires larger datasets (Olczak et al., 2017)
6. **Explainability as adoption barrier** — Grad-CAM is the most commonly used technique; coarse spatial resolution is a known limitation (Zhou et al., 2022)
7. **Mobile feasibility demonstrated** — Li et al. (2021) achieved 89% accuracy for offline wrist fracture detection with TFLite
8. **Validation gap** — Technical performance ≠ clinical effectiveness; models fail to generalize to new populations/equipment (Kelly et al., 2019)

---

## 8. Theoretical Frameworks

### 8.1 X-Ray Physics Basis

- X-rays discovered by Wilhelm Röntgen (1895)
- Dense bone (calcium) = radiopaque (white); soft tissue = radiolucent (dark)
- Fractures: linear lucencies, cortical step-offs, angulation, or displacement
- Reference: Bushberg et al. (2020); Whitley et al. (2015)

### 8.2 CNN Architecture Theory

**Key components:**
- **Convolutional Layers** — learnable filters detect local patterns (edges, textures, shapes); preserve spatial relationships
- **Pooling Layers** — reduce spatial dimensions; max pooling common in medical imaging
- **ReLU Activation** — introduces non-linearity; enables complex pattern learning
- **Fully Connected Layers** — integrate learned features for classification

### 8.3 Transfer Learning

- ImageNet pretrained models learn general features (edges, textures) transferable to medical imaging
- Early layers: general features; later layers: task-specific
- Enables good performance with limited medical data; reduces training time
- Reference: Yosinski et al. (2014); Tajbakhsh et al. (2016)

### 8.4 MobileNetV2 Architecture

- Developed by Sandler et al. (2018)
- **Key innovations:** Inverted residual structures + linear bottlenecks
- 3.4M parameters; 72.0% ImageNet Top-1 accuracy; fast mobile inference
- Specifically designed for resource-constrained on-device deployment
- Seamless TensorFlow Lite conversion

### 8.5 Grad-CAM Theory

- Selvaraju et al. (2019) — IJCV
- Uses gradients of target class score flowing into last convolutional layer
- Produces coarse localization map (heatmap) highlighting important image regions
- No retraining required; model-agnostic; clinically intuitive
- **Mathematical steps:**
  1. Forward pass → class score
  2. Compute gradient of score w.r.t. last conv feature maps
  3. Global average pool gradients → neuron importance weights α
  4. Weighted combination of feature maps + ReLU
  5. Upsample to input resolution (224×224)
  6. Overlay with colormap (jet/hot)

### 8.6 Technology Acceptance Model (TAM)

- Davis (1989): Technology adoption driven by perceived usefulness + perceived ease of use
- In medical AI: explainability (Grad-CAM) increases perceived usefulness; mobile UI increases ease of use
- Reference: Holden & Karsh (2010)

### 8.7 Design Science Research (DSR) Paradigm

- Hevner et al. (2004) — MIS Quarterly
- Appropriate for IT artifact creation solving real-world problems
- **Three cycles:** Relevance (healthcare context → requirements), Rigor (existing knowledge base), Design (iterative build + evaluate)

---

## 9. Related Work and Existing Systems

### 9.1 Comparison Matrix

| Feature | BoneView (Gleamer) | FractureDetect Mobile | MURA Competition Models | **This Project** |
|---------|-------------------|----------------------|------------------------|-----------------|
| Mobile Deployment | No | Yes | No | **Yes** |
| Offline Functionality | Partial | Yes | No | **Yes** |
| Multi-Bone Detection | Yes | No | Yes | **Yes** |
| Fracture Type Classification | No | No | No | **Yes** |
| Heat Map Visualization | No | No | Limited | **Yes (Grad-CAM)** |
| Cost-Effective | No | Yes | N/A | **Yes** |
| Explainable Outputs | Limited | No | No | **Yes** |
| Regulatory Status | FDA/CE Approved | Research | Research | Research |

### 9.2 Gap Analysis

| Gap | Description | How This Project Fills It |
|-----|-------------|--------------------------|
| Gap 1 | No system integrates multi-bone detection + fracture type classification | Hybrid 3-head MobileNetV2 does all three simultaneously |
| Gap 2 | Mobile fracture systems are black boxes | Grad-CAM integrated in mobile pipeline |
| Gap 3 | No offline-capable comprehensive system | Flutter + TFLite; fully offline |
| Gap 4 | Commercial systems cost-prohibitive for developing countries | Open, deployable on commodity Android devices |
| Gap 5 | Explainability gap limits clinical trust | Visual heat maps enable clinician verification |
| Gap 6 | Binary detection dominates; fracture type underrepresented | Three fracture types as classification target |

---

## 10. Technology Stack and Justifications

### 10.1 Programming Languages

| Language | Role | Justification |
|----------|------|---------------|
| Python 3.9+ | ML pipeline | Dominant ML ecosystem (TensorFlow, NumPy, scikit-learn); superior for deep learning |
| Dart 2.19+ | Mobile app | Required by Flutter; type-safe; compiled to native ARM |

### 10.2 ML Frameworks

| Tool | Version | Purpose |
|------|---------|---------|
| TensorFlow | 2.13+ | Primary deep learning framework |
| Keras | 2.13+ | High-level model API |
| TensorFlow Lite | 2.13+ | On-device mobile inference |
| NumPy / Pandas | Latest | Data manipulation |
| scikit-learn | Latest | Evaluation metrics |
| Matplotlib / Plotly | Latest | Visualization |

**Why TensorFlow over PyTorch:** Comprehensive TFLite ecosystem for mobile; production-ready deployment; Keras API; built-in Grad-CAM support.

### 10.3 Architecture Comparison (MobileNetV2 Chosen)

| Architecture | Parameters (M) | Top-1 Accuracy | Mobile Inference | Project Suitability |
|-------------|----------------|----------------|-----------------|---------------------|
| **MobileNetV2** | **3.4** | **72.0%** | **Fast** | **Excellent** |
| ResNet-50 | 25.6 | 76.0% | Slow | Moderate |
| EfficientNet-B0 | 5.3 | 77.1% | Moderate | Good |
| DenseNet-121 | 8.0 | 75.0% | Moderate | Good |

**Justification for MobileNetV2:** Best accuracy-to-parameter ratio for mobile; purpose-built for on-device deployment; proven TFLite compatibility.

### 10.4 Mobile Framework

| Framework | Language | Justification |
|-----------|----------|---------------|
| **Flutter** (chosen) | Dart | Cross-platform (Android primary); compiled to native ARM; Material Design; TFLite plugin support; hot reload |
| React Native | JavaScript | Rejected — potential performance overhead |
| Native Android (Kotlin) | Kotlin | Rejected — limits cross-platform potential |

### 10.5 Explainability Tool

| Technique | Chosen? | Reason |
|-----------|---------|--------|
| **Grad-CAM** | Yes | Model-agnostic; no retraining; computationally efficient; clinically intuitive; produces visual heat maps |
| LIME | No | Computationally expensive for real-time use |
| SHAP | No | Significant computation; not optimized for images |
| Saliency Maps | No | Often noisy and less interpretable |

### 10.6 TensorFlow Lite Optimization

- **FP16 quantization** — balanced accuracy and performance (default)
- **INT8 quantization** — further optimization if needed
- **Quantization-aware training** — used if accuracy loss > 2%
- Hardware acceleration: GPU/NPU delegation where available

### 10.7 Development Environment

| Tool | Purpose |
|------|---------|
| Jupyter Notebook | EDA, model development, visualization |
| VS Code | Python code editor |
| Android Studio | Mobile development, emulation, debugging |
| Git | Version control |

---

## 11. Research Methodology

### 11.1 Research Paradigm

- **Design Science Research (DSR)** — Hevner et al. (2004)
- Relevance Cycle → Rigor Cycle → Design Cycle

### 11.2 Approach

- **Mixed methods:**
  - Quantitative: accuracy, precision, recall, F1, latency measurements, localization accuracy
  - Qualitative: literature thematic analysis, heat map expert review, UX assessment

### 11.3 Development Methodology

- **Agile** with 4 sprints over 16 weeks
- Sprint 1 (Weeks 1–4): Literature, data acquisition, environment setup
- Sprint 2 (Weeks 5–8): Model development, training, Grad-CAM
- Sprint 3 (Weeks 9–12): TFLite conversion, Flutter app, integration testing
- Sprint 4 (Weeks 13–16): Evaluation, user testing, documentation

---

## 12. Data Sources and Preprocessing

### 12.1 Datasets

**MURA (Musculoskeletal Radiographs) — Stanford ML Group (2018)**

| Field | Detail |
|-------|--------|
| Total images | 40,561 multi-view X-ray images |
| Studies | 14,863 |
| Anatomical regions | Shoulder, elbow, forearm, hand, wrist, humerus, finger |
| Labels | Body part; binary label (normal/abnormal) |
| Format | JPEG + JSON metadata |
| Use in project | Body part classification; fracture detection |

**FracAtlas — Hardalaç et al. (2022)**

| Field | Detail |
|-------|--------|
| Total images | 4,083 X-ray images |
| Labels | Fracture presence + fracture type (simple, comminuted, greenstick) |
| Annotations | PASCAL VOC XML + COCO JSON (bounding boxes/masks) |
| Use in project | Fracture type classification |

### 12.2 Dataset Integration

**Unified schema:**

| Field | MURA Mapping | FracAtlas Mapping |
|-------|-------------|-------------------|
| Image ID | Study ID + image number | Image filename |
| Body Part | `body_part` field | Derived from metadata |
| Fracture Status | `label` (0/1) | `fracture_presence` (0/1) |
| Fracture Type | Not available (masked as "unknown") | `fracture_type` field |

**Handling missing labels:** MURA images lack fracture type → `fracture_type` set to "unknown" with masked loss during training.

### 12.3 Preprocessing Pipeline

**Stage 1 — Image Standardization:**
- Resize to 224×224 pixels (MobileNetV2 input requirement)
- Maintain aspect ratio with padding
- Convert to RGB (3-channel input)

**Stage 2 — Normalization:**
- Pixel values: integer [0, 255] → float [0, 1]
- Formula: `pixel_float = pixel_int × (1/255)`
- Config: `NORMALIZE_SCALE = 1.0 / 255.0`

**Stage 3 — Label Encoding:**
- Body parts: integer class index (0–6), 7 classes
- Fracture: binary (0 = normal, 1 = fracture)
- Fracture type: integer class index (0 = simple, 1 = comminuted, 2 = greenstick)

**Stage 4 — Data Augmentation (documented in proposal):**

| Augmentation | Parameters | Purpose |
|-------------|-----------|---------|
| Random Rotation | ±15° | Simulate patient positioning variations |
| Random Zoom | ±10% | Simulate distance/magnification variations |
| Random Horizontal Flip | 50% | Account for bilateral symmetry |
| Random Brightness | ±20% | Simulate exposure variations |
| Random Contrast | ±20% | Simulate image quality variations |

**Stage 5 — Dataset Split:**
- Training: 80%
- Validation: 10%
- Test: 10%
- Stratified split maintains distribution of body parts, fracture status, fracture types

### 12.4 Folder Structure

```
ml/data/raw/
├── train/
│   └── {body_part}/
│       ├── normal/
│       ├── fracture_simple/
│       ├── fracture_comminuted/
│       └── fracture_greenstick/
├── valid/  (same structure)
└── test/   (same structure)
```

---

## 13. Model Architecture (Implementation)

### 13.1 Architecture Overview

The model is a **multi-task hybrid MobileNetV2** with three output heads sharing a single CNN backbone.

**File:** [ml/models/hybrid_model.py](ml/models/hybrid_model.py)

```
Input (224×224×3)
    ↓
MobileNetV2 (ImageNet pretrained, top 30 layers fine-tuned)
    ↓
Global Average Pooling (pooling='avg' in base)
    ↓
Dropout(0.3)
    ↓
┌─────────────────────┬──────────────────────┬─────────────────────────┐
│   HEAD 1            │   HEAD 2             │   HEAD 3                │
│   Body Part         │   Fracture           │   Fracture Type         │
│   Dense(7, softmax) │   Dense(1, sigmoid)  │   Dense(3, softmax)     │
│   name='body_part'  │   name='fracture'    │   name='fracture_type'  │
│   7 classes         │   binary             │   3 classes             │
└─────────────────────┴──────────────────────┴─────────────────────────┘
```

### 13.2 Configuration (config.py)

```python
IMG_SIZE = 224                    # Input image size
NORMALIZE_SCALE = 1.0 / 255.0    # Normalization factor
TRAIN_RATIO, VAL_RATIO, TEST_RATIO = 0.8, 0.1, 0.1
BODY_PARTS = ["elbow", "finger", "forearm", "hand", "humerus", "shoulder", "wrist"]  # 7 classes
FRACTURE_TYPES = ["simple", "comminuted", "greenstick"]                               # 3 classes
MODEL_INPUT_SHAPE = (224, 224, 3)
BATCH_SIZE = 32
EPOCHS = 20
```

### 13.3 Model Compilation

```python
optimizer: Adam(learning_rate=1e-4)
loss = {
    "body_part":     sparse_categorical_crossentropy,
    "fracture":      binary_crossentropy,
    "fracture_type": sparse_categorical_crossentropy,
}
loss_weights = {"body_part": 1.0, "fracture": 1.5, "fracture_type": 1.0}
```

**Loss weighting rationale:** Fracture detection (binary task) is most clinically critical, hence weight 1.5.

### 13.4 Training Strategy

**Transfer Learning Phase:**
- Freeze MobileNetV2 base layers (all except last 30)
- Train classification heads only
- Adam optimizer, lr=1e-4, batch size=32, epochs=20
- Early stopping (patience=5) on validation loss
- ModelCheckpoint to `ml/checkpoints/bone_fracture_model.keras`

**Fine-Tuning Phase (after initial convergence):**
- Unfreeze top ~30% of MobileNetV2 layers
- Reduce learning rate to 0.0001
- Monitor validation loss; early stopping

### 13.5 Class Imbalance Handling

- **Weighted loss:** Class weights computed from inverse frequency
- **Focal loss** (Lin et al., 2017): Considered for fracture detection branch to focus training on hard examples
- **Oversampling:** Minority classes (fracture images, specific fracture types) oversampled per batch

### 13.6 Multi-Task Loss Function

```
L_total = α·L_body + β·L_fracture + γ·L_type
```
Where:
- α = 1.0 (body part categorical cross-entropy)
- β = 1.5 (fracture binary cross-entropy)
- γ = 1.0 (fracture type categorical cross-entropy)

### 13.7 Regularization

- Dropout(0.3) after backbone
- L2 weight regularization (λ = 0.001) — documented in proposal
- Early stopping on validation loss
- Data augmentation
- Batch normalization (inherent in MobileNetV2)

---

## 14. Grad-CAM Implementation

**File:** [ml/grad_cam.py](ml/grad_cam.py)

### 14.1 Algorithm (Python Implementation)

```python
def make_gradcam_heatmap(model, img_array, pred_index=None, layer_name=None):
    # 1. Find last 4D conv layer (last convolutional layer in MobileNetV2)
    # 2. Build gradient model: input → target_layer → fracture output
    # 3. Forward pass to get conv_output and fracture prediction
    # 4. Compute gradient of fracture score w.r.t. feature maps
    # 5. Global average pool gradients → importance weights
    # 6. Weighted combination of feature maps + ReLU
    # 7. Normalize to [0,1]
    # Returns heatmap as numpy array
```

**Key implementation details:**
- Targets the `fracture` output head for gradient computation
- Uses `tf.GradientTape` for gradient computation
- Normalizes heatmap: `heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-8)`
- Overlay uses OpenCV `COLORMAP_JET`; alpha blending at 0.4

### 14.2 Mobile App Heat Map (Flutter)

**Status:** Visual overlay approximation (not full on-device Grad-CAM).

In [mobile/lib/screens/result_screen.dart](mobile/lib/screens/result_screen.dart):
- When `result.hasFracture == true`: gradient overlay (transparent → red, 35% opacity) applied over X-ray image
- Disclaimer text: *"Heat map highlights the region of interest. For full Grad-CAM, use the desktop ML pipeline."*

**Full Grad-CAM path:** Available only in Python ML pipeline (`ml/grad_cam.py`). On-device TFLite Grad-CAM is architecturally planned but not yet implemented.

---

## 15. Mobile Application (Implementation)

### 15.1 App Identity

| Property | Value |
|----------|-------|
| Package name | `bone_fracture_app` |
| App title | "Smarter Health Better You" |
| Version | 1.0.0+1 |
| Platform | Android (primary); also runs on Windows/web for dev |
| SDK | Dart ≥ 3.0.0, Flutter ≥ 3.10 |

### 15.2 Dependencies

```yaml
tflite_flutter: ^0.10.4    # On-device TFLite inference
image_picker: ^0.8.7       # Camera + gallery image acquisition
image: ^4.0.17             # Image decoding + resizing
path_provider: ^2.1.2      # File system paths (history storage)
google_fonts: ^6.2.1       # Typography
```

### 15.3 Architecture (Clean Architecture Pattern)

```
Presentation Layer  →  Flutter UI (Screens + Widgets)
Application Layer   →  Use Cases / Business Logic
Domain Layer        →  Entities, Repository Interfaces
Data Layer          →  TFLite Model + SQLite/JSON + File Storage
```

### 15.4 Screens

| Screen | File | Description |
|--------|------|-------------|
| Splash Screen | `screens/splash_screen.dart` | App launch / loading |
| Home Screen | `screens/home_screen.dart` | Hero section, model status, quick actions |
| Result Screen | `screens/result_screen.dart` | X-ray image + results + heat map overlay |
| History Screen | `screens/history_screen.dart` | Past analyses list |
| App Shell | `screens/app_shell.dart` | Navigation shell |

### 15.5 Key Services

**InferenceService** ([mobile/lib/services/inference_service_io.dart](mobile/lib/services/inference_service_io.dart)):
- Loads `assets/bone_fracture.tflite`
- Image preprocessing: decode → resize to 224×224 → normalize [0,1] → Float32List
- Runs multi-output inference: body part (7), fracture (1), fracture type (3)
- Confidence thresholds: body part ≥ 0.5, fracture ≥ 0.5
- Returns `InferenceResult` with `bodyPartName`, `hasFracture`, `fractureConfidence`, `fractureTypeName`

**HistoryService** ([mobile/lib/services/history_service_io.dart](mobile/lib/services/history_service_io.dart)):
- File-based storage (Android/iOS/Windows)
- Saves analysis images to `{documents}/bone_fracture_app/images/`
- History index: `{documents}/bone_fracture_app/history.json`
- Operations: `getEntries()`, `saveEntry()`, `deleteEntry()`

### 15.6 User Flow

```
Launch App → Splash → Home Screen
    ↓
[Capture X-ray (camera)]  |  [Choose from Gallery]  |  [View History]
    ↓                               ↓                         ↓
Image acquired → runInference() → Processing → ResultScreen
    ↓
[Body part] + [Fracture: Yes/No + Confidence%] + [Fracture Type] + [Heat map overlay]
    ↓
[Save to history] | [Share (copy to clipboard)] | [New Analysis]
```

### 15.7 TFLite Model Integration

**Conversion pipeline** (from `ml/export_tflite.py`):
1. Load trained Keras model from `ml/checkpoints/bone_fracture_model.keras`
2. Convert with `TFLiteConverter.from_keras_model()`
3. Apply FP16 quantization: `converter.target_spec.supported_types = [tf.float16]`
4. Output: `ml/export/bone_fracture.tflite`
5. Copy to `mobile/assets/bone_fracture.tflite`

**Model asset:** Declared in `pubspec.yaml` under `flutter.assets`.

### 15.8 Offline Capability

- All inference runs on-device via TFLite interpreter
- No network requests during analysis
- History stored in local JSON file (not cloud)
- Images stored in app documents directory
- Share feature copies text to clipboard (no internet needed)

### 15.9 Disclaimer Implementation

**DisclaimerBanner** widget ([mobile/lib/widgets/disclaimer_banner.dart](mobile/lib/widgets/disclaimer_banner.dart)) — shown on Home and Result screens:

> "This app is for educational and decision support only. It is not a replacement for professional medical diagnosis. Always seek a qualified healthcare professional for final diagnosis and treatment. Do not rely on this app for self-diagnosis or treatment without clinical consultation."

---

## 16. Evaluation Framework

### 16.1 Classification Metrics (per Task)

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| Accuracy | (TP+TN)/(TP+TN+FP+FN) | Overall correctness |
| Precision | TP/(TP+FP) | Proportion of positive predictions correct |
| Recall (Sensitivity) | TP/(TP+FN) | Proportion of actual positives correctly identified |
| F1-Score | 2×(P×R)/(P+R) | Harmonic mean of precision and recall |
| AUC-ROC | Area under ROC curve | Discrimination ability across thresholds |

**Applied to 3 tasks:**
- Body part identification (7-class; macro-averaged)
- Fracture detection (binary)
- Fracture type classification (3-class; macro-averaged)

**Implementation** ([ml/evaluate.py](ml/evaluate.py)):
```python
def evaluate_metrics(y_true, y_pred, task='binary'):
    # binary: threshold at 0.5
    # multiclass: argmax
    # Returns: {accuracy, precision, recall, f1} via sklearn
```

### 16.2 Grad-CAM Evaluation

| Method | Description |
|--------|-------------|
| **Qualitative** | Domain experts (radiologists) rate heat map relevance on Likert scale (1–5) |
| **Localization accuracy** | % of heat map highlighting actual fracture region (where ground truth available) |
| **IoU** | Intersection over Union between heat map threshold and ground truth fracture mask |

### 16.3 System Performance Targets

| Metric | Target |
|--------|--------|
| Inference time | < 2 seconds |
| Model size | < 50 MB |
| Memory usage | < 200 MB peak |
| Battery impact | < 5% per 10 analyses |

### 16.4 User Evaluation

**Target population:** 20–30 participants:
- Final-year medical students (radiology rotation experience)
- Junior doctors
- Experienced clinicians (expert validation sample)

**Instruments:**
- **System Usability Scale (SUS):** 10-item questionnaire; score 0–100; benchmark > 68 = above average
- **Custom satisfaction questionnaire:** ease of use, usefulness, heat map trust, willingness to use
- **Task completion metrics:** success rate, time to analysis, error count

### 16.5 Comparative Evaluation

| Baseline | Purpose |
|----------|---------|
| Single-task MobileNetV2 (separate models) | Demonstrate multi-task advantage |
| ResNet-50 | Accuracy benchmark comparison |
| Published MURA literature results | Position against state-of-the-art |
| FractureDetect Mobile (Li et al., 2021) | Conceptual feature comparison |

---

## 17. Implementation Status vs. Requirements

### Fully Implemented ✅

| Requirement | Implementation |
|-------------|----------------|
| Fracture detection across multiple bones | `ml/models/hybrid_model.py`: 7 body parts + fracture detection |
| Fracture type classification | 3-class head (`fracture_type`) |
| Body part identification | 7-class head (`body_part`) |
| MobileNetV2 base | `keras.applications.MobileNetV2(weights="imagenet")` |
| Grad-CAM (Python) | `ml/grad_cam.py`: `make_gradcam_heatmap()` |
| TFLite export | `ml/export_tflite.py` |
| Flutter mobile app | `mobile/` |
| Offline inference | TFLite on-device; no network |
| Image capture (camera + gallery) | `image_picker` plugin |
| 224×224 preprocessing | `config.IMG_SIZE=224`; both Python and Flutter |
| [0,1] normalization | `NORMALIZE_SCALE=1/255`; both pipelines |
| 80/10/10 split | `config.py`; `prepare_datasets.py` |
| Evaluation metrics | `ml/evaluate.py`: accuracy, precision, recall, F1 |
| History (save + review) | `HistoryService` + `HistoryScreen` |
| In-app disclaimer | `DisclaimerBanner` on Home + Result screens |
| Save & Share | `_saveToHistory()` and `_share()` (clipboard) |

### Partially Implemented ⚠️

| Requirement | Status |
|-------------|--------|
| Grad-CAM in mobile app | Visual gradient overlay only; full on-device Grad-CAM not implemented |
| ImageNet mean/std normalization | [0,1] only; ImageNet (mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225]) not applied |
| Data augmentation | Documented in proposal; not yet implemented in `dataset.py`/`train.py` |

---

## 18. Ethical Considerations

### 18.1 Data Privacy

- MURA and FracAtlas are publicly released for research; de-identified by creators
- No patient-identifiable information used
- Dataset terms of use strictly followed
- All data processing on local development machines
- Mobile app: all data stored locally; no cloud upload
- User can delete analysis history

### 18.2 Medical Disclaimer (doc 3.10.2)

Implemented as `DisclaimerBanner` widget:
> "This app is for educational and decision support only. It is not a replacement for professional medical diagnosis. Always seek a qualified healthcare professional for final diagnosis and treatment."

Additional notes:
- Model accuracy is not 100%
- System may miss some fractures (false negatives possible)
- False positives possible
- Not validated for all fracture types or patient populations

### 18.3 Institutional Approval

- Approved by UENR Department faculty
- Adherence to UENR research ethics guidelines
- Departmental research committee consulted

### 18.4 Bias Mitigation

| Concern | Approach |
|---------|----------|
| Demographic limitations of public datasets | Acknowledged; discuss potential performance variation across populations |
| Algorithmic fairness | Per-class metrics reported; performance disparities across body parts evaluated |
| Unknown populations | Recommendation for local validation before clinical deployment |

---

## 19. Project Timeline

**Total duration:** 16 weeks; Agile methodology with 4 sprints

| Sprint | Weeks | Key Activities | Deliverables |
|--------|-------|----------------|--------------|
| 1 — Foundation | 1–4 | Literature review; dataset acquisition; data preprocessing; environment setup | Preprocessed datasets; model architecture spec; dev environment docs |
| 2 — Model Development | 5–8 | Multi-task model implementation; initial training; hyperparameter tuning; Grad-CAM | Trained model; Grad-CAM working; checkpoints |
| 3 — Mobile Development | 9–12 | TFLite conversion; Flutter app; UI/UX; integration testing | Working mobile app; TFLite integrated; basic functionality complete |
| 4 — Evaluation & Docs | 13–16 | Comprehensive evaluation; user testing; bug fixes; documentation | Evaluation results; final report; presentation materials |

---

## 20. References

Abadi, M., et al. (2016). TensorFlow: A system for large-scale machine learning. *12th USENIX Symposium on Operating Systems Design and Implementation*, 265–283.

Bushberg, J. T., Seibert, J. A., Leidholdt, E. M., & Boone, J. M. (2020). *The essential physics of medical imaging* (4th ed.). Lippincott Williams & Wilkins.

Davis, F. D. (1989). Perceived usefulness, perceived ease of use, and user acceptance of information technology. *MIS Quarterly*, 13(3), 319–340.

Esteva, A., et al. (2017). Dermatologist-level classification of skin cancer with deep neural networks. *Nature*, 542(7639), 115–118.

Gulshan, V., et al. (2016). Development and validation of a deep learning algorithm for detection of diabetic retinopathy in retinal fundus photographs. *JAMA*, 316(22), 2402–2410.

Hardalaç, F., Uysal, F., Peker, O., et al. (2022). FracAtlas: A dataset for fracture classification, localization and pattern recognition. *Scientific Data*, 9(1), 1–10.

Hevner, A. R., March, S. T., Park, J., & Ram, S. (2004). Design science in information systems research. *MIS Quarterly*, 28(1), 75–105.

Holden, R. J., & Karsh, B. T. (2010). The technology acceptance model: Its past and its future in health care. *Journal of Biomedical Informatics*, 43(1), 159–172.

Kelly, C. J., et al. (2019). Key challenges for delivering clinical impact with artificial intelligence. *BMC Medicine*, 17(1), 1–9.

LeCun, Y., Bengio, Y., & Hinton, G. (2015). Deep learning. *Nature*, 521(7553), 436–444.

Lewis, P., et al. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *Advances in Neural Information Processing Systems*, 33, 9459–9474.

Li, J., Zhang, Y., & Huang, T. (2021). Offline mobile fracture detection using lightweight deep learning models. *Healthcare AI*, 8(3), 112–124.

Lin, T. Y., Goyal, P., Girshick, R., He, K., & Dollár, P. (2017). Focal loss for dense object detection. *Proceedings of the IEEE ICCV*, 2980–2988.

Lindsey, R., et al. (2018). Deep neural network improves fracture detection by clinicians. *Proceedings of the National Academy of Sciences*, 115(45), 11591–11596.

Oberije, C., Meinders, J., & Lambin, P. (2020). Multi-task learning for simultaneous body part classification and fracture detection on musculoskeletal radiographs. *Medical Image Analysis*, 65, 101774.

Olczak, J., et al. (2017). Artificial intelligence for analyzing orthopedic trauma radiographs. *Acta Orthopaedica*, 88(6), 581–586.

Park, S. H., & Han, K. (2020). Methodologic guide for evaluating clinical performance and effect of artificial intelligence technology for medical diagnosis and prediction. *Radiology*, 286(3), 800–809.

Rajpurkar, P., et al. (2017). CheXNet: Radiologist-level pneumonia detection on chest X-rays with deep learning. *arXiv preprint arXiv:1711.05225*.

Rajpurkar, P., et al. (2018). MURA: Large dataset for abnormality detection in musculoskeletal radiographs. *arXiv preprint arXiv:1712.06957*.

Raschka, S., Patterson, J., & Nolet, C. (2020). Machine learning in Python: Main developments and technology trends. *Information*, 11(4), 193.

Sandler, M., Howard, A., Zhu, M., Zhmoginov, A., & Chen, L. C. (2018). MobileNetV2: Inverted residuals and linear bottlenecks. *Proceedings of the IEEE CVPR*, 4510–4520.

Selvaraju, R. R., et al. (2019). Grad-CAM: Visual explanations from deep networks via gradient-based localization. *International Journal of Computer Vision*, 128(2), 336–359.

Su, Z., Wang, Z., & Li, S. (2023). Deep learning for skeletal fracture detection: A systematic review. *Diagnostics*, 13(4), 567–589.

Tajbakhsh, N., et al. (2016). Convolutional neural networks for medical image analysis: Full training or fine tuning? *IEEE Transactions on Medical Imaging*, 35(5), 1299–1312.

Wang, Y., Zhang, L., & Liu, M. (2022). Automated fracture detection in wrist X-rays using deep learning: A multi-center study. *European Radiology*, 32(3), 1892–1901.

Whitley, A. S., et al. (2015). *Clark's positioning in radiography* (13th ed.). CRC Press.

World Health Organization. (2021). *Musculoskeletal conditions*. WHO Fact Sheets.

Yosinski, J., Clune, J., Bengio, Y., & Lipson, H. (2014). How transferable are features in deep neural networks? *Advances in Neural Information Processing Systems*, 27, 3320–3328.

Zhou, B., et al. (2022). Explainable machine learning for medical image analysis: A review. *Pattern Recognition Letters*, 155, 78–87.

---

*Document compiled from: `doc_extracted.txt` (Chapters 1–3 of original proposal), `IMPLEMENTATION_CHECKLIST.md`, `README.md`, and all source code in `ml/` and `mobile/lib/`.*
