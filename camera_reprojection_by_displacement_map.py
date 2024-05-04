from OpenGL.GL import *
import numpy as np
import gl_utils

quad_VAO = 0
quad_shader = 0
disp_VAO = 0
disp_shader = 0

def init():
    global quad_VAO
    global quad_shader
    global disp_VAO
    global disp_shader
    # quad_VAO = gl_utils.setup_quad_vertices()
    # quad_shader = gl_utils.create_shader_program(open('shaders/quad_texture_vert.glsl', 'r').read(), open('shaders/quad_texture_frag.glsl', 'r').read())
    disp_VAO = gl_utils.setup_displace_vertices()
    disp_shader = gl_utils.create_shader_program(open('shaders/displace_vert.glsl', 'r').read(), open('shaders/displace_frag.glsl', 'r').read())


def render(rgb_tex_id, depth_tex_id, xywh):
    glClear(GL_COLOR_BUFFER_BIT)

    # glUseProgram(quad_shader)
    glUseProgram(disp_shader)

    # glUniformMatrix4fv(glGetUniformLocation(disp_shader, "orthoMatrix"), 1, GL_FALSE, ortho_matrix)
    glUniform4fv(glGetUniformLocation(disp_shader, "u_offset"), 1, xywh)
    glUniform1f(glGetUniformLocation(disp_shader, "u_horizontalOffset"), 0.0)

    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, rgb_tex_id)
    glActiveTexture(GL_TEXTURE1)
    glBindTexture(GL_TEXTURE_2D, depth_tex_id)
    # glBindVertexArray(quad_VAO)
    glBindVertexArray(disp_VAO)
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
