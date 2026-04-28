import cv2
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog
from spire.presentation import Presentation

# Pre-initialize Tkinter for the file dialog to avoid lag
root = tk.Tk()
root.withdraw()

def setup_display(window_name="Live Stream"):
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 720)
    return window_name

def load_pptx_as_images(pptx_path):
    """Converts a PPTX file into a list of OpenCV images using Spire."""
    pres = Presentation()
    pres.LoadFromFile(pptx_path)
    slide_images = []
    
    for i in range(pres.Slides.Count):
        with pres.Slides[i].SaveAsImage() as image:
            temp_path = f"temp_{i}.png"
            image.Save(temp_path)
            cv_img = cv2.imread(temp_path)
            if cv_img is not None:
                slide_images.append(cv_img)
            if os.path.exists(temp_path):
                os.remove(temp_path)
    pres.Dispose()
    return slide_images

def load_single_slide(path):
    if not path: return []
    if path.lower().endswith('.pptx'):
        return load_pptx_as_images(path)
    img = cv2.imread(path)
    return [img] if img is not None else []

def handle_clicks(event, x, y, flags, param):
    """Global click handler to be used in the main loop."""
    global last_click
    if event == cv2.EVENT_LBUTTONDOWN:
        last_click = (x, y)

last_click = None

def update_display(cam_frame, current_word, window_name="Live Stream", 
                   settings=None, slides_state=None):
    """
    slides_state should be a dict: {'slides': [], 'idx': 0}
    This function now handles the click logic internally.
    """
    global last_click
    if settings is None: settings = {"subtitles": True}
    if slides_state is None: slides_state = {'slides': [], 'idx': 0}
    
    WIDTH, HEIGHT = 1280, 720
    SUBTITLE_H = 60
    CONTENT_H = HEIGHT - SUBTITLE_H

    canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    canvas[:] = (45, 45, 45)

    # --- Camera Area ---
    cam_x1, cam_y1, cam_x2, cam_y2 = 15, 15, int(WIDTH * 0.45), CONTENT_H - 15
    cv2.rectangle(canvas, (cam_x1, cam_y1), (cam_x2, cam_y2), (20, 20, 20), -1)
    if cam_frame is not None:
        # Resize and center camera logic...
        ch, cw = cam_frame.shape[:2]
        scale = min((cam_x2-cam_x1)/cw, (cam_y2-cam_y1)/ch)
        nw, nh = int(cw*scale), int(ch*scale)
        resized = cv2.resize(cam_frame, (nw, nh))
        canvas[cam_y1:cam_y1+nh, cam_x1:cam_x1+nw] = resized

    # --- Slides Area ---
    sx1, sy1, sx2, sy2 = int(WIDTH * 0.45) + 15, 15, WIDTH - 15, CONTENT_H - 15
    cv2.rectangle(canvas, (sx1, sy1), (sx2, sy2), (30, 30, 30), -1)
    
    if slides_state['slides']:
        slide = slides_state['slides'][slides_state['idx']]
        sh, sw = slide.shape[:2]
        s_scale = min((sx2-sx1)/sw, (sy2-sy1)/sh)
        snw, snh = int(sw*s_scale), int(sh*s_scale)
        s_resized = cv2.resize(slide, (snw, snh))
        canvas[sy1:sy1+snh, sx1:sx1+snw] = s_resized

    # --- Buttons ---
    # Upload Button
    up_rect = (WIDTH - 150, CONTENT_H + 10, WIDTH - 20, HEIGHT - 10)
    cv2.rectangle(canvas, (up_rect[0], up_rect[1]), (up_rect[2], up_rect[3]), (0, 120, 0), -1)
    cv2.putText(canvas, "UPLOAD", (up_rect[0]+15, up_rect[1]+35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    # Prev/Next Buttons
    p_rect = (sx1 + 10, sy2 - 50, sx1 + 70, sy2 - 10)
    n_rect = (sx2 - 70, sy2 - 50, sx2 - 10, sy2 - 10)
    cv2.rectangle(canvas, (p_rect[0], p_rect[1]), (p_rect[2], p_rect[3]), (80, 80, 80), -1)
    cv2.rectangle(canvas, (n_rect[0], n_rect[1]), (n_rect[2], n_rect[3]), (80, 80, 80), -1)
    cv2.putText(canvas, "<", (p_rect[0]+20, p_rect[1]+30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
    cv2.putText(canvas, ">", (n_rect[0]+20, n_rect[1]+30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

    # --- Subtitles ---
    cv2.putText(canvas, f"Text: {current_word}", (20, CONTENT_H + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    # --- CLICK DETECTION LOGIC ---
    if last_click:
        lx, ly = last_click
        # Check Upload
        if up_rect[0] < lx < up_rect[2] and up_rect[1] < ly < up_rect[3]:
            path = filedialog.askopenfilename(filetypes=[("Slides", "*.pptx"), ("Images", "*.jpg;*.png")])
            if path:
                slides_state['slides'] = load_single_slide(path)
                slides_state['idx'] = 0
        
        # Check Prev/Next
        if p_rect[0] < lx < p_rect[2] and p_rect[1] < ly < p_rect[3]:
            slides_state['idx'] = max(0, slides_state['idx'] - 1)
        if n_rect[0] < lx < n_rect[2] and n_rect[1] < ly < n_rect[3]:
            slides_state['idx'] = min(len(slides_state['slides']) - 1, slides_state['idx'] + 1)
            
        last_click = None # Reset click

    cv2.imshow(window_name, canvas)
    cv2.setMouseCallback(window_name, handle_clicks)