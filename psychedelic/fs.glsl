#version 300 es
precision highp float;
uniform float seconds;
in vec4 pos;
out vec4 color;
void main() {
    float x = pos.x;
    float y = pos.y;
    color = vec4(cos((pow(x, 4.0) + 3.0 * pow(x, 3.0) + 4.0 * pow(x, 2.0) - y) * (seconds * 3.0))
    , sin((pow(x, 3.0) + 4.0 * pow(x, 2.0) + x + y) * (seconds * 2.0))
    , cos((pow(x, 2.0) - pow(y, 2.0) * (seconds * 5.0)) * seconds)    
    ,1.0);
}
