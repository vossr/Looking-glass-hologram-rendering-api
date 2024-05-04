#version 330 core
in vec2 TexCoord;
out vec4 FragColor;

uniform float u_horizontalOffset;
uniform sampler2D u_rgb;
uniform sampler2D u_depth;

void main()
{
    float depth = texture(u_depth, TexCoord).r;

    // texture2D(texture, p + (texture2D(map, p).rb) * amp);

    vec2 displacedTexCoord = TexCoord + vec2(depth * u_horizontalOffset, 0.0);

    FragColor = texture(u_rgb, displacedTexCoord);
}
