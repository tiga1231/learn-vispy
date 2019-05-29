import numpy as np
from vispy import app
from vispy import gloo
from time import time




def rot(dim, i,j,angle):
	res = np.eye(dim)
	res[i,i] = np.cos(angle)
	res[j,i] = np.sin(angle)
	res[i,j] = -np.sin(angle)
	res[j,j] = np.cos(angle)
	return res


def project(data, t, thetas0=None, dim=4, stepsize=0.01):
	if thetas0 is None:
		thetas0 = thetas_global * stepsize * t
	rotation = np.eye(dim)

	for i in range(dim):
		for j in range(dim):
			rotation = rotation.dot(rot(dim, i,j,thetas0[i][j]))
	return data.dot(rotation[:,:3])




canvas = app.Canvas(keys='interactive')
t = time()

@canvas.connect
def on_resize(event):
	gloo.set_viewport(0,0,*event.size)

@canvas.connect
def on_draw(event):
	global t
	data = project(data0, t, dim=data0.shape[1], stepsize=0.1)
	program['a_position'] = data.astype(np.float32)

	gloo.clear([0.5,0.5,0.5,1])
	program.draw('points')
	canvas.update()
	t = time()




vertex = '''
attribute vec3 a_position;
attribute vec3 a_color;
varying vec3 v_color;

void main(void){
	gl_PointSize = (a_position[2]+1)*10;
	gl_PointSize = 6.0;

	gl_Position = vec4(a_position, 1.0);
	v_color = a_color;
}
'''

fragment = '''
varying vec3 v_color;
void main(){
	gl_FragColor = vec4(0.8,0.8,0.8, 1.0);
	gl_FragColor = vec4(v_color, 1.0);

	float dist = distance(vec2(0.5, 0.5), gl_PointCoord);
    if(dist > 0.5){
      discard;
    }

}
'''



data0 = np.random.random([1000,4])-0.5
colors = np.random.random([1000,3])
thetas_global = np.random.randn(4,4)

program = gloo.Program(vertex, fragment)
program['a_color'] = colors.astype(np.float32)

# timer = app.Timer('auto', on_draw)
# timer.start()

canvas.show()
app.run()