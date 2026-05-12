# App icon

1. Add your app logo here as **`app_icon.png`**.
2. Recommended size: **1024×1024** pixels (square, PNG with transparency if needed).
3. Then from the project root (`mobile/`) run:
   ```bash
   dart run flutter_launcher_icons
   ```
   This generates all launcher icon sizes for Android (and iOS if enabled).

If `app_icon.png` is missing, the icon generator will fail until you add it.
