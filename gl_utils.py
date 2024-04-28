from OpenGL.GL import *
import numpy as np
import cv2

def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        error = glGetShaderInfoLog(shader).decode()
        print('Shader compilation failed:', error)
        glDeleteShader(shader)
        return None
    return shader

def create_shader_program(vertex_source, fragment_source):
    vertex_shader = compile_shader(vertex_source, GL_VERTEX_SHADER)
    fragment_shader = compile_shader(fragment_source, GL_FRAGMENT_SHADER)

    if vertex_shader is None or fragment_shader is None:
        return None

    shader_program = glCreateProgram()
    glAttachShader(shader_program, vertex_shader)
    glAttachShader(shader_program, fragment_shader)
    glLinkProgram(shader_program)

    if not glGetProgramiv(shader_program, GL_LINK_STATUS):
        error = glGetProgramInfoLog(shader_program).decode()
        print('Shader program linking failed:', error)
        glDeleteProgram(shader_program)
        if vertex_shader:
            glDeleteShader(vertex_shader)
        if fragment_shader:
            glDeleteShader(fragment_shader)
        return None

    glDetachShader(shader_program, vertex_shader)
    glDetachShader(shader_program, fragment_shader)
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)

    return shader_program

def load_texture_from_cv_image(cv_image):
    image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)

    textureID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, textureID)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    height, width, channels = image.shape
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image)

    glGenerateMipmap(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, 0)
    return textureID

def setup_vertex_data():
    vertices = np.array([
        # Positions       # Texture Coords
        -0.5, -0.5, 0.0,  0.0, 0.0,  # Bottom left
         0.5, -0.5, 0.0,  1.0, 0.0,  # Bottom right
        -0.5,  0.5, 0.0,  0.0, 1.0,  # Top left
         0.5,  0.5, 0.0,  1.0, 1.0   # Top right
    ], dtype=np.float32)

    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)

    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * vertices.itemsize, None)
    glEnableVertexAttribArray(0)

    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * vertices.itemsize, ctypes.c_void_p(3 * vertices.itemsize))
    glEnableVertexAttribArray(1)
    return VAO
