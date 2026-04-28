# display.py
import cv2
import numpy as np
import os
import aspose.slides as slides_api # Used for PPTX conversion

def setup_display(window_name="Live Stream"):
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 720)
    return window_name

def load_slide_folder(folder_path):
    exts = (".png", ".jpg", ".jpeg", ".bmp")
    files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(exts)])
    return [img for img in (cv2.imread(os.path.join(folder_path, f)) for f in files) if img is not None]

def load_pptx_as_images(pptx_path):
    """Converts a PPTX file into a list of OpenCV images."""
    presentation = slides_api.Presentation(pptx_path)
    slide_images = []
    
    # Create a temporary directory to store slide exports if needed, 
    # or render directly to stream
    for i in range(len(presentation.slides)):
        # Define the scale (adjust for quality)
        scale_x, scale_y = 1.5, 1.5 
        bmp = presentation.slides[i].get_thumbnail(scale_x, scale_y)
        
        # Convert Aspose Bitmap to OpenCV format
        # We save to a temp buffer then read with CV2
        img_array = np.array(bmp)
        # Convert from RGB to BGR for OpenCV
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
        slide_images.append(img_bgr)
        
    return slide_images

def load_single_slide(path):
    """Detects file type and loads accordingly."""
    if path.lower().endswith('.pptx'):
        try:
            return load_pptx_as_images(path)
        except Exception as e:
            print(f"Error loading PPTX: {e}")
            return []
    
    # Default to image loading
    img = cv2.imread(path)
    return [img] if img is not None else []

# ... [Keep draw_slide_area, draw_upload_button, and draw_subtitle_bar the same] ...

def update_display(cam_frame, current_word, window_name="Live Stream", 
                   settings=None, hand_coords=None, slides=None, 
                   slide_idx=0, sign_img=None, btn_state=False):
    if settings is None: settings = {"subtitles": True}
    if slides is None: slides = []
    
    WIDTH, HEIGHT = 1280, 720
    SUBTITLE_H = 60
    CONTENT_H = HEIGHT - SUBTITLE_H

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

        bx1, by1 = int(70 * scale) + ox, int(70 * scale) + oy
        bx2, by2 = int(350 * scale) + ox, int(350 * scale) + oy
        cv2.rectangle(canvas, (bx1, by1), (bx2, by2), (0, 255, 0), 2)
        cv2.putText(canvas,"ROI", (bx1, by1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # --- Right: Slides Area ---
    slide_x1 = int(WIDTH * 0.45) + 15
    slide_region = (slide_x1, 15, WIDTH - 15, CONTENT_H - 15)
    prev_rect, next_rect = draw_slide_area(canvas, slides, slide_idx, slide_region)

    # --- Bottom: UI Controls & Subtitles ---
    draw_subtitle_bar(canvas, current_word, settings.get("subtitles"), CONTENT_H, WIDTH, SUBTITLE_H)
    # Positioning the button on the far right of the subtitle bar
    upload_rect = draw_upload_button(canvas, btn_state, WIDTH - 100, CONTENT_H + SUBTITLE_H // 2)

    cv2.imshow(window_name, canvas)
    return upload_rect, prev_rect, next_rect