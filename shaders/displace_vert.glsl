#version 330 core
layout (location = 0) in vec2 aPos;
layout (location = 1) in vec2 aTexCoord;

out vec2 TexCoord;
uniform vec4 u_offset;
uniform float u_yrot;

void main() {
    vec2 pos = (aPos + vec2(1.0)) * 0.5;//map to 0 to 1
    pos = (pos * u_offset.zw);
    pos.x = pos.x + u_offset.x;
    pos.y = 1.0 - (pos.y + (u_offset.y));

    pos = pos * 2.0 - vec2(1.0);//map to -1 to 1

    vec3 pos3 = vec3(pos, 0.0);

    float theta = u_yrot;
    mat3 yRot = mat3(
        cos(theta), 0.0, sin(theta),
        0.0, 1.0, 0.0,
        -sin(theta), 0.0, cos(theta)
    );
    pos3 = yRot * pos3;



    gl_Position = vec4(pos3, 1.0);
    // gl_Position = vec4(pos, 0.0, 1.0);
    TexCoord = aTexCoord;
}
