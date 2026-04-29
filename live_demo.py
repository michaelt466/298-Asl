import cv2
import sys
import os
import threading
import numpy as np
import display
import spell_checker as spell_checker
import voice as voice

# Disable tensorflow compilation warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()

# Language in which you want to convert
language = 'en'

# Get a live stream from the webcam
live_stream = cv2.VideoCapture(0)

# Word for which letters are currently being signed
current_word = ""

# Load training labels file
label_lines = [line.rstrip() for line in tf.gfile.GFile("training_set_labels.txt")]

# Load trained model's graph
with tf.gfile.FastGFile("trained_model_graph.pb", 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    _ = tf.import_graph_def(graph_def, name='')


def predict(sess, softmax_tensor, image_data):
    # Focus on Region of Interest (Image within the bounding box)
    resized_image = image_data[70:350, 70:350]

    # Resize to 200 x 200
    resized_image = cv2.resize(resized_image, (200, 200))

    image_data = cv2.imencode('.jpg', resized_image)[1].tobytes()

    predictions = sess.run(softmax_tensor, {'DecodeJpeg/contents:0': image_data})

    # Sort to show labels of first prediction in order of confidence
    top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]

    max_score = 0.0
    res = ''
    for node_id in top_k:
        # Just to get rid of the Z error for demo
        if label_lines[node_id].upper() == 'Z':
            human_string = label_lines[node_id + 1]
        else:
            human_string = label_lines[node_id]
        score = predictions[0][node_id]
        if score > max_score:
            max_score = score
            res = human_string

    return res, max_score


def speak_letter(letter):
    voice.speak(letter)


def process_letter(sess, softmax_tensor, img):
    """Run prediction on a frame and update current_word. Returns updated word."""
    global current_word

    letter, score = predict(sess, softmax_tensor, img)
    letter_upper = letter.upper()

    print("Letter:", letter_upper, " Score:", score)
    print("Current word:", current_word)

    if letter_upper not in ('NOTHING', 'SPACE', 'DEL'):
        current_word += letter_upper
        speak_letter(letter)

    elif letter_upper in ('SPACE', 'DEL'):
        if len(current_word) > 0:
            speak_letter(current_word)
        current_word = ""

    elif letter_upper == 'NOTHING':
        pass

    else:
        print("UNEXPECTED INPUT:", letter_upper)


# Flags and counters — defined before the loop
time_counter = 0
captureFlag = False
realTime = True
spell_check = False

window_name = display.setup_display("Live Stream")

with tf.Session() as sess:
    softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')

    while True:
        keypress = cv2.waitKey(1)

        img = live_stream.read()[1]

        height, width = img.shape[:2]

        display.update_display(img, current_word, window_name)

        # Real-time mode: predict every 45 frames
        if time_counter % 45 == 0 and realTime:
            threading.Thread(target=process_letter, args=(sess, softmax_tensor, img.copy())).start()

        # 'C' pressed — switch to capture mode
        if keypress == ord('c'):
            captureFlag = True
            realTime = False

        # 'R' pressed — resume real-time mode
        if keypress == ord('r'):
            realTime = True

        # Capture mode: predict on demand
        if captureFlag:
            captureFlag = False
            threading.Thread(target=process_letter, args=(sess, softmax_tensor, img.copy())).start()

        # ESC pressed — exit
        if keypress == 27:
            break

        time_counter += 1

# Release resources
live_stream.release()
cv2.destroyAllWindows()