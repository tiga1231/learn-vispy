attribute vec3 position;

attribute vec4 color;
varying vec4 v_color;

uniform sampler2D texture;
attribute vec2 texcoord;
varying vec2 v_texcoord;

uniform vec4 u_color;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main(){
    v_color = u_color * color;
    gl_Position = projection*view*model*vec4(position, 1.0);
    v_texcoord = texcoord;
}