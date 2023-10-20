#version 300 es
uniform float seconds;
out vec4 pos;
void main() {

    gl_Position = gl_VertexID == 0 ? vec4(-1, -1, 0, 1) : 
    gl_VertexID == 1 ? vec4(-1, 1, 0, 1) : 
    gl_VertexID == 2 ? vec4(1, 1, 0, 1) :
    gl_VertexID == 3 ? vec4(-1, -1, 0, 1) :
    gl_VertexID == 4 ? vec4(1, -1, 0, 1) : vec4(1, 1, 0, 1);

    pos = gl_Position * vec4(sin(seconds), cos(seconds), 0, 1);

}