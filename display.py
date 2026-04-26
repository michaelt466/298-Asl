import cv2
import numpy as np

def setup_display(window_name="Live Stream"):
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    return window_name

def draw_subtitle_bar(img, current_word, subtitles_active, bar_y, width, bar_h=50):
    cv2.rectangle(img, (0, bar_y), (width, bar_y + bar_h), (210, 210, 210), -1)
    dot_color = (0, 200, 0) if subtitles_active else (0, 0, 220)
    label = current_word if subtitles_active else "Inactive Subtitles"
    cv2.circle(img, (20, bar_y + bar_h // 2), 8, dot_color, -1)
    cv2.putText(img, label, (45, bar_y + bar_h // 2 + 7),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (40, 40, 40), 1, cv2.LINE_AA)

def update_display(cam_frame, current_word, window_name="Live Stream", 
                   settings=None, hand_coords=None, slide_img=None, 
                   sign_img=None, btn_state=False):
    # Setup Canvas
    WIDTH, HEIGHT = 1280, 720
    SUBTITLE_H = 60
    SIDE_W = WIDTH // 2
    canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    canvas[:] = (240, 240, 240) # Background color

    # --- 1. Left Side: SLIDES ---
    if slide_img is not None:
        # Resize slide to fit the left half
        s_h, s_w = slide_img.shape[:2]
        ratio = (SIDE_W - 40) / s_w
        resized_slide = cv2.resize(slide_img, (SIDE_W - 40, int(s_h * ratio)))
        y_off = 20
        canvas[y_off:y_off+resized_slide.shape[0], 20:20+resized_slide.shape[1]] = resized_slide
    else:
        cv2.rectangle(canvas, (20, 20), (SIDE_W - 20, HEIGHT - SUBTITLE_H - 20), (255, 255, 255), -1)
        cv2.putText(canvas, "No Slide Loaded", (SIDE_W//4, HEIGHT//2), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2)

    # --- 2. Right Side: CAMERA ---
    if cam_frame is not None:
        cam_w = SIDE_W - 40
        cam_h = int(cam_w * 0.75)
        resized_cam = cv2.resize(cam_frame, (cam_w, cam_h))
        start_x, start_y = SIDE_W + 20, 20
        canvas[start_y:start_y+cam_h, start_x:start_x+cam_w] = resized_cam
        
        # Draw green box for hand_coords if they exist
        if hand_coords:
            x1, y1, x2, y2 = hand_coords
            # Rescale coords to fit the resized camera window
            scale_x = cam_w / cam_frame.shape[1]
            scale_y = cam_h / cam_frame.shape[0]
            cv2.rectangle(canvas, 
                          (int(x1*scale_x)+start_x, int(y1*scale_y)+start_y), 
                          (int(x2*scale_x)+start_x, int(y2*scale_y)+start_y), (0, 255, 0), 2)

    # --- 3. Middle: UPLOAD BUTTON ---
    btn_w, btn_h = 100, 40
    btn_x, btn_y = (WIDTH // 2) - (btn_w // 2), (HEIGHT // 2) - (btn_h // 2)
    color = (150, 150, 150) if btn_state else (200, 200, 200)
    cv2.rectangle(canvas, (btn_x, btn_y), (btn_x + btn_w, btn_y + btn_h), color, -1)
    cv2.rectangle(canvas, (btn_x, btn_y), (btn_x + btn_w, btn_y + btn_h), (50, 50, 50), 2)
    cv2.putText(canvas, "UPLOAD", (btn_x+15, btn_y+25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)

    # --- 4. Bottom Left: SIGN PiP (Picture in Picture) ---
    if sign_img is not None:
        pip_h, pip_w = 120, 120
        resized_sign = cv2.resize(sign_img, (pip_w, pip_h))
        canvas[HEIGHT-SUBTITLE_H-140:HEIGHT-SUBTITLE_H-20, 40:40+pip_w] = resized_sign
        cv2.rectangle(canvas, (40, HEIGHT-SUBTITLE_H-140), (40+pip_w, HEIGHT-SUBTITLE_H-20), (0, 255, 0), 2)

    # --- 5. Bottom: SUBTITLES ---
    draw_subtitle_bar(canvas, current_word, settings.get("subtitles", True), HEIGHT-SUBTITLE_H, WIDTH, SUBTITLE_H)

    cv2.imshow(window_name, canvas)
    return (btn_x, btn_y, btn_x + btn_w, btn_y + btn_h)