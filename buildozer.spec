[app]

# (str) Title of your application
title = Precision Land Calculator

# (str) Package name
package.name = landcalculator

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application version
version = 0.1

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.0

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API required
android.minapi = 21

# (list) Permissions
android.permissions = INTERNET

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Accept SDK license
android.accept_sdk_license = True

# (bool) Skip Android SDK update
android.skip_update = False

# (int) Fullscreen mode
fullscreen = 0
here
