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

def create_framebuffer(texture_id):
    fbo_id = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, fbo_id)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture_id, 0)
    if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        raise RuntimeError("Framebuffer is not complete")
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    return fbo_id

def create_texture(width, height):
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
    glBindTexture(GL_TEXTURE_2D, 0)
    return texture_id

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

    # glGenerateMipmap(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, 0)
    return textureID

def setup_quad_vertices():
    vertices = np.array([
        # Positions   # Texture Coords
        -1.0, -1.0,   0.0, 1.0,
         1.0, -1.0,   1.0, 1.0,
        -1.0,  1.0,   0.0, 0.0,
         1.0,  1.0,   1.0, 0.0 
    ], dtype=np.float32)

    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)

    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * vertices.itemsize, None)
    glEnableVertexAttribArray(0)

    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * vertices.itemsize, ctypes.c_void_p(2 * vertices.itemsize))
    glEnableVertexAttribArray(1)
    return VAO

def setup_displace_vertices():
    vertices = np.array([
        # Positions   # Texture Coords
        -1.0, -1.0,   0.0, 0.0,
         1.0, -1.0,   1.0, 0.0,
        -1.0,  1.0,   0.0, 1.0,
         1.0,  1.0,   1.0, 1.0 
    ], dtype=np.float32)

    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)

    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * vertices.itemsize, None)
    glEnableVertexAttribArray(0)

    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * vertices.itemsize, ctypes.c_void_p(2 * vertices.itemsize))
    glEnableVertexAttribArray(1)
    return VAO

def setup_quilt_vertices():
    vertices = np.array([
        -1.0, -1.0,  # Bottom left
         1.0, -1.0,  # Bottom right
        -1.0,  1.0,  # Top left
         1.0,  1.0   # Top right
    ], dtype=np.float32)

    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)

    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * vertices.itemsize, None)
    glEnableVertexAttribArray(0)
    return VAO

def create_grid_vao(width, height):
    vertices = []
    uvs = []
    
    for y in range(height):
        for x in range(width):
            # Coordinates normalized between -1 and 1
            x0 = x / width * 2 - 1
            x1 = (x + 1) / width * 2 - 1
            y0 = y / height * 2 - 1
            y1 = (y + 1) / height * 2 - 1
            
            quad_vertices = [
                x0, y0, 0, x1, y0, 0, x1, y1, 0,
                x0, y0, 0, x1, y1, 0, x0, y1, 0
            ]
            vertices.extend(quad_vertices)
            
            quad_uvs = [
                0, 0, 1, 0, 1, 1,
                0, 0, 1, 1, 0, 1
            ]
            uvs.extend(quad_uvs)
    
    vertices = np.array(vertices, dtype=np.float32)
    uvs = np.array(uvs, dtype=np.float32)
    
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    
    vertex_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vertex_vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)
    
    uv_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, uv_vbo)
    glBufferData(GL_ARRAY_BUFFER, uvs.nbytes, uvs, GL_STATIC_DRAW)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(1)
    
    glBindVertexArray(0)
    return vao, vertex_vbo, uv_vbo
