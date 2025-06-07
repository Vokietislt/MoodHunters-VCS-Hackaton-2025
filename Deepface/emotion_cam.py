import cv2
import csv
import os
from datetime import datetime
from deepface import DeepFace
import win32gui
import win32process
import psutil

# ─── Configuration ────────────────────────────────────────────────────────────
CSV_LOG_PATH = "emotion_log.csv"  # CSV file for logging results
CAMERA_INDEX = 0                  # Change to 1 or 2 if 0 doesn’t work
FRAME_WIDTH = 640                 # Resize width for performance
FRAME_HEIGHT = 480                # Resize height for performance
ANALYZE_EVERY_N_FRAMES = 2        # Skip frames to speed up (analyze every 2nd frame)
# ──────────────────────────────────────────────────────────────────────────────

# ─── Foreground App Detection ─────────────────────────────────────────────────
def get_foreground_app():
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        exe_name = process.name()
        window_title = win32gui.GetWindowText(hwnd)
        return f"{exe_name} - {window_title}"
    except Exception:
        return "Unknown"
# ──────────────────────────────────────────────────────────────────────────────

# Initialize webcam with DirectShow backend (Windows)
cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
if not cap.isOpened():
    print(f"Failed to open camera with index {CAMERA_INDEX}. Exiting.")
    exit(1)

# Prepare CSV logging (create file with headers if not exists)
if not os.path.exists(CSV_LOG_PATH):
    with open(CSV_LOG_PATH, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "face_id", "emotion", "confidence", "foreground_app"])

# Frame counter for skipping
frame_counter = 0

# Main loop
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize for performance
    frame_resized = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

    # Only analyze every Nth frame
    if frame_counter % ANALYZE_EVERY_N_FRAMES == 0:
        try:
            # DeepFace returns a list if multiple faces; otherwise a dict
            results = DeepFace.analyze(frame_resized, actions=["emotion"], enforce_detection=False)

            # Ensure results is iterable
            if not isinstance(results, list):
                results = [results]

            # Log and draw for each detected face
            for face_id, analysis in enumerate(results, start=1):
                region = analysis.get("region", {})
                x, y, w, h = region.get("x", 0), region.get("y", 0), region.get("w", 0), region.get("h", 0)

                if w == 0 or h == 0:
                    continue

                # Adjust region coords to original frame size if needed
                scale_x = frame.shape[1] / FRAME_WIDTH
                scale_y = frame.shape[0] / FRAME_HEIGHT
                x_orig = int(x * scale_x)
                y_orig = int(y * scale_y)
                w_orig = int(w * scale_x)
                h_orig = int(h * scale_y)

                dominant = analysis["dominant_emotion"]
                confidence = analysis["emotion"].get(dominant, 0.0)

                # Draw bounding box and label on original frame
                cv2.rectangle(frame, (x_orig, y_orig), (x_orig + w_orig, y_orig + h_orig), (0, 255, 0), 2)
                label = f"{dominant}: {confidence:.2f}"
                cv2.putText(
                    frame,
                    label,
                    (x_orig, y_orig - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA,
                )

                # Log to CSV with foreground app
                timestamp = datetime.now().isoformat(sep=" ", timespec="seconds")
                foreground_app = get_foreground_app()
                with open(CSV_LOG_PATH, mode="a", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([timestamp, face_id, dominant, f"{confidence:.2f}", foreground_app])

        except Exception:
            # If an error occurs (e.g., no face detected), skip this frame
            pass

    # Show the annotated frame
    cv2.imshow("DeepFace Emotion", frame)
    frame_counter += 1

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Clean up
cap.release()
cv2.destroyAllWindows()
