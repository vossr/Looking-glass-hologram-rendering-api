from OpenGL.GL import *
import bridge_api
import gl_utils
import atexit
import glfw
import cv2

device = bridge_api.get_device(0)

# vert = "#version 330 core\n" + device.shader.vertex_shader
# frag = "#version 330 core\n" + device.shader.fragment_shader

if not glfw.init():
    raise Exception("Failed to initialize GLFW")

def terminate():
    glfw.terminate()

atexit.register(terminate)

window_title = 'rendering_python_api'

def create_window():
    glfw.window_hint(glfw.DECORATED, glfw.FALSE)
    window = glfw.create_window(device.window.w, device.window.h, window_title, None, None)
    glfw.set_window_pos(window, device.window.x, device.window.y)
    if not window:
        glfw.terminate()
        raise Exception("Failed to create GLFW window")
    return window

window = create_window()
glfw.make_context_current(window)

quad_VAO = gl_utils.setup_quad_vertices()
quad_shader = gl_utils.create_shader_program(open('quad_texture_vert.glsl', 'r').read(), open('quad_texture_frag.glsl', 'r').read())
quilt_VAO = gl_utils.setup_quilt_vertices()
quilt_shader = gl_utils.create_shader_program(open('look_old_vert.glsl', 'r').read(), open('look_old_frag.glsl', 'r').read())
# quilt_shader = gl_utils.create_shader_program(open('look_vert.glsl', 'r').read(), open('look_frag.glsl', 'r').read())





def render_pass_quilt(texture_id):
    glClear(GL_COLOR_BUFFER_BIT)
    glUseProgram(quilt_shader)

    unused_uniforms = """
    glUniform1f(glGetUniformLocation(quilt_shader, "pitch"), device.shader.lenticular_pitch)
    glUniform1f(glGetUniformLocation(quilt_shader, "tilt"), device.shader.lenticular_tilt)
    glUniform1f(glGetUniformLocation(quilt_shader, "center"), device.shader.center_offset)
    glUniform1f(glGetUniformLocation(quilt_shader, "subp"), device.shader.subpixel_size)
    glUniform1f(glGetUniformLocation(quilt_shader, "displayAspect"), device.window.aspect_ratio)
    glUniform1f(glGetUniformLocation(quilt_shader, "quiltAspect"), device.quilt.tiling_dimension_x / device.quilt.tiling_dimension_y)
    # glUniform1f(glGetUniformLocation(quilt_shader, "quiltAspect"), 1.0)
    
    glUniform1i(glGetUniformLocation(quilt_shader, "invView"), device.shader.should_invert)
    glUniform1i(glGetUniformLocation(quilt_shader, "ri"), device.shader.red_index)
    glUniform1i(glGetUniformLocation(quilt_shader, "bi"), device.shader.blue_index)
    glUniform1i(glGetUniformLocation(quilt_shader, "overscan"), 1)
    glUniform1i(glGetUniformLocation(quilt_shader, "quiltInvert"), 0)
    glUniform1i(glGetUniformLocation(quilt_shader, "debug"), 0)

    quilt_image_count = device.quilt.tiling_dimension_x * device.quilt.tiling_dimension_y
    glUniform3fv(glGetUniformLocation(quilt_shader, "tile"), 1, (device.quilt.tiling_dimension_x, device.quilt.tiling_dimension_y, quilt_image_count))
    tileWidth = round(device.window.w / device.quilt.tiling_dimension_x)
    tileHeight = round(device.window.y / device.quilt.tiling_dimension_y)
    quiltViewPortion = (
        device.quilt.tiling_dimension_x * tileWidth * device.window.w,
        device.quilt.tiling_dimension_y * tileHeight * device.window.h
    )
    glUniform2fv(glGetUniformLocation(quilt_shader, "viewPortion"), 1, quiltViewPortion)
    # glUniform1i(glGetUniformLocation(quilt_shader, "screenTex"), texture_id)
    """

    glUniform1f(glGetUniformLocation(quilt_shader, "pitch"), device.shader.lenticular_pitch)
    glUniform1f(glGetUniformLocation(quilt_shader, "tilt"), device.shader.lenticular_tilt)
    glUniform1f(glGetUniformLocation(quilt_shader, "center"), device.shader.center_offset)
    glUniform1f(glGetUniformLocation(quilt_shader, "invView"), device.shader.should_invert)
    glUniform1f(glGetUniformLocation(quilt_shader, "subp"), device.shader.subpixel_size)
    quilt_image_count = device.quilt.tiling_dimension_x * device.quilt.tiling_dimension_y
    glUniform1f(glGetUniformLocation(quilt_shader, "numViews"), quilt_image_count)
    glUniform1f(glGetUniformLocation(quilt_shader, "tilesX"), device.quilt.tiling_dimension_x)
    glUniform1f(glGetUniformLocation(quilt_shader, "tilesY"), device.quilt.tiling_dimension_y)

    tileWidth = round(device.window.w / device.quilt.tiling_dimension_x)
    tileHeight = round(device.window.y / device.quilt.tiling_dimension_y)
    quiltViewPortion = (
        device.quilt.tiling_dimension_x * tileWidth * device.window.w,
        device.quilt.tiling_dimension_y * tileHeight * device.window.h
    )
    quiltViewPortion = (
        1.0, 1.0
    )
    glUniform2fv(glGetUniformLocation(quilt_shader, "quiltViewPortion"), 1, quiltViewPortion)
    # glUniform1i(glGetUniformLocation(quilt_shader, "u_texture"), texture_id)


    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glBindVertexArray(quilt_VAO)
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

    glfw.swap_buffers(window)
    glfw.poll_events()



def render_pass_quad(texture_id):
    glClear(GL_COLOR_BUFFER_BIT)

    glUseProgram(quad_shader)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glBindVertexArray(quad_VAO)
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

    glfw.swap_buffers(window)
    glfw.poll_events()



def _generate_lenticular_projection(quilt):
    lent = 0
    return lent

def _generate_quilt_from_rgbd(rgb_depth):
    # quilt_image_count
    quilt = 0
    return quilt




def show_lenticular_projection(lent):
    texture_id = gl_utils.load_texture_from_cv_image(lent)
    render_pass_quad(texture_id)
    glDeleteTextures(1, [texture_id])

def show_quilt(quilt):
    # Vertically flip the image
    quilt = cv2.flip(quilt, 0)

    texture_id = gl_utils.load_texture_from_cv_image(quilt)
    render_pass_quilt(texture_id)
    glDeleteTextures(1, [texture_id])
    # lent = _generate_lenticular_projection(quilt)
    # show_lenticular_projection(lent)
    # show_lenticular_projection

def show_rgb_depth(rgb_depth):
    # quilt = _generate_quilt_from_rgbd(rgb_depth)
    # show_quilt(quilt)
    pass
