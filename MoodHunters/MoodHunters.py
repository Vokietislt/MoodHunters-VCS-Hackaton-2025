import sys
import os
import subprocess
import threading
import signal
import psutil
import traceback
import sqlite3
from dbfunctions import EmotionLogDB
procs = []
db = EmotionLogDB()
db.close()
def cleanup(signum, frame):
    print("Cleaning up subprocesses...")
    for p in procs:
        if p.poll() is None:
            p.terminate()
    print("Cleanup done.")
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)

def get_extracted_path(filename: str) -> str:
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.abspath(filename)

def stream_subprocess_output(proc):
    def print_stream(stream, label):
        for line in iter(stream.readline, ''):
            if line:
                print(f"[{label}] {line.strip()}")
    threading.Thread(target=print_stream, args=(proc.stdout, f"PID {proc.pid} STDOUT"), daemon=True).start()
    threading.Thread(target=print_stream, args=(proc.stderr, f"PID {proc.pid} STDERR"), daemon=True).start()

def wait_proc(proc):
    ret = proc.wait()
    print(f"Process PID {proc.pid} exited with code {ret}")

def find_running_process(cmd_substring):
    for proc in psutil.process_iter(['pid', 'cmdline', 'status']):
        try:
            cmdline = proc.info['cmdline']
            status = proc.info['status']
            if cmdline and any(cmd_substring in part for part in cmdline):
                if status in (psutil.STATUS_RUNNING, psutil.STATUS_SLEEPING, psutil.STATUS_DISK_SLEEP):
                    return proc
                else:
                    proc.terminate()
                    proc.wait(timeout=5)
                    return None
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

try:
    print("Starting subprocesses...")

    # Get paths inside bundle or normal path
    emotion_cam_path = get_extracted_path('emotion_cam.py')
    app_py_path = get_extracted_path('app.py')

    # Use system python, requires python in PATH on user system
    python_exe = "python"

    emotion_proc = find_running_process('emotion_cam.py')
    if emotion_proc:
        print(f"emotion_cam.py already running with PID {emotion_proc.pid}. Skipping launch.")
    else:
        print(f"Launching emotion_cam.py: {emotion_cam_path}")
        p1 = subprocess.Popen(
            [python_exe, emotion_cam_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stream_subprocess_output(p1)
        procs.append(p1)

    streamlit_proc = find_running_process('streamlit')
    streamlit_running = False
    if streamlit_proc and app_py_path in ' '.join(streamlit_proc.info['cmdline']):
        streamlit_running = True
        print(f"Streamlit app already running with PID {streamlit_proc.pid}. Skipping launch.")

    if not streamlit_running:
        print(f"Launching Streamlit app: {app_py_path}")
        p2 = subprocess.Popen(
            ['streamlit', 'run', app_py_path, '--server.runOnSave', 'false'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stream_subprocess_output(p2)
        procs.append(p2)

    if not procs:
        print("No subprocesses launched. Exiting.")
        sys.exit(0)

    threads = []
    for p in procs:
        t = threading.Thread(target=wait_proc, args=(p,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

except Exception as e:
    print("Error occurred:", e)
    traceback.print_exc()
    cleanup(None, None)

finally:
    print("Script exiting normally.")
    input("Press Enter to exit...")
