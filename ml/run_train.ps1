# Run from: D:\Projects\gloria\ml
# Uses Python 3.11 venv to train the model.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "Creating venv with Python 3.11..."
    py -3.11 -m venv venv
}

Write-Host "Installing dependencies (this may take a few minutes)..."
& .\venv\Scripts\python.exe -m pip install -r requirements.txt -q

Write-Host "Starting training..."
& .\venv\Scripts\python.exe train.py --epochs 20

Write-Host "Exporting TFLite..."
& .\venv\Scripts\python.exe export_tflite.py

$dest = "..\mobile\assets\bone_fracture.tflite"
if (Test-Path "export\bone_fracture.tflite") {
    Copy-Item "export\bone_fracture.tflite" $dest -Force
    Write-Host "Copied model to mobile/assets/. Run the app with: cd ..\mobile; flutter run"
} else {
    Write-Host "TFLite file not found. Check export folder."
}
