# Data Setup (MURA & FracAtlas-style)

Per proposal: "Collect and prepare X-ray images from public datasets (MURA & FracAtlas)."

## Folder structure

Create the following under `ml/data/raw/`:

```
raw/
  train/
    elbow/
      normal/           <- no fracture
      fracture_simple/
      fracture_comminuted/
      fracture_greenstick/
    finger/
      normal/
      fracture_simple/
      ...
  valid/   (or validation/)
    ...
  test/
    ...
```

## MURA dataset

1. Download MURA from https://stanfordmlgroup.github.io/projects/mura/
2. Map MURA studies to the structure above. MURA uses "positive" / "negative" for abnormality; you can treat positive as fracture and negative as normal, and use the body part (ELBOW, FINGER, etc.) as the folder name.

## FracAtlas / fracture datasets

Use any public X-ray fracture dataset that provides:
- Body part or bone type
- Fracture vs normal
- Optionally fracture type (simple, comminuted, greenstick)

Place images in the corresponding `{body_part}/{normal|fracture_type}/` folders.

## Quick test without real data

Run training with no data; the script will use a small dummy set so the pipeline runs and you can export a TFLite model for the app. Replace with real data for real metrics.
