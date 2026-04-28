# display.py
import cv2
import numpy as np
import os

def setup_display(window_name="Live Stream"):
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 720)
    return window_name

def load_slide_folder(folder_path):
    exts = (".png", ".jpg", ".jpeg", ".bmp")
    files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(exts)])
    return [img for img in (cv2.imread(os.path.join(folder_path, f)) for f in files) if img is not None]

def load_single_slide(path):
    img = cv2.imread(path)
    return [img] if img is not None else []

def draw_slide_area(canvas, slides, slide_idx, region):
    x1, y1, x2, y2 = region
    rw, rh = x2 - x1, y2 - y1

    cv2.rectangle(canvas, (x1, y1), (x2, y2), (255, 255, 255), -1)
    cv2.rectangle(canvas, (x1, y1), (x2, y2), (180, 180, 180), 1)

    if not slides:
        cv2.putText(canvas, "No slides loaded - click Upload",
                    (x1 + rw // 2 - 120, y1 + rh // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (160, 160, 160), 1, cv2.LINE_AA)
        return None, None

    slide = slides[slide_idx]
    sh, sw = slide.shape[:2]
    pad = 12
    avail_w, avail_h = rw - pad * 2, rh - pad * 2 - 32
    scale = min(avail_w / sw, avail_h / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    resized = cv2.resize(slide, (nw, nh), interpolation=cv2.INTER_AREA)
    ox, oy = x1 + pad + (avail_w - nw) // 2, y1 + pad + (avail_h - nh) // 2
    canvas[oy:oy + nh, ox:ox + nw] = resized

    nav_y, total = y2 - 28, len(slides)
    prev_rect = (x1 + 8, nav_y, x1 + 68, y2 - 4)
    active_prev = slide_idx > 0
    cv2.rectangle(canvas, prev_rect[:2], prev_rect[2:], (80, 80, 200) if active_prev else (190, 190, 190), -1)
    cv2.putText(canvas, "< Prev", (x1 + 12, nav_y + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255) if active_prev else (140, 140, 140), 1, cv2.LINE_AA)

    cv2.putText(canvas, f"{slide_idx + 1} / {total}", (x1 + rw // 2 - 20, nav_y + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (80, 80, 80), 1, cv2.LINE_AA)

    next_rect = (x2 - 68, nav_y, x2 - 8, y2 - 4)
    active_next = slide_idx < total - 1
    cv2.rectangle(canvas, next_rect[:2], next_rect[2:], (80, 80, 200) if active_next else (190, 190, 190), -1)
    cv2.putText(canvas, "Next >", (x2 - 62, nav_y + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255) if active_next else (140, 140, 140), 1, cv2.LINE_AA)

    return prev_rect, next_rect

def draw_upload_button(canvas, btn_state, cx, cy):
    btn_w, btn_h = 160, 36
    bx1, by1 = cx - btn_w // 2, cy - btn_h // 2
    bx2, by2 = bx1 + btn_w, by1 + btn_h
    color = (50, 50, 160) if btn_state else (80, 80, 200)
    cv2.rectangle(canvas, (bx1, by1), (bx2, by2), color, -1)
    cv2.rectangle(canvas, (bx1, by1), (bx2, by2), (150, 150, 255), 1)
    cv2.putText(canvas, "^ Upload Slides", (bx1 + 14, by1 + 23), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
    return (bx1, by1, bx2, by2)

def draw_subtitle_bar(canvas, current_word, subtitles_active, bar_y, width, bar_h=55):
    cv2.rectangle(canvas, (0, bar_y), (width, bar_y + bar_h), (30, 30, 30), -1)
    cv2.line(canvas, (0, bar_y), (width, bar_y), (60, 60, 60), 1)
    dot_color = (0, 200, 0) if subtitles_active else (0, 0, 200)
    label = f"WORD: {current_word}" if subtitles_active else "Inactive Subtitles"
    cv2.circle(canvas, (25, bar_y + bar_h // 2), 8, dot_color, -1)
    cv2.putText(canvas, label, (50, bar_y + bar_h // 2 + 7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (210, 210, 210), 2, cv2.LINE_AA)

def update_display(cam_frame, current_word, window_name="Live Stream", 
                   settings=None, hand_coords=None, slides=None, 
                   slide_idx=0, sign_img=None, btn_state=False):
    # Default initializations for compatibility with main.py
    if settings is None: settings = {"subtitles": True}
    if slides is None: slides = []
    
    WIDTH, HEIGHT = 1280, 720
    SUBTITLE_H = 60
    CONTENT_H = HEIGHT - SUBTITLE_H

    canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    canvas[:] = (45, 45, 45) # Dark gray background

    # --- Left: Camera Area ---
    cam_x1, cam_y1 = 15, 15
    cam_x2, cam_y2 = int(WIDTH * 0.45), CONTENT_H - 15
    cv2.rectangle(canvas, (cam_x1, cam_y1), (cam_x2, cam_y2), (20, 20, 20), -1)

    if cam_frame is not None:
        rw, rh = cam_x2 - cam_x1, cam_y2 - cam_y1
        ch, cw = cam_frame.shape[:2]
        scale = min(rw / cw, rh / ch)
        nw, nh = int(cw * scale), int(ch * scale)
        resized_cam = cv2.resize(cam_frame, (nw, nh), interpolation=cv2.INTER_AREA)
        ox, oy = cam_x1 + (rw - nw) // 2, cam_y1 + (rh - nh) // 2
        canvas[oy:oy + nh, ox:ox + nw] = resized_cam

        # Draw the prediction bounding box (70:350 range based on your predict function)
        # We scale the 70-350 coords to the resized camera view
        bx1, by1 = int(70 * scale) + ox, int(70 * scale) + oy
        bx2, by2 = int(350 * scale) + ox, int(350 * scale) + oy
        cv2.rectangle(canvas, (bx1, by1), (bx2, by2), (0, 255, 0), 2)
        cv2.putText(canvas, "ROI", (bx1, by1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # --- Right: Slides Area ---
    slide_x1 = int(WIDTH * 0.45) + 15
    slide_region = (slide_x1, 15, WIDTH - 15, CONTENT_H - 15)
    prev_rect, next_rect = draw_slide_area(canvas, slides, slide_idx, slide_region)

    # --- Bottom: UI Controls & Subtitles ---
    draw_subtitle_bar(canvas, current_word, settings.get("subtitles"), CONTENT_H, WIDTH, SUBTITLE_H)
    upload_rect = draw_upload_button(canvas, btn_state, WIDTH - 100, CONTENT_H + SUBTITLE_H // 2)

    cv2.imshow(window_name, canvas)
    return upload_rect, prev_rect, next_rect