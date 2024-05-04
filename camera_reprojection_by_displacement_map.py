from OpenGL.GL import *
import numpy as np
import gl_utils

quad_VAO = 0
quad_shader = 0
disp_shader = 0

def init():
    global quad_VAO
    global quad_shader
    global disp_shader
    quad_VAO = gl_utils.setup_quad_vertices()
    quad_shader = gl_utils.create_shader_program(open('shaders/quad_texture_vert.glsl', 'r').read(), open('shaders/quad_texture_frag.glsl', 'r').read())
    disp_shader = gl_utils.create_shader_program(open('shaders/displace_vert.glsl', 'r').read(), open('shaders/displace_frag.glsl', 'r').read())

def orthographic_projection(left, right, bottom, top, near=-1, far=1):
    return np.array([
        [2 / (right - left), 0, 0, -(right + left) / (right - left)],
        [0, 2 / (top - bottom), 0, -(top + bottom) / (top - bottom)],
        [0, 0, -2 / (far - near), -(far + near) / (far - near)],
        [0, 0, 0, 1]
    ], dtype=np.float32)

def render(rgb_tex_id, depth_tex_id):
    glClear(GL_COLOR_BUFFER_BIT)

    # glUseProgram(quad_shader)
    glUseProgram(disp_shader)

    view_left = 0
    view_right = 1
    view_bot = 0
    view_top = 1

    view_left = -1 + 2 * view_left
    view_right = -1 + 2 * view_right
    view_top = -1 + 2 * view_top
    view_bot = -1 + 2 * view_bot
    ortho_matrix = orthographic_projection(view_left, view_right, view_bot, view_top)

    glUniformMatrix4fv(glGetUniformLocation(disp_shader, "orthoMatrix"), 1, GL_FALSE, ortho_matrix)
    glUniform1f(glGetUniformLocation(disp_shader, "u_horizontalOffset"), 0.1)

    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, rgb_tex_id)
    glActiveTexture(GL_TEXTURE1)
    glBindTexture(GL_TEXTURE_2D, depth_tex_id)
    glBindVertexArray(quad_VAO)
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
