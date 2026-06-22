"""Generate a polished Word document summarizing the Gloria bone fracture detection project."""

from __future__ import annotations

import json
import zipfile
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "Gloria_Project_Technical_Documentation.docx"
HISTORY_PATH = ROOT / "ml" / "checkpoints" / "training_history.json"


def load_training_history() -> dict | None:
    if not HISTORY_PATH.exists():
        return None
    return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))


def best_epoch_metrics(history: dict) -> dict:
    """Pick checkpoint epoch by highest validation fracture accuracy."""
    val_frac = history.get("val_fracture_accuracy", [])
    if not val_frac:
        return {}
    best_idx = max(range(len(val_frac)), key=lambda i: val_frac[i])
    epoch = best_idx + 1

    def pct(key: str) -> str:
        vals = history.get(key, [])
        if best_idx >= len(vals):
            return "N/A"
        return f"{vals[best_idx] * 100:.2f}%"

    def pct_at(key: str, idx: int) -> str:
        vals = history.get(key, [])
        if idx >= len(vals):
            return "N/A"
        return f"{vals[idx] * 100:.2f}%"

    last = len(val_frac) - 1
    return {
        "best_epoch": epoch,
        "epochs_trained": len(val_frac),
        "best_val_fracture": pct("val_fracture_accuracy"),
        "best_val_body": pct("val_body_part_accuracy"),
        "best_val_type": pct("val_fracture_type_accuracy"),
        "train_body_at_best": pct("body_part_accuracy"),
        "train_fracture_at_best": pct("fracture_accuracy"),
        "train_type_at_best": pct("fracture_type_accuracy"),
        "final_train_body": pct_at("body_part_accuracy", last),
        "final_train_fracture": pct_at("fracture_accuracy", last),
        "final_train_type": pct_at("fracture_type_accuracy", last),
        "final_val_fracture": pct_at("val_fracture_accuracy", last),
    }


def paragraph(text: str, style: str = "Normal") -> str:
    return (
        f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr>'
        f'<w:r><w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>'
    )


def heading(text: str, level: int) -> str:
    return paragraph(text, f"Heading{level}")


def bullet(text: str) -> str:
    return (
        "<w:p><w:pPr><w:pStyle w:val=\"ListParagraph\"/>"
        "<w:numPr><w:ilvl w:val=\"0\"/><w:numId w:val=\"1\"/></w:numPr></w:pPr>"
        f"<w:r><w:t xml:space=\"preserve\">{escape(text)}</w:t></w:r></w:p>"
    )


def table_row(cells: list[str], header: bool = False) -> str:
    row = "<w:tr>"
    for cell in cells:
        tag = "w:tc"
        inner = (
            f"<{tag}><w:p><w:r><w:rPr>"
            + ("<w:b/>" if header else "")
            + f"</w:rPr><w:t xml:space=\"preserve\">{escape(cell)}</w:t></w:r></w:p></{tag}>"
        )
        row += inner
    row += "</w:tr>"
    return row


def table(rows: list[list[str]], header: bool = True) -> str:
    body = "".join(
        table_row(row, header=(header and i == 0)) for i, row in enumerate(rows)
    )
    return (
        "<w:tbl><w:tblPr><w:tblW w:w=\"5000\" w:type=\"pct\"/>"
        "<w:tblBorders>"
        "<w:top w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
        "<w:left w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
        "<w:bottom w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
        "<w:right w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
        "<w:insideH w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
        "<w:insideV w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
        "</w:tblBorders></w:tblPr>" + body + "</w:tbl>"
    )


def build_document_body(metrics: dict) -> str:
    today = date.today().strftime("%B %d, %Y")
    parts: list[str] = []

    parts.append(heading("Mobile-Based Machine Learning System for Bone Fracture Detection", 1))
    parts.append(paragraph("Technical Project Documentation"))
    parts.append(paragraph(f"Prepared: {today}"))
    parts.append(paragraph(
        "Institution: Department of Information Technology and Decision Sciences, "
        "University of Energy and Natural Resources (UENR), Sunyani, Ghana"
    ))
    parts.append(paragraph(
        "Application: Smarter Health Better You (bone_fracture_app) — Version 1.0.0+1"
    ))

    parts.append(heading("1. Executive Summary", 1))
    parts.append(paragraph(
        "This project delivers an offline-capable mobile system that analyzes musculoskeletal "
        "X-ray images to identify the affected body part, detect fractures, classify fracture "
        "type, and visualize regions of interest using Grad-CAM heat maps. The solution combines "
        "a multi-task MobileNetV2 deep learning model (Python/TensorFlow), TensorFlow Lite "
        "deployment, and a Flutter Android application for use in low-resource healthcare settings."
    ))

    parts.append(heading("2. Dataset Overview", 1))
    parts.append(heading("2.1 Source Datasets", 2))
    parts.append(table([
        ["Dataset", "Source", "Size", "Labels Provided", "Role in Project"],
        [
            "MURA (Musculoskeletal Radiographs)",
            "Stanford ML Group (2018)",
            "40,561 X-ray images from 14,863 studies",
            "7 body parts; binary normal/abnormal",
            "Multi-bone coverage and fracture presence",
        ],
        [
            "FracAtlas",
            "Hardalaç et al. (2022)",
            "4,083 annotated X-ray images",
            "Fracture presence and fracture type",
            "Fracture type labels (simple, comminuted, greenstick)",
        ],
    ]))

    parts.append(heading("2.2 Classification Tasks and Classes", 2))
    parts.append(paragraph("The model performs three concurrent classification tasks:"))
    parts.append(bullet(
        "Body part identification — 7 classes: elbow, finger, forearm, hand, humerus, shoulder, wrist"
    ))
    parts.append(bullet(
        "Fracture detection — binary: normal (0) vs. fracture present (1)"
    ))
    parts.append(bullet(
        "Fracture type classification — 3 classes: simple, comminuted, greenstick "
        "(MURA abnormal cases mapped to fracture_unlabeled when type is unknown)"
    ))

    parts.append(heading("2.3 Image Dimensions and Preprocessing", 2))
    parts.append(table([
        ["Parameter", "Value", "Notes"],
        ["Input shape", "224 × 224 × 3", "RGB channels required by MobileNetV2"],
        ["Resize method", "224×224 resize", "Applied in Python (PIL) and Flutter mobile pipeline"],
        ["Color format", "RGB", "Converted from grayscale or other formats"],
        ["Normalization", "[0, 1] scaling", "Pixel values divided by 255.0"],
        ["Train / Valid / Test split", "80% / 10% / 10%", "Stratified by body part and label where possible"],
        ["Batch size", "32", "Configured in ml/config.py"],
    ]))

    parts.append(heading("2.4 Prepared Project Data (Current Repository)", 2))
    parts.append(table([
        ["Split", "Total Images", "Body Parts Present", "Label Distribution (summary)"],
        [
            "Training",
            "32,146",
            "elbow, finger, forearm, hand",
            "normal: 10,007 | fracture_simple: 12,708 | fracture_unlabeled: 9,431",
        ],
        [
            "Validation",
            "0 (folder not populated)",
            "—",
            "Validation split should be regenerated via prepare_datasets.py",
        ],
        [
            "Test",
            "3,551",
            "All 7 body parts",
            "normal: 856 | fracture_simple: 1,548 | fracture_unlabeled: 1,147",
        ],
    ]))
    parts.append(paragraph(
        "Note: An earlier prepared subset contained 3,271 training, 411 validation, and 401 test "
        "images (FracAtlas-focused). The model checkpoint on disk was produced from a 6-epoch training "
        "run using validation data at that time."
    ))

    parts.append(heading("2.5 Folder Structure for ML Training", 2))
    parts.append(paragraph(
        "Images are organized as: ml/data/raw/{train|valid|test}/{body_part}/{label}/image.jpg "
        "where label is one of: normal, fracture_simple, fracture_comminuted, fracture_greenstick, "
        "or fracture_unlabeled."
    ))

    parts.append(heading("3. Machine Learning Model", 1))
    parts.append(heading("3.1 Architecture", 2))
    parts.append(table([
        ["Component", "Specification"],
        ["Base network", "MobileNetV2 (ImageNet pretrained weights)"],
        ["Pooling", "Global average pooling on backbone output"],
        ["Regularization", "Dropout (0.3) on shared features"],
        ["Head A — body_part", "Dense(7) + Softmax — 7-class anatomy classification"],
        ["Head B — fracture", "Dense(1) + Sigmoid — binary fracture detection"],
        ["Head C — fracture_type", "Dense(3) + Softmax — simple / comminuted / greenstick"],
        ["Optimizer", "Adam (learning rate 1×10⁻⁴)"],
        ["Loss functions", "Sparse categorical cross-entropy (body & type); binary cross-entropy (fracture)"],
        ["Loss weights", "body_part: 1.0 | fracture: 1.5 | fracture_type: 1.0"],
        ["Fine-tuning", "Last ~30 MobileNetV2 layers trainable; earlier layers frozen"],
    ]))

    parts.append(heading("3.2 Training Configuration", 2))
    parts.append(table([
        ["Setting", "Value"],
        ["Maximum epochs", "20 (default; early stopping patience = 5)"],
        ["Epochs completed (saved run)", str(metrics.get("epochs_trained", "N/A"))],
        ["Checkpoint monitor", "Validation fracture accuracy (maximize)"],
        ["Saved model", "ml/checkpoints/bone_fracture_model.keras (~22 MB)"],
        ["Mobile export", "ml/export/bone_fracture.tflite (FP16 optimized)"],
    ]))

    parts.append(heading("3.3 Model Performance and Accuracy", 2))
    if metrics:
        parts.append(paragraph(
            f"The trained model completed {metrics['epochs_trained']} epochs. The best checkpoint "
            f"(selected by highest validation fracture accuracy) occurred at epoch "
            f"{metrics['best_epoch']}."
        ))
        parts.append(table([
            ["Metric", "Training Set (at best epoch)", "Validation Set (at best epoch)"],
            ["Body part accuracy", metrics["train_body_at_best"], metrics["best_val_body"]],
            ["Fracture detection accuracy", metrics["train_fracture_at_best"], metrics["best_val_fracture"]],
            ["Fracture type accuracy", metrics["train_type_at_best"], metrics["best_val_type"]],
        ]))
        parts.append(paragraph("Final epoch training metrics (last epoch of saved run):"))
        parts.append(table([
            ["Metric", "Training Accuracy", "Validation Accuracy"],
            ["Body part", metrics["final_train_body"], metrics.get("best_val_body", "N/A")],
            ["Fracture detection", metrics["final_train_fracture"], metrics["final_val_fracture"]],
            ["Fracture type", metrics["final_train_type"], "See training log"],
        ]))
        parts.append(paragraph(
            "Primary reported accuracy for fracture detection on the held-out validation set at the "
            f"best checkpoint: {metrics['best_val_fracture']}. Training fracture accuracy at the same "
            f"epoch: {metrics['train_fracture_at_best']}. Full test-set metrics (accuracy, precision, "
            "recall, F1-score per task) can be reproduced by running: "
            "python ml/evaluate.py --model ml/checkpoints/bone_fracture_model.keras"
        ))
    else:
        parts.append(paragraph(
            "No training_history.json was found. Run training and evaluation to populate metrics."
        ))

    parts.append(heading("3.4 Explainability — Grad-CAM", 2))
    parts.append(paragraph(
        "Grad-CAM (Gradient-weighted Class Activation Mapping) is implemented in ml/grad_cam.py. "
        "It computes gradients of the fracture prediction with respect to the last convolutional "
        "feature maps of MobileNetV2, producing a heat map overlaid on the 224×224 input. "
        "The mobile app provides a visual overlay on the result screen; full on-device Grad-CAM "
        "is available through the Python pipeline."
    ))

    parts.append(heading("4. Technology Stack", 1))
    parts.append(heading("4.1 Machine Learning Pipeline", 2))
    parts.append(table([
        ["Technology", "Version / Package", "Purpose", "Why It Was Chosen"],
        [
            "Python",
            "3.10–3.11 recommended",
            "Model development and data pipeline",
            "Dominant ML ecosystem; required by TensorFlow",
        ],
        [
            "TensorFlow / Keras",
            "≥ 2.10",
            "Build, train, and export models",
            "Industry-standard DL framework with TFLite conversion support",
        ],
        [
            "MobileNetV2",
            "ImageNet pretrained",
            "Feature extraction backbone",
            "Low compute cost; proven mobile deployment; ~72% ImageNet top-1 accuracy",
        ],
        [
            "scikit-learn",
            "≥ 1.0",
            "Evaluation metrics",
            "Standard accuracy, precision, recall, F1 implementation",
        ],
        [
            "NumPy, Pandas, Pillow",
            "Latest stable",
            "Arrays, tabular data, image I/O",
            "Efficient numerical and image preprocessing",
        ],
        [
            "OpenCV (headless)",
            "≥ 4.5",
            "Heat map overlay visualization",
            "Fast colormap and image blending for Grad-CAM",
        ],
        [
            "TensorFlow Lite",
            "Bundled with TF",
            "On-device inference",
            "Quantized (FP16) export for offline mobile use with minimal size/speed trade-off",
        ],
    ]))

    parts.append(heading("4.2 Mobile Application", 2))
    parts.append(table([
        ["Technology", "Package / Version", "Purpose", "Why It Was Chosen"],
        [
            "Flutter",
            "SDK ≥ 3.0",
            "Cross-platform UI (Android target)",
            "Single codebase; strong performance; widely used for healthcare apps",
        ],
        [
            "Dart",
            "2.19+",
            "Application logic",
            "Native Flutter language; type-safe UI code",
        ],
        [
            "tflite_flutter",
            "^0.10.4",
            "Load and run TFLite model",
            "Direct on-device inference without network dependency",
        ],
        [
            "image_picker",
            "^0.8.7",
            "Camera and gallery capture",
            "Standard way to acquire X-ray photos on Android",
        ],
        [
            "image",
            "^4.0.17",
            "Decode, resize, normalize to 224×224",
            "Pure Dart image processing aligned with training pipeline",
        ],
        [
            "path_provider",
            "^2.1.2",
            "Local file storage",
            "Persist analysis history on device",
        ],
        [
            "google_fonts",
            "^6.2.1",
            "Typography",
            "Professional, accessible UI styling",
        ],
    ]))

    parts.append(heading("4.3 Development and Deployment Tools", 2))
    parts.append(bullet("Git — version control for ml/ and mobile/ codebases"))
    parts.append(bullet("VS Code / Android Studio — development and device testing"))
    parts.append(bullet("PowerShell scripts (ml/run_train.ps1) — automated training workflow on Windows"))

    parts.append(heading("5. Mobile Application Features", 1))
    parts.append(bullet("Offline X-ray analysis via TensorFlow Lite (no internet required)"))
    parts.append(bullet("Image input from camera or gallery (max 1600×1600, JPEG quality 92%)"))
    parts.append(bullet("Outputs: body part name, fracture yes/no with confidence, fracture type"))
    parts.append(bullet("Anatomy confidence gating to reduce false positives on non-X-ray images"))
    parts.append(bullet("Result screen with heat-map-style visualization when fracture is detected"))
    parts.append(bullet("Analysis history (local storage) and save/share actions"))
    parts.append(bullet("Medical disclaimer banner on home and result screens"))

    parts.append(heading("6. Evaluation Framework", 1))
    parts.append(paragraph(
        "The project evaluates model quality using accuracy, precision, recall, and F1-score "
        "(weighted average for multi-class tasks). Metrics are computed separately for each task: "
        "body part identification, fracture detection, and fracture type classification. "
        "Grad-CAM quality is assessed qualitatively for clinical relevance. System performance "
        "targets include inference under 2 seconds, model size under 50 MB, and peak memory under 200 MB."
    ))

    parts.append(heading("7. Project Structure", 1))
    parts.append(table([
        ["Path", "Description"],
        ["ml/config.py", "Global constants: image size, splits, class names, batch size, epochs"],
        ["ml/data/", "Dataset loaders, MURA/FracAtlas preparation scripts, raw image folders"],
        ["ml/models/hybrid_model.py", "MobileNetV2 multi-task model definition"],
        ["ml/train.py", "Training with early stopping and model checkpointing"],
        ["ml/evaluate.py", "Test-set metric reporting"],
        ["ml/export_tflite.py", "Keras to TFLite conversion (FP16 optimization)"],
        ["ml/grad_cam.py", "Grad-CAM heat map generation and overlay"],
        ["mobile/lib/", "Flutter screens, inference service, history, and UI theme"],
        ["mobile/assets/bone_fracture.tflite", "Deployed model asset for the app"],
    ]))

    parts.append(heading("8. Limitations and Notes", 1))
    parts.append(bullet(
        "Model accuracy is not 100%; the app is for educational and decision support only."
    ))
    parts.append(bullet(
        "ImageNet mean/std normalization and training-time data augmentation are documented "
        "in the thesis proposal but not fully implemented in the current code (uses [0,1] scaling only)."
    ))
    parts.append(bullet(
        "Fracture type classes (comminuted, greenstick) require FracAtlas labels; MURA positives "
        "are stored as fracture_unlabeled when type is unknown."
    ))
    parts.append(bullet(
        "Local validation on Ghanaian patient populations is recommended before any clinical use."
    ))

    parts.append(paragraph("— End of Document —"))
    return "".join(parts)


def create_docx(output_path: Path, body_xml: str) -> None:
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
</Types>"""

    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

    doc_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
</Relationships>"""

    styles = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:spacing w:after="160" w:line="276" w:lineRule="auto"/></w:pPr>
    <w:rPr><w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:basedOn w:val="Normal"/>
    <w:uiPriority w:val="9"/>
    <w:qFormat/>
    <w:pPr><w:spacing w:before="360" w:after="120"/></w:pPr>
    <w:rPr><w:b/><w:sz w:val="32"/><w:szCs w:val="32"/><w:color w:val="1F3864"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:basedOn w:val="Normal"/>
    <w:uiPriority w:val="9"/>
    <w:qFormat/>
    <w:pPr><w:spacing w:before="240" w:after="80"/></w:pPr>
    <w:rPr><w:b/><w:sz w:val="26"/><w:szCs w:val="26"/><w:color w:val="2F5496"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="ListParagraph">
    <w:name w:val="List Paragraph"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr><w:ind w:left="720"/></w:pPr>
  </w:style>
</w:styles>"""

    numbering = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:abstractNum w:abstractNumId="0">
    <w:multiLevelType w:val="hybridMultilevel"/>
    <w:lvl w:ilvl="0">
      <w:start w:val="1"/>
      <w:numFmt w:val="bullet"/>
      <w:lvlText w:val="•"/>
      <w:lvlJc w:val="left"/>
      <w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr>
    </w:lvl>
  </w:abstractNum>
  <w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
</w:numbering>"""

    document = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>{body_xml}<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr></w:body>
</w:document>"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/_rels/document.xml.rels", doc_rels)
        zf.writestr("word/document.xml", document)
        zf.writestr("word/styles.xml", styles)
        zf.writestr("word/numbering.xml", numbering)


def main() -> None:
    history = load_training_history()
    metrics = best_epoch_metrics(history) if history else {}
    body = build_document_body(metrics)
    create_docx(OUTPUT, body)
    print(f"Created: {OUTPUT}")


if __name__ == "__main__":
    main()
