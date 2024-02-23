#version 300 es
precision highp float;
uniform vec4 color;

uniform vec3 lightdir;
uniform vec3 lightcolor;
uniform mat4 mv;
uniform vec3 eye;
uniform float seconds;

out vec4 fragColor;
in vec3 vnormal;
in vec4 pos;

void main() {
    float val = pos.z;
    vec3 n = normalize(vnormal);
    float lambert = max(dot(n, mat3(mv) * lightdir), 0.0);
    float blinn = pow(max(dot(n, normalize(eye + mat3(mv) * lightdir)), 0.0), 150.0);
    vec4 color_grad = val < -0.357 ? vec4(1.0, (val - -0.5)/ (-0.357 - -0.5), 0.0, 1.0) :
    val < -0.214 ? vec4((-0.214 - val) / (-0.214 - -0.357), 1.0, 0.0, 1.0) :
    val < -0.071 ? vec4(0.0, 1.0, (val - -0.214) / (-0.071- -0.214), 1.0) : 
    val < 0.071 ? vec4(0.0, (0.071 - val)/(0.071 - -0.071), 1.0, 1.0) :
    val < 0.214 ? vec4((val - 0.071)/(0.214 - 0.071), 0.0, 1.0, 1.0) : 
    val < 0.357 ?vec4(1.0, 0.0, (0.357 - val)/(0.357 - 0.214), 1.0) : vec4(1.0, 0.0, (val - 0.357)/ (0.5 - 0.357), 1.0);
    fragColor = vec4((color_grad.rgb * lambert) + (vec3(1,1,1) * blinn), 1);
}
