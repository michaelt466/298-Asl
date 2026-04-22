import cv2


def setup_display(window_name="Live Stream"):
    """Initialize the display window for live video output."""
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    return window_name


def update_display(img, current_word, window_name="Live Stream", roi=(70, 70, 350, 350)):
    """Draw the ROI and current word on the frame and display it."""
    if img is None:
        return

    x1, y1, x2, y2 = roi
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

    height = img.shape[0]
    position = (10, height - 20)

    cv2.putText(
        img,
        current_word,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )

    cv2.imshow(window_name, img)
