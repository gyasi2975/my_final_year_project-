# Train the model (your data is ready)

You have **3,271 train**, **411 valid**, and **401 test** images in `data/raw/`. FracAtlas was prepared successfully. MURA was not detected (check that `data/downloads/mura` contains the unzipped MURA folder with `train/ELBOW/...` etc. if you want to add it).

## Python version

**TensorFlow needs Python 3.10 or 3.11** (it does not support Python 3.14 yet).

### Option A: You have Python 3.10 or 3.11 installed

1. Open PowerShell and go to the ML folder:
   ```powershell
   cd D:\Projects\gloria\ml
   ```

2. Create a virtual environment with that Python (use the version you have):
   ```powershell
   py -3.11 -m venv venv
   ```
   Or if only 3.10: `py -3.10 -m venv venv`

3. Activate it and install dependencies:
   ```powershell
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. Train:
   ```powershell
   python train.py --epochs 20
   ```

5. Export for the app and copy to mobile:
   ```powershell
   python export_tflite.py
   copy export\bone_fracture.tflite ..\mobile\assets\bone_fracture.tflite
   ```

### Option B: Install Python 3.11

1. Download **Python 3.11** from https://www.python.org/downloads/release/python-3119/
2. Run the installer and check **“Add Python to PATH”**.
3. In a **new** PowerShell window, run Option A (create venv with `py -3.11 -m venv venv`, then activate, pip install, train).

---

After training finishes, the model is saved as `checkpoints/bone_fracture_model.keras`. Run `export_tflite.py` and copy the `.tflite` file to `mobile/assets/` to use it in the app.
