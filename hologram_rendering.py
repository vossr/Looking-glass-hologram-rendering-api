import camera_reprojection_by_displacement_map as displace
from OpenGL.GL import *
import bridge_api
import gl_utils
import atexit
import glfw
import cv2
import os

install_dir = os.path.dirname(os.path.abspath(__file__))

device = bridge_api.get_device(0)
if device.info.bridge_core_version != "0.1.1":
    print("Warning: Untested bridge version")
if device.info.device_type != "portrait":
    print("Warning: Untested device")

if not glfw.init():
    raise Exception("Failed to initialize GLFW")

def _terminate():
    glfw.terminate()

atexit.register(_terminate)

window_title = 'rendering_python_api'

def _create_window():
    glfw.window_hint(glfw.DECORATED, glfw.FALSE)
    window = glfw.create_window(device.window.w, device.window.h, window_title, None, None)
    glfw.set_window_pos(window, device.window.x, device.window.y)
    if not window:
        glfw.terminate()
        raise Exception("Failed to create GLFW window")
    return window

window = _create_window()
glfw.make_context_current(window)

displace.init()
quad_VAO = gl_utils.setup_quad_vertices()
quad_shader = gl_utils.create_shader_program(open(install_dir + '/shaders/quad_texture_vert.glsl', 'r').read(), open(install_dir + '/shaders/quad_texture_frag.glsl', 'r').read())
quilt_VAO = gl_utils.setup_quilt_vertices()
quilt_shader_old = 0
# quilt_shader_old = gl_utils.create_shader_program(open(install_dir + '/shaders/look_old_vert.glsl', 'r').read(), open(install_dir + '/shaders/look_old_frag.glsl', 'r').read())

vert = "#version 330 core\n" + device.shader.vertex_shader
frag = "#version 330 core\n" + device.shader.fragment_shader
quilt_shader = gl_utils.create_shader_program(vert, frag)


def _render_pass_quilt_old_webgl_shader(texture_id):
    glClear(GL_COLOR_BUFFER_BIT)
    glUseProgram(quilt_shader_old)

    glUniform1f(glGetUniformLocation(quilt_shader_old, "pitch"), device.shader.lenticular_pitch)
    glUniform1f(glGetUniformLocation(quilt_shader_old, "tilt"), device.shader.lenticular_tilt)
    glUniform1f(glGetUniformLocation(quilt_shader_old, "center"), device.shader.center_offset)
    glUniform1f(glGetUniformLocation(quilt_shader_old, "invView"), device.shader.should_invert)
    glUniform1f(glGetUniformLocation(quilt_shader_old, "subp"), device.shader.subpixel_size)
    quilt_image_count = device.quilt.tiling_dimension_x * device.quilt.tiling_dimension_y
    glUniform1f(glGetUniformLocation(quilt_shader_old, "numViews"), quilt_image_count)
    glUniform1f(glGetUniformLocation(quilt_shader_old, "tilesX"), device.quilt.tiling_dimension_x)
    glUniform1f(glGetUniformLocation(quilt_shader_old, "tilesY"), device.quilt.tiling_dimension_y)

    tileWidth = round(device.window.w / device.quilt.tiling_dimension_x)
    tileHeight = round(device.window.h / device.quilt.tiling_dimension_y)
    quiltViewPortion = (
        device.quilt.tiling_dimension_x * tileWidth * device.window.w,
        device.quilt.tiling_dimension_y * tileHeight * device.window.h
    )
    quiltViewPortion = (
        1.0, 1.0
    )
    glUniform2fv(glGetUniformLocation(quilt_shader_old, "quiltViewPortion"), 1, quiltViewPortion)
    # glUniform1i(glGetUniformLocation(quilt_shader_old, "u_texture"), texture_id)

    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glBindVertexArray(quilt_VAO)
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

    glfw.swap_buffers(window)
    glfw.poll_events()


def _render_pass_quilt(texture_id, flip=False):
    glClear(GL_COLOR_BUFFER_BIT)
    glUseProgram(quilt_shader)

    glUniform1f(glGetUniformLocation(quilt_shader, "pitch"), device.shader.lenticular_pitch)
    glUniform1f(glGetUniformLocation(quilt_shader, "tilt"), device.shader.lenticular_tilt)
    glUniform1f(glGetUniformLocation(quilt_shader, "center"), device.shader.center_offset)
    glUniform1i(glGetUniformLocation(quilt_shader, "invView"), device.shader.should_invert)
    glUniform1f(glGetUniformLocation(quilt_shader, "subp"), device.shader.subpixel_size)
    glUniform1f(glGetUniformLocation(quilt_shader, "displayAspect"), device.window.aspect_ratio)

    #why this in wrong order h / w
    # glUniform1f(glGetUniformLocation(quilt_shader, "quiltAspect"), device.quilt.tiling_dimension_y / device.quilt.tiling_dimension_x)
    # glUniform1f(glGetUniformLocation(quilt_shader, "quiltAspect"), device.quilt.tiling_dimension_x / device.quilt.tiling_dimension_y)
    glUniform1f(glGetUniformLocation(quilt_shader, "quiltAspect"), 1.0)

    glUniform1i(glGetUniformLocation(quilt_shader, "ri"), device.shader.red_index)
    glUniform1i(glGetUniformLocation(quilt_shader, "bi"), device.shader.blue_index)



    quilt_image_count = device.quilt.tiling_dimension_x * device.quilt.tiling_dimension_y
    glUniform3fv(glGetUniformLocation(quilt_shader, "tile"), 1, (device.quilt.tiling_dimension_x, device.quilt.tiling_dimension_y, quilt_image_count))

    tileWidth = round(device.window.w / device.quilt.tiling_dimension_x)
    tileHeight = round(device.window.h / device.quilt.tiling_dimension_y)
    quiltViewPortion = (
        device.quilt.tiling_dimension_x * tileWidth * device.window.w,
        device.quilt.tiling_dimension_y * tileHeight * device.window.h
    )
    quiltViewPortion = (
        1.0, 1.0
    )
    if flip:
        quiltViewPortion = (quiltViewPortion[0], quiltViewPortion[1] * -1.0)
    glUniform2fv(glGetUniformLocation(quilt_shader, "viewPortion"), 1, quiltViewPortion)
    glUniform1i(glGetUniformLocation(quilt_shader, "overscan"), 1)
    glUniform1i(glGetUniformLocation(quilt_shader, "quiltInvert"), 0)
    glUniform1i(glGetUniformLocation(quilt_shader, "debug"), 0)


    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glBindVertexArray(quilt_VAO)
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

    glfw.swap_buffers(window)
    glfw.poll_events()

def _render_pass_quad(texture_id):
    glClear(GL_COLOR_BUFFER_BIT)

    glUseProgram(quad_shader)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glBindVertexArray(quad_VAO)
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

    glfw.swap_buffers(window)
    glfw.poll_events()

def render_image(lent):
    try:
        texture_id = gl_utils.load_texture_from_cv_image(lent)
        _render_pass_quad(texture_id)
        glDeleteTextures(1, [texture_id])
    except KeyboardInterrupt:
        exit(0)

def render_quilt(quilt):
    try:
        texture_id = gl_utils.load_texture_from_cv_image(quilt)
        _render_pass_quilt(texture_id, flip=True)
        # _render_pass_quilt_old_webgl_shader(texture_id)
        glDeleteTextures(1, [texture_id])
        # lent = _generate_lenticular_projection(quilt)
        # show_lenticular_projection(lent)
        # show_lenticular_projection
    except KeyboardInterrupt:
        exit(0)

rgbd_target_texture_id = gl_utils.create_texture(device.window.w, device.window.h)
rgbd_target = gl_utils.create_framebuffer(rgbd_target_texture_id)

quilt_resw = int(device.window.w / device.quilt.tiling_dimension_x)
quilt_resh = int(device.window.h / device.quilt.tiling_dimension_y)
if quilt_resw % 2 != 0:
    quilt_resw += 1
if quilt_resh % 2 != 0:
    quilt_resh += 1
maxw = quilt_resw * 2
maxh = quilt_resh * 2

def crop_image_if_larger(img, maxw, maxh):
    height, width = img.shape[:2]
    
    if width > maxw or height > maxh:
        ratio_w = maxw / width
        ratio_h = maxh / height
        ratio = min(ratio_w, ratio_h)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        resized_img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
        return resized_img
    return img
  
def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))

def render_rgb_depth(rgb, depth, offset_scale, rot_max_rad):
    depth = cv2.resize(depth, (quilt_resw, quilt_resh))
    rgb = crop_image_if_larger(rgb, maxw, maxh)

    try:
        glBindFramebuffer(GL_FRAMEBUFFER, rgbd_target)
        glViewport(0, 0, device.window.w, device.window.h)

        rgb_tex_id = gl_utils.load_texture_from_cv_image(rgb)
        #TODO use GL_R32F
        depth_tex_id = gl_utils.load_texture_from_cv_image(depth)

        tilecount = device.quilt.tiling_dimension_x * device.quilt.tiling_dimension_y
        quilt_widthp = 1.0 / device.quilt.tiling_dimension_x
        quilt_heightp = 1.0 / device.quilt.tiling_dimension_y 
        i = 0
        for qy in range(device.quilt.tiling_dimension_y):
            for qx in range(device.quilt.tiling_dimension_x):
                xx = qx / device.quilt.tiling_dimension_x
                yy = qy / device.quilt.tiling_dimension_y
                xywh = (xx, 1.0 - yy - quilt_heightp, quilt_widthp, quilt_heightp)
                hoffset = (i / tilecount) - 0.5
                displace.render(rgb_tex_id, depth_tex_id, xywh, hoffset * offset_scale, hoffset * rot_max_rad)
                i += 1

        glDeleteTextures(1, [rgb_tex_id])
        glDeleteTextures(1, [depth_tex_id])
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        _render_pass_quilt(rgbd_target_texture_id, flip=False)
    except KeyboardInterrupt:
        exit(0)
