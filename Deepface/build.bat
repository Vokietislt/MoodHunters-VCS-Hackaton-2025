@echo off
REM Clean previous build/dist folders
rmdir /s /q build
rmdir /s /q dist

REM Build MoodHunters.exe from moodhunters.py
REM --onefile bundles into a single executable
REM --add-data copies dependent scripts into the bundle (adjust paths)
pyinstaller --noconfirm --onefile --console ^
  --add-data "emotion_cam.py;." ^
  --add-data "app.py;." ^
  --add-data "dbfunctions.py;." ^
  moodhunters.py

@REM   --hidden-import=cv2 ^
@REM   --hidden-import=tensorflow ^
@REM   --hidden-import=pandas ^
@REM   --hidden-import=numpy ^
@REM   --hidden-import=scipy ^