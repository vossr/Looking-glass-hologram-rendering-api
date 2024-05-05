import hologram_rendering
import numpy as np
import keyboard
import sys
import cv2

def split_image_vertically(image):
    height, width = image.shape[:2]
    midpoint = width // 2
    left = image[:, :midpoint]
    right = image[:, midpoint:]
    return left, right

def fix_aspect_ratio(img):
    height, width, channels = img.shape
    wanted_width = int(height * (1536 / 2048))
    if wanted_width % 2 != 0:
        wanted_width += 1
    
    delta_width = wanted_width - width
    left_pad = right_pad = max(delta_width // 2, 0)
    if delta_width % 2 != 0:
        right_pad += 1

    if delta_width > 0:
        new_image = np.full((height, wanted_width, channels), (0, 0, 0), dtype=np.uint8)
        new_image[:, left_pad:left_pad + width] = img
    else:
        crop_start = -left_pad
        crop_end = width + left_pad
        new_image = img[:, crop_start:crop_end]
    return new_image



cap = cv2.VideoCapture(sys.argv[1])
fps = cap.get(cv2.CAP_PROP_FPS)
delay = int(1000 / fps * 0.8)

horiz = 0.3
rot = 0.6

def on_key_press(event):
    global horiz
    global rot
    if event.name == 'w':
        horiz += 0.1
        print("horiz", horiz)
    if event.name == 's':
        horiz -= 0.1
        print("horiz", horiz)
    if event.name == 'a':
        rot -= 0.1
        print("rot", rot)
    if event.name == 'd':
        rot += 0.1
        print("rot", rot)
keyboard.on_press(on_key_press)


while True:
    ret, frame = cap.read()

    rgb, depth = split_image_vertically(frame)
    rgb = fix_aspect_ratio(rgb)
    depth = fix_aspect_ratio(depth)
    hologram_rendering.render_rgb_depth(rgb, depth, horiz, rot)

    key = cv2.waitKey(delay)

# image_path = 'test_data/quilt_background.png'
# image = cv2.imread(image_path)
# while True:
#     hologram_rendering.render_quilt(image)
#     # hologram_rendering.render_image(image)
