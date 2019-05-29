from vispy import app, gloo
from vispy.color import Color
from vispy.geometry import create_cube
from vispy.gloo import Program, VertexBuffer, IndexBuffer

from vispy.util.transforms import perspective, translate, rotate

import numpy as np
import math
from random import random
import sys

def checkerboard(grid_num=8, grid_size=32):
    row_even = grid_num // 2 * [0, 1]
    row_odd = grid_num // 2 * [1, 0]
    Z = np.row_stack(grid_num // 2 * (row_even, row_odd)).astype(np.uint8)
    return 255 * Z.repeat(grid_size, axis=0).repeat(grid_size, axis=1)


class MyCanvas(app.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timer = app.Timer('auto', connect=self.on_timer, start=True)
        
        with open('vertex.glsl') as f:
            self.vshader = f.read()
        with open('fragment.glsl') as f:
            self.fshader = f.read()
        self.program = Program(self.vshader, self.fshader)

        v, i, iOutline = create_cube()
        self.vertices = VertexBuffer(v)
        self.indices = IndexBuffer(i)
        self.outlineIndices = IndexBuffer(iOutline)
        self.program.bind(self.vertices)

        self.theta, self.phi = 0,0
        self.program['model'] = np.eye(4)
        self.program['view'] = translate([0,0,-5])

        self.program['texture'] = checkerboard()
        gloo.set_state(clear_color=(0.30, 0.30, 0.35, 1.00), 
            polygon_offset=(1, 1), 
            blend_func=('src_alpha', 'one_minus_src_alpha'),
            line_width=5,
            depth_test=True)

    def on_resize(self, event):
        gloo.set_viewport(0,0, *self.physical_size)
        proj = perspective(45.0, self.size[0]/self.size[1], 0.01, 1000)
        self.program['projection'] = proj

    def on_draw(self, event):
        gloo.clear(color=True, depth=True)

        gloo.set_state(blend=False, depth_test=True, polygon_offset_fill=True)
        self.program['u_color'] = [1,1,1,1]
        self.program.draw('triangles', self.indices)

        gloo.set_state(blend=True, depth_mask=False, polygon_offset_fill=False)
        self.program['u_color'] = [0,0,0,1]
        self.program.draw('lines', self.outlineIndices)
        gloo.set_state(depth_mask=True)

    def on_timer(self, event):
        self.theta = event.elapsed * 30
        self.phi = 0
        self.program['model'] = np.dot(
            rotate(self.phi, [1,0,0]), 
            rotate(self.theta, [0,1,0]),)
        self.update()

    # def on_key_press(self, event):
    #     print(repr(event))
    #     print(event.modifiers, event.key)

    # def on_mouse_move(self, event):
    #     print(repr(event))



#==============================
# app.use_app('glfw')
canvas = MyCanvas(title='colored cube',
    size=[1200,900],
    keys='interactive', 
    always_on_top=True
)
# canvas.measure_fps()
canvas.show()
if not sys.flags.interactive:
    app.run()