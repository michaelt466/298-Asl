import cv2
import numpy as np


def setup_display(window_name="Live Stream"):
    """Initialize the display window with mouse callback for settings toggle."""
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    return window_name


def draw_settings_panel(img, panel_open, settings, panel_x, panel_y):
    """Draw the Settings dropdown button and optional expanded panel."""
    btn_w, btn_h = 80, 20
    # Draw settings button (top-right)
    cv2.rectangle(img, (panel_x, panel_y), (panel_x + btn_w, panel_y + btn_h), (200, 200, 200), -1)
    cv2.rectangle(img, (panel_x, panel_y), (panel_x + btn_w, panel_y + btn_h), (120, 120, 120), 1)
    arrow = "v" if not panel_open else "^"
    cv2.putText(img, f"{arrow} Settings", (panel_x + 4, panel_y + 14),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (50, 50, 50), 1, cv2.LINE_AA)

    if panel_open:
        item_h = 18
        options = ["Subtitles", "Read-aloud", "Camera Feed"]
        panel_h = item_h * len(options) + 6
        cv2.rectangle(img, (panel_x, panel_y + btn_h),
                      (panel_x + btn_w, panel_y + btn_h + panel_h), (230, 230, 230), -1)
        cv2.rectangle(img, (panel_x, panel_y + btn_h),
                      (panel_x + btn_w, panel_y + btn_h + panel_h), (120, 120, 120), 1)

        for i, label in enumerate(options):
            key = label.lower().replace(" ", "_")
            ty = panel_y + btn_h + 14 + i * item_h
            checked = settings.get(key, True)
            # Checkbox square
            cv2.rectangle(img, (panel_x + 4, ty - 10), (panel_x + 13, ty - 1), (255, 255, 255), -1)
            cv2.rectangle(img, (panel_x + 4, ty - 10), (panel_x + 13, ty - 1), (80, 80, 80), 1)
            if checked:
                cv2.line(img, (panel_x + 5, ty - 5), (panel_x + 8, ty - 2), (0, 150, 0), 1)
                cv2.line(img, (panel_x + 8, ty - 2), (panel_x + 13, ty - 9), (0, 150, 0), 1)
            cv2.putText(img, label, (panel_x + 16, ty),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (30, 30, 30), 1, cv2.LINE_AA)


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
    draw_settings_panel(img, panel_open, settings, panel_x, panel_y)

    # --- Subtitle bar (bottom) ---
    bar_y = h - bar_h
    subtitles_active = settings.get("subtitles", True)
    draw_subtitle_bar(img, current_word, subtitles_active, bar_y, bar_h)

    cv2.imshow(window_name, img)