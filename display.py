import cv2
import numpy as np


def setup_display(window_name="Live Stream"):
    """Initialize the display window with mouse callback for settings toggle."""
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    return window_name

def draw_subtitle_bar(img, current_word, subtitles_active, bar_y, bar_h=30):
    """Draw the subtitle status bar with colored dot and text."""
    h, w = img.shape[:2]
    # Subtitle bar background
    cv2.rectangle(img, (0, bar_y), (w, bar_y + bar_h), (210, 210, 210), -1)
    cv2.rectangle(img, (0, bar_y), (w, bar_y + bar_h), (160, 160, 160), 1)

    dot_color = (0, 200, 0) if subtitles_active else (0, 0, 220)
    label = current_word if subtitles_active else "Inactive Subtitles"

    cx, cy = 16, bar_y + bar_h // 2
    cv2.circle(img, (cx, cy), 8, dot_color, -1)
    cv2.putText(img, label, (32, bar_y + bar_h // 2 + 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (40, 40, 40), 1, cv2.LINE_AA)


def update_display(img, current_word, window_name="Live Stream",
                   roi=(70, 70, 350, 350), settings=None, panel_open=False):
    """
    Draw the ROI, settings panel, and subtitle bar on the frame and display it.

    Args:
        img:          The current video frame (modified in-place).
        current_word: Text shown in the subtitle bar.
        window_name:  OpenCV window name.
        roi:          (x1, y1, x2, y2) region-of-interest box.
        settings:     Dict with keys 'subtitles', 'read_aloud', 'camera_feed' (bools).
        panel_open:   Whether the Settings dropdown is expanded.
    """
    if img is None:
        return

    if settings is None:
        settings = {"subtitles": True, "read_aloud": False, "camera_feed": True}

    h, w = img.shape[:2]
    bar_h = 34

    # --- ROI box ---
    x1, y1, x2, y2 = roi
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # --- Settings button (top-right corner) ---
    panel_x = w - 90
    panel_y = 4

    # --- Subtitle bar (bottom) ---
    bar_y = h - bar_h
    subtitles_active = settings.get("subtitles", True)
    draw_subtitle_bar(img, current_word, subtitles_active, bar_y, bar_h)

    cv2.imshow(window_name, img)