#version 300 es

layout(location = 0) in vec4 position;
layout(location = 1) in vec4 color;
uniform mat4 rot;
uniform mat4 move;
uniform float seconds;
out vec4 vColor;
void main() {
    vColor = color;
    gl_Position = gl_VertexID == 0 ? vec4(position.x * 0.2 - 0.1 + 0.05 * sin(seconds  * 5.0), position.y * 0.2 - 0.5 + 0.02 * sin(seconds  * 10.0), position.zw): 
    gl_VertexID == 1 ? vec4(position.x * 0.2 - 0.1 + 0.05 * sin(seconds  *6.0), position.y * 0.2 - 0.5, position.zw): 
    gl_VertexID == 2 ? vec4(position.x * 0.2 - 0.1 + 0.05 * sin(seconds  * 10.0), position.y * 0.2 - 0.5 + 0.05 * cos(seconds  * 10.0), position.zw):
    gl_VertexID == 3 ? vec4(position.x * 0.2 - 0.1 , position.y * 0.2 - 0.5 + 0.05 * sin(seconds  * 10.0), position.zw):
    gl_VertexID == 4 ? vec4(position.x * 0.2 - 0.1 + 0.05 * -sin(seconds  * 10.0), position.y * 0.2 - 0.5 + 0.05 * cos(seconds  * 5.0), position.zw): 
    gl_VertexID == 5 ? vec4(position.x * 0.2 - 0.1 + 0.05 * sin(seconds  * 10.0), position.y * 0.2 - 0.5 + 0.05 * -cos(seconds  * 10.0), position.zw): 
    gl_VertexID == 6 ? vec4(position.x * 0.2 - 0.1 + 0.05 * -sin(seconds  * 10.0), position.y * 0.2 - 0.5 + 0.05 * cos(seconds  * 7.0), position.zw): 
    gl_VertexID == 7 ? vec4(position.x * 0.2 - 0.1 + 0.05 * cos(seconds  * 10.0), position.y * 0.2 - 0.5 + 0.05 * sin(seconds  * 5.0), position.zw): 
    gl_VertexID == 8 ? vec4(position.x * 0.2 - 0.1 + 0.05 * sin(seconds  * 10.0), position.y * 0.2 - 0.5 + 0.05 * -cos(seconds  * 10.0), position.zw): 
    gl_VertexID == 9 ? vec4(position.x * 0.2 - 0.1 + 0.05 * sin(seconds  * 5.0), position.y * 0.2 - 0.5, position.zw): 
    gl_VertexID == 10 ? vec4(position.x * 0.2 - 0.1 + 0.05 * sin(seconds  * 10.0), position.y * 0.2 - 0.5 + 0.05 * cos(seconds  * 10.0), position.zw): 
    gl_VertexID == 11 ? vec4(position.x * 0.2 - 0.1 + 0.05 * sin(seconds  * 10.0), position.y * 0.2 - 0.5 + 0.05 * cos(seconds  * 6.0), position.zw): 
    gl_VertexID == 12 ? vec4(position.x * 0.2 - 0.1, position.y * 0.2 - 0.5 + 0.05 * cos(seconds  * 10.0), position.zw): 
    gl_VertexID == 13 ? vec4(position.x * 0.2 - 0.1 + 0.05 * sin(seconds  * 7.0), position.y * 0.2 - 0.5 + 0.05 * cos(seconds  * 7.0), position.zw):
    gl_VertexID == 14 ? vec4(position.x * 0.2 - 0.1 + 0.05 * cos(seconds  * 8.0), position.y * 0.2 - 0.5 + 0.05 * cos(seconds  * 8.0), position.zw): 
    vec4(position.x * 0.2 - 0.1 + 0.05 * sin(seconds  * 5.0), position.y * 0.2 - 0.5 + 0.05 * cos(seconds  * 5.0), position.zw);
}