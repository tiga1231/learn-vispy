varying vec4 v_color;

uniform sampler2D texture;
varying vec2 v_texcoord;

void main(){
	gl_FragColor = v_color * texture2D( texture, v_texcoord+0.125/2.0);
}