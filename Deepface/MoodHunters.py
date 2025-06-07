import subprocess
import os
import sys

# Ensure paths are absolute and work even after compiling
base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

emotion_cam_path = os.path.join(base_path, "emotion_cam.py")
app_path = os.path.join(base_path, "app.py")

# Launch emotion_cam.py in one process
subprocess.Popen(["python", emotion_cam_path])

# Launch streamlit app.py in another process
subprocess.Popen(["streamlit", "run", app_path])
