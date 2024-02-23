#version 300 es
precision highp float;
uniform vec4 color;

uniform vec3 lightdir;
uniform vec3 lightcolor;
uniform mat4 mv;
uniform vec3 eye;

out vec4 fragColor;
in vec3 vnormal;
in vec3 normal2;

void main() {
    vec3 n = normalize(vnormal);
    vec3 n2 = normalize(normal2);
    float lambert = max(dot(n, mat3(mv) * lightdir), 0.0);
    float blinn = pow(max(dot(n, normalize(eye + mat3(mv) * lightdir)), 0.0), 150.0);
    vec3 d_color = n2.z < 0.7 ? vec3(0.6, 0.3, 0.3) : vec3(0.2, 0.6, 0.1) ;
    fragColor = vec4(color.rgb * (d_color * lambert) + (vec3(1,1,1) * blinn), color.a);
}