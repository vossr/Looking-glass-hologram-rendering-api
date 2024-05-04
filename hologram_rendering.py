import camera_reprojection_by_displacement_map as displace
from OpenGL.GL import *
import bridge_api
import gl_utils
import atexit
import glfw
import cv2

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
    # glfw.set_window_pos(window, device.window.x, device.window.y)
    if not window:
        glfw.terminate()
        raise Exception("Failed to create GLFW window")
    return window

window = _create_window()
glfw.make_context_current(window)

displace.init()
quad_VAO = gl_utils.setup_quad_vertices()
quad_shader = gl_utils.create_shader_program(open('shaders/quad_texture_vert.glsl', 'r').read(), open('shaders/quad_texture_frag.glsl', 'r').read())
quilt_VAO = gl_utils.setup_quilt_vertices()
quilt_shader_old = 0
# quilt_shader_old = gl_utils.create_shader_program(open('shaders/look_old_vert.glsl', 'r').read(), open('shaders/look_old_frag.glsl', 'r').read())

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


def _render_pass_quilt(texture_id):
    glClear(GL_COLOR_BUFFER_BIT)
    glUseProgram(quilt_shader)

    glUniform1f(glGetUniformLocation(quilt_shader, "pitch"), device.shader.lenticular_pitch)
    glUniform1f(glGetUniformLocation(quilt_shader, "tilt"), device.shader.lenticular_tilt)
    glUniform1f(glGetUniformLocation(quilt_shader, "center"), device.shader.center_offset)
    glUniform1i(glGetUniformLocation(quilt_shader, "invView"), device.shader.should_invert)
    glUniform1f(glGetUniformLocation(quilt_shader, "subp"), device.shader.subpixel_size)
    glUniform1f(glGetUniformLocation(quilt_shader, "displayAspect"), device.window.aspect_ratio)

    #why this in wrong order h / w
    glUniform1f(glGetUniformLocation(quilt_shader, "quiltAspect"), device.quilt.tiling_dimension_y / device.quilt.tiling_dimension_x)
    # glUniform1f(glGetUniformLocation(quilt_shader, "quiltAspect"), device.quilt.tiling_dimension_x / device.quilt.tiling_dimension_y)
    # glUniform1f(glGetUniformLocation(quilt_shader, "quiltAspect"), 1.0)

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
        1.0, -1.0
    )
    glUniform2fv(glGetUniformLocation(quilt_shader, "viewPortion"), 1, quiltViewPortion)
    glUniform1i(glGetUniformLocation(quilt_shader, "overscan"), 0)
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
        _render_pass_quilt(texture_id)
        # _render_pass_quilt_old_webgl_shader(texture_id)
        glDeleteTextures(1, [texture_id])
        # lent = _generate_lenticular_projection(quilt)
        # show_lenticular_projection(lent)
        # show_lenticular_projection
    except KeyboardInterrupt:
        exit(0)

def render_rgb_depth(rgb, depth):
    try:
        rgb_tex_id = gl_utils.load_texture_from_cv_image(rgb)
        #TODO use GL_R32F
        depth_tex_id = gl_utils.load_texture_from_cv_image(depth)

        #so loop all the cameras
            # render to a section of the render target
        displace.render(rgb_tex_id, depth_tex_id)

        glDeleteTextures(2, [rgb_tex_id, depth_tex_id])

        glfw.swap_buffers(window)
        glfw.poll_events()
    except KeyboardInterrupt:
        exit(0)
