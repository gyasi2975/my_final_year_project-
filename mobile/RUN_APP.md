# Run the Bone Fracture app

## 1. Install Flutter (if needed)

- Install Flutter: https://docs.flutter.dev/get-started/install/windows  
- Add Flutter to your PATH (e.g. `C:\flutter\bin` or your install path).  
- In a **new** terminal, run: `flutter doctor`

## 2. Run the app

From the mobile folder:

```powershell
cd c:\Users\boaky\Music\gloria\mobile
flutter pub get
flutter run
```

Pick a device when prompted (Windows desktop or a connected Android device).

## 3. TFLite model (bundled)

The app loads `assets/bone_fracture.tflite` (fine-tuned June 2026 model).

After retraining in `ml/`:

```powershell
cd c:\Users\boaky\Music\gloria\ml
.\venv\Scripts\python.exe export_tflite.py --float32
Copy-Item -Force export\bone_fracture.tflite ..\mobile\assets\bone_fracture.tflite
cd ..\mobile
flutter pub get
flutter run
```

Use `--float32` for best Android compatibility.

Then capture or pick an X-ray to see body part, fracture detection, and fracture type.
