# Run the Bone Fracture app

## 1. Install Flutter (if needed)

- Install Flutter: https://docs.flutter.dev/get-started/install/windows  
- Add Flutter to your PATH (e.g. `C:\flutter\bin` or your install path).  
- In a **new** terminal, run: `flutter doctor`

## 2. Run the app

From the project root:

```powershell
cd d:\Projects\gloria\mobile
flutter pub get
flutter run
```

Pick a device when prompted (Chrome, Windows, or a connected Android device).

## 3. Without the TFLite model

The app will start even if `assets/bone_fracture.tflite` is missing. You’ll see a message that the model is not loaded. To enable inference:

1. Train and export the model from the ML pipeline (see main README).
2. Copy `d:\Projects\gloria\ml\export\bone_fracture.tflite` to `d:\Projects\gloria\mobile\assets\bone_fracture.tflite`.
3. Run the app again.

Then you can capture or pick an X-ray and see body part, fracture detection, fracture type, and the heat map overlay.
