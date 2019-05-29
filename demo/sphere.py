import sys

import vispy
from vispy import scene, app
from vispy.visuals.transforms import STTransform

import numpy as np




canvas = scene.SceneCanvas(
	keys='interactive', 
	bgcolor='#333333', 
	size=[1600,1600],
	show=True
)

view = canvas.central_widget.add_view()
view.camera = scene.TurntableCamera()
view.camera.set_range((-10, 10), (-10, 10), (-10, 10))

for i in range(10):
	s = scene.visuals.Sphere(
		method='ico', subdivisions=1,
		parent=view.scene,
		shading='smooth',
		radius=1, 
		# edge_color='black',
	)
	s.mesh.light_dir = [1,2,300]

	x,y,z = (np.random.random(3)-0.5) * 10
	s.transform = STTransform(translate=[x,y,z])


canvas.app.run()

