# Step-by-Step: Download Datasets and Train the Model

Follow these steps in order. All commands assume you are in the project folder `D:\Projects\gloria`.

---

## Step 1: Create the data folder structure

Open PowerShell and run:

```powershell
cd D:\Projects\gloria\ml
python -c "
from pathlib import Path
p = Path('data/raw')
for split in ['train','valid','test']:
    for body in ['elbow','finger','forearm','hand','humerus','shoulder','wrist']:
        (p/split/body/'normal').mkdir(parents=True, exist_ok=True)
        for ft in ['fracture_simple','fracture_comminuted','fracture_greenstick']:
            (p/split/body/ft).mkdir(parents=True, exist_ok=True)
print('Folders created under ml/data/raw/')
"
```

---

## Step 2: Download the MURA dataset

1. **Go to Stanford AIMI (MURA):**
   - Open: **https://stanfordaimi.azurewebsites.net/datasets**
   - Search for **"MURA"** or **"Musculoskeletal Radiographs"**.
   - Or use: **https://stanfordaimi.azurewebsites.net/datasets/3e00d84b-d86e-4fed-b2a4-bfe3effd661b**
   - Find the dataset **"MURA (Musculoskeletal Radiographs)"** (bone X-rays, ~40k images).

2. **Register / sign in** if the site asks (Stanford AIMI may require a free account).

3. **Download the dataset:**
   - Use the provided download link (often a zip or multiple zips by body part).
   - Save the downloaded file(s) to: `D:\Projects\gloria\ml\data\downloads\mura`
   - Create that folder if needed: `mkdir D:\Projects\gloria\ml\data\downloads\mura`

4. **Unzip** the MURA archive(s) into `ml\data\downloads\mura`. You should see structure like:
   - `MURA-v1.1/` or similar, with subfolders by **body part** (e.g. `ELBOW`, `FINGER`, `FOREARM`, `HAND`, `HUMERUS`, `SHOULDER`, `WRIST`) and inside each, studies labeled **positive** (abnormal/fracture) or **negative** (normal).

---

## Step 3: Download the FracAtlas dataset (fracture types)

1. **Go to Figshare (FracAtlas):**
   - Open: **https://figshare.com/articles/dataset/FracAtlas_A_Dataset_for_Fracture_Classification_Localization_and_Segmentation_of_Musculoskeletal_Radiographs/22363012**
   - Or search **"FracAtlas fracture"** on Figshare.

2. **Download:**
   - Click **"Download all"** (or the main dataset zip).
   - Save to: `D:\Projects\gloria\ml\data\downloads\fracatlas`
   - Create folder: `mkdir D:\Projects\gloria\ml\data\downloads\fracatlas`

3. **Unzip** into `ml\data\downloads\fracatlas`. You should see images and annotation files (e.g. CSV/JSON with labels like fracture type).

---

## Step 4: Prepare data into the project format

Our training code expects this layout:

```
ml/data/raw/
  train/
    elbow/   normal/   and   fracture_simple/   fracture_comminuted/   fracture_greenstick/
    finger/  ...
  valid/
  test/
```

Run the preparation script (it will copy images from `downloads/mura` and `downloads/fracatlas` into `raw/train`, `raw/valid`, `raw/test` with an 80/10/10 split):

```powershell
cd D:\Projects\gloria\ml
python data/prepare_datasets.py
```

**If you only have MURA:** the script maps MURA “positive” → `fracture_simple` and “negative” → `normal`, and splits 80/10/10 into train/valid/test.

**If you have both MURA and FracAtlas:** the script uses FracAtlas for fracture-type labels where available and MURA for the rest.

(If the script fails, see “Manual copy” in Step 4b below.)

---

## Step 4b: Manual copy (if no script or script fails)

- **From MURA:**  
  - For each body part (e.g. ELBOW → `elbow`), copy:
    - **Negative** images → `raw/train/elbow/normal/` (and a small part to `raw/valid/elbow/normal/`, `raw/test/elbow/normal/`).
    - **Positive** images → `raw/train/elbow/fracture_simple/` (and same for valid/test) if you don’t have fracture types; otherwise map to `fracture_simple`, `fracture_comminuted`, or `fracture_greenstick` if you have that info.
- **From FracAtlas:**  
  - Use the dataset’s labels to copy images into the right `raw/{train|valid|test}/{body_part}/normal/` or `.../fracture_simple/`, `.../fracture_comminuted/`, `.../fracture_greenstick/` as needed.

---

## Step 5: Install Python dependencies

```powershell
cd D:\Projects\gloria\ml
pip install -r requirements.txt
```

Use a virtual environment if you prefer:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## Step 6: Train the model

```powershell
cd D:\Projects\gloria\ml
python train.py
```

Optional arguments:

- `--epochs 30`   (default 20)
- `--batch-size 16`
- `--save checkpoints/my_model.keras`

Training will:
- Load data from `data/raw/train` and `data/raw/valid`.
- Save the best model to `checkpoints/bone_fracture_model.keras`.

---

## Step 7: Export to TFLite (for the mobile app)

```powershell
cd D:\Projects\gloria\ml
python export_tflite.py
```

Default: reads `checkpoints/bone_fracture_model.keras`, writes `export/bone_fracture.tflite`.

Custom paths:

```powershell
python export_tflite.py --model checkpoints/my_model.keras --output export/my_app.tflite
```

---

## Step 8: Copy the model into the mobile app

```powershell
copy D:\Projects\gloria\ml\export\bone_fracture.tflite D:\Projects\gloria\mobile\assets\bone_fracture.tflite
```

Then run the app (e.g. on your phone or Windows):

```powershell
cd D:\Projects\gloria\mobile
flutter run
```

---

## Step 9: (Optional) Evaluate the model

To print metrics (accuracy, precision, recall, F1) on the test set:

```powershell
cd D:\Projects\gloria\ml
python evaluate.py --model checkpoints/bone_fracture_model.keras
```

Requires data in `data/raw/test/`.

---

## Quick reference – folder layout

| Purpose              | Path |
|----------------------|------|
| Raw data (train/valid/test) | `ml/data/raw/` |
| MURA download        | `ml/data/downloads/mura/` |
| FracAtlas download   | `ml/data/downloads/fracatlas/` |
| Saved model          | `ml/checkpoints/bone_fracture_model.keras` |
| TFLite for app       | `ml/export/bone_fracture.tflite` |
| App assets           | `mobile/assets/bone_fracture.tflite` |

---

## If you have no data yet (dummy run)

To test the pipeline without real data:

```powershell
cd D:\Projects\gloria\ml
pip install -r requirements.txt
python train.py
```

The script will use a small dummy dataset and save a checkpoint. You can then run `export_tflite.py` and copy the `.tflite` to `mobile/assets/` to verify the app loads the model (predictions will not be meaningful until you train on real data).
