from OpenGL.GL import *
import numpy as np
import gl_utils
import os

install_dir = os.path.dirname(os.path.abspath(__file__))

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
    # quad_shader = gl_utils.create_shader_program(open(install_dir + '/shaders/quad_texture_vert.glsl', 'r').read(), open(install_dir + '/shaders/quad_texture_frag.glsl', 'r').read())
    disp_VAO = gl_utils.setup_displace_vertices()
    disp_shader = gl_utils.create_shader_program(open(install_dir + '/shaders/displace_vert.glsl', 'r').read(), open(install_dir + '/shaders/displace_frag.glsl', 'r').read())


def render(rgb_tex_id, depth_tex_id, xywh, horizontal_offset):

    # glUseProgram(quad_shader)
    glUseProgram(disp_shader)

    # glUniformMatrix4fv(glGetUniformLocation(disp_shader, "orthoMatrix"), 1, GL_FALSE, ortho_matrix)
    glUniform4fv(glGetUniformLocation(disp_shader, "u_offset"), 1, xywh)
    glUniform1f(glGetUniformLocation(disp_shader, "u_horizontalOffset"), horizontal_offset)

    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, rgb_tex_id)
    glUniform1i(glGetUniformLocation(disp_shader, "u_rgb"), 0)
    glActiveTexture(GL_TEXTURE1)
    glBindTexture(GL_TEXTURE_2D, depth_tex_id)
    glUniform1i(glGetUniformLocation(disp_shader, "u_depth"), 1)
    # glBindVertexArray(quad_VAO)
    glBindVertexArray(disp_VAO)
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
