
import numpy as np
import cv2

def create_color_image(color, w, h):
    image = np.zeros((h, w, 3), dtype=np.uint8)
    image[:] = color
    return image

def create_random_color_image(w, h):
    color = tuple(np.random.randint(0, 256, size=3))
    image = np.zeros((h, w, 3), dtype=np.uint8)
    image[:] = color
    return image

def add_text_to_image(img, text, font_scale=3, font_color=(255, 0, 0), thickness=2):
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    text_x = (img.shape[1] - text_size[0]) // 2
    text_y = (img.shape[0] + text_size[1]) // 2
    cv2.putText(img, text, (text_x, text_y), font, font_scale, font_color, thickness, cv2.LINE_AA)
    return img

def make_grid(images, rows, cols):
    h, w, _ = images[0].shape
    grid = np.zeros((h * rows, w * cols, 3), dtype=np.uint8)

    for idx, img in enumerate(images):
        # row = idx // cols
        row = (rows - 1) - (idx // cols)  # inverse the row order
        col = idx % cols
        grid[row*h:(row+1)*h, col*w:(col+1)*w, :] = img

    return grid

def gen_quilt_numbers():
    images = []
    for i in range(6 * 8):
        quilt_w = 192
        quilt_h = 341
        rng_img = create_random_color_image(quilt_w, quilt_h)
        rng_img = add_text_to_image(rng_img, str(i))
        images.append(rng_img)

    img_grid = make_grid(images, 6, 8)
    cv2.imwrite("quilt_numbers.png", img_grid)

gen_quilt_numbers()

def lerp_color(c1, c2, n):
    if not (0 <= n <= 1):
        raise ValueError("n must be between 0 and 1")

    r = int(c1[0] + (c2[0] - c1[0]) * n)
    g = int(c1[1] + (c2[1] - c1[1]) * n)
    b = int(c1[2] + (c2[2] - c1[2]) * n)
    return (r, g, b)

def overlay_image(background, overlay):
    resized_overlay = cv2.resize(overlay, (background.shape[1], background.shape[0]), interpolation=cv2.INTER_AREA)

    alpha_overlay = resized_overlay[:, :, 3] / 255.0
    alpha_background = 1.0 - alpha_overlay

    for c in range(0, 3):
        background[:, :, c] = (alpha_overlay * resized_overlay[:, :, c] +
                                alpha_background * background[:, :, c])

def gen_quilt_background():
    color1 = tuple([245, 34, 129])
    color2 = tuple([38, 9, 145])

    card_img = cv2.imread("card.png", cv2.IMREAD_UNCHANGED)

    images = []
    for i in range(6 * 8):
        quilt_w = 192
        quilt_h = 341
        progress = i / (6 * 8)
        rng_img = create_color_image(lerp_color(color1, color2, progress), quilt_w, quilt_h)
        overlay_image(rng_img, card_img)
        images.append(rng_img)

    img_grid = make_grid(images, 6, 8)
    cv2.imwrite("quilt_background.png", img_grid)

gen_quilt_background()
