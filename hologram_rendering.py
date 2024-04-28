import bridge_api
import cv2

device = bridge_api.get_device(0)
x_position = device.window.x
y_position = device.window.y
width = device.window.w
height = device.window.h
quilt_image_count = device.quilt.tiling_dimension_x * device.quilt.tiling_dimension_y

window_name = 'looking_glass_rendering_python_api'
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL | cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.moveWindow(window_name, x_position, y_position)
cv2.resizeWindow(window_name, width, height)

def _generate_lenticular_projection(quilt):
    lent = 0
    return lent

def _generate_quilt_from_rgbd(rgb_depth):
    # quilt_image_count
    quilt = 0
    return quilt





def show_lenticular_projection(lent):
    cv2.imshow(window_name, lent)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        exit(0)

def show_quilt(quilt):
    lent = _generate_lenticular_projection(quilt)
    show_lenticular_projection(lent)

def show_rgb_depth(rgb_depth):
    quilt = _generate_quilt_from_rgbd(rgb_depth)
    show_quilt(quilt)
