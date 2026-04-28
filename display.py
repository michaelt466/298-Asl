import cv2
import numpy as np
import os
import aspose.slides as slides_api

def setup_display(window_name="Live Stream"):
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 720)
    return window_name

def load_pptx_as_images(pptx_path):
    """Converts a PPTX file into a list of OpenCV images."""
    presentation = slides_api.Presentation(pptx_path)
    slide_images = []
    
    for i in range(len(presentation.slides)):
        # Higher scale = better quality
        bmp = presentation.slides[i].get_thumbnail(1.5, 1.5)
        
        # Convert Aspose Bitmap to BGR for OpenCV
        img_array = np.array(bmp)
        # Aspose often returns RGBA; convert to BGR
        if img_array.shape[2] == 4:
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
        else:
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        slide_images.append(img_bgr)
        
    return slide_images

def load_single_slide(path):
    if path.lower().endswith('.pptx'):
        try:
            return load_pptx_as_images(path)
        except Exception as e:
            print(f"Error loading PPTX: {e}")
            return []
    
    img = cv2.imread(path)
    return [img] if img is not None else []

def draw_slide_area(canvas, slides, slide_idx, region):
    """Draws the slide and returns the bounding boxes for Prev/Next buttons."""
    x1, y1, x2, y2 = region
    w, h = x2 - x1, y2 - y1
    
    # Draw Background
    cv2.rectangle(canvas, (x1, y1), (x2, y2), (30, 30, 30), -1)
    
    if slides and len(slides) > 0:
        slide = slides[slide_idx]
        sh, sw = slide.shape[:2]
        scale = min(w/sw, h/sh)
        nw, nh = int(sw*scale), int(sh*scale)
        resized = cv2.resize(slide, (nw, nh), interpolation=cv2.INTER_AREA)
        
        # Center the slide in the region
        ox, oy = x1 + (w-nw)//2, y1 + (h-nh)//2
        canvas[oy:oy+nh, ox:ox+nw] = resized

    # Define Button Rects (Relative to slide area)
    prev_rect = (x1 + 10, y2 - 50, x1 + 60, y2 - 10)
    next_rect = (x2 - 60, y2 - 50, x2 - 10, y2 - 10)
    
    # Draw Navigation Buttons
    for rect, text in [(prev_rect, "<"), (next_rect, ">")]:
        cv2.rectangle(canvas, (rect[0], rect[1]), (rect[2], rect[3]), (100, 100, 100), -1)
        cv2.putText(canvas, text, (rect[0]+15, rect[1]+30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
    return prev_rect, next_rect

def draw_upload_button(canvas, btn_state, x_center, y_center):
    """Draws the upload button and returns its bounding box."""
    color = (0, 150, 0) if not btn_state else (0, 255, 0)
    rect = (x_center - 60, y_center - 20, x_center + 60, y_center + 20)
    
    cv2.rectangle(canvas, (rect[0], rect[1]), (rect[2], rect[3]), color, -1)
    cv2.putText(canvas, "UPLOAD", (rect[0]+12, rect[1]+30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return rect

def draw_subtitle_bar(canvas, current_word, enabled, content_h, width, subtitle_h):
    y_start = content_h
    cv2.rectangle(canvas, (0, y_start), (width, y_start + subtitle_h), (20, 20, 20), -1)
    
    if enabled:
        display_text = f"TEXT: {current_word}"
        cv2.putText(canvas, display_text, (20, y_start + 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

def update_display(cam_frame, current_word, window_name="Live Stream", 
                   settings=None, hand_coords=None, slides=None, 
                   slide_idx=0, sign_img=None, btn_state=False):
    
    if settings is None: settings = {"subtitles": True}
    if slides is None: slides = []
    
    WIDTH, HEIGHT = 1280, 720
    SUBTITLE_H = 60
    CONTENT_H = HEIGHT - SUBTITLE_H

    # Create Dark Theme Canvas
    canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    canvas[:] = (45, 45, 45)

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

        # ROI Overlay (Matching your [70:350, 70:350] prediction logic)
        # Scaling the ROI box relative to the resized camera feed
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
    
    # Crucial: Returning the clickable regions so main.py can detect clicks
    return upload_rect, prev_rect, next_rect