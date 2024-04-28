from OpenGL.GL import *
import bridge_api
import gl_utils
import atexit
import glfw

device = bridge_api.get_device(0)
quilt_image_count = device.quilt.tiling_dimension_x * device.quilt.tiling_dimension_y

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

VAO = gl_utils.setup_vertex_data()
quad_shader = gl_utils.create_shader_program(open('quad_texture_vert.glsl', 'r').read(), open('quad_texture_frag.glsl', 'r').read())
# lenticular_shader = gl_utils.create_shader_program(open('look_vert.glsl', 'r').read(), open('look_frag.glsl', 'r').read())





def render_frame(texture_id):
    glClear(GL_COLOR_BUFFER_BIT)

    glUseProgram(quad_shader)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glBindVertexArray(VAO)
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
    render_frame(texture_id)
    glDeleteTextures(1, [texture_id])

def show_quilt(quilt):
    # lent = _generate_lenticular_projection(quilt)
    # show_lenticular_projection(lent)
    pass

def show_rgb_depth(rgb_depth):
    # quilt = _generate_quilt_from_rgbd(rgb_depth)
    # show_quilt(quilt)
    pass
