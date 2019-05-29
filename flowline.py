from vispy import app, scene, visuals, gloo
from vispy.util import ptime

import numpy as np

class VectorFieldVisual(visuals.Visual):
    vshader = '''
    uniform sampler2D field;
    uniform sampler2D offset;
    attribute vec3 index;
    uniform vec2 field_shape;
    uniform float n_step;
    uniform float spacing;
    varying float step;
    varying float time_offset;
    varying vec4 color;
    vec3 hsv2rgb(vec3 c) {
        vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
        vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
        return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
    }

    void main(){
        gl_PointSize = 2.0;
        vec3 random = texture2D(offset, index.xy*spacing/field_shape.xy).rgb;
        vec2 loc = (index.xy+random.xy) * spacing;
        step = index.z;
        
        time_offset = random.b;

        vec2 uv;
        for(int i=0; i<step; i++){
            for(int j=0; j<n_step; j++){
                uv = texture2D(field, loc/field_shape.xy).rg;
                loc += 0.001 * uv;
            }
        }
        vec3 hsv = vec3(atan(uv.y, uv.x)/6.28+0.5, 0.5, 0.8);
        color = vec4(hsv2rgb(hsv), sqrt(length(uv)/200));
        gl_Position = $transform(vec4(loc, 0, 1));
    }
    '''

    fshader = '''
    varying float step;
    uniform float time;
    uniform float n_step;
    varying float time_offset;
    varying vec4 color;

    void main(){
        float loc = step / n_step;
        float t = 0.3*time + time_offset;
        float x = (-t + loc);
        float alpha = mod(x, 1);
        alpha *= (1+cos(3.14 * (loc-0.1))) * 0.5;
        //alpha *= (1+cos(3.14 * 10* loc)) * 0.9;
        vec3 final_color = mix(color.rgb, vec3(1,1,1), 0.0);
        gl_FragColor = vec4(final_color.rgb, color.a * alpha);
    }
    '''

    def __init__(self, field, nstep=30, spacing = 0.5):
        

        self.field = field
        self.field = gloo.Texture2D(self.field, 
            format='rg', internalformat='rg32f', interpolation='linear')

        self.offset = np.random.random(
            ( int(field.shape[0]/spacing), int(field.shape[1]/spacing), 3,)).astype(np.float32)
        self.offset[:,:,:2] -= 0.5
        self.offset = gloo.Texture2D(self.offset, 
            format='rgb', internalformat='rgb32f')

        i = np.arange(field.shape[0] / spacing)
        j = np.arange(field.shape[1] / spacing)
        k = np.arange(nstep*2)
        k[::2] = k[::2]/2.0
        k[1::2] = k[::2]+1
        i,j,k = np.meshgrid(i, j, k)
        ij = np.c_[np.ravel(i), np.ravel(j), np.ravel(k)].astype(np.float32)
        self.time = 0

        

        super().__init__(vcode=self.vshader, fcode=self.fshader)
        self.timer = app.Timer(interval='auto', connect=self.update_time)
        self.freeze()

        self.shared_program['field_shape'] = field.shape[:2]
        self.shared_program['n_step'] = nstep

        
        self.shared_program['offset'] = self.offset
        self.shared_program['field'] = self.field

        self.shared_program['time'] = self.time
        
        self.shared_program['index'] = ij
        self.shared_program['spacing'] = spacing
        self._draw_mode = 'lines'

        self.set_gl_state('translucent', depth_test=False)
        
        self.timer.start()
    def _prepare_transforms(self, view):
        view.view_program.vert['transform'] = view.get_transform()
 
    # def _prepare_draw(self, view):
    #     pass

    # def _compute_bounds(self, axis, view):
    #     if axis > 1:
    #         return (0, 0)
        # return (0, self._field_shape[axis])
    def setField(self, field):
        self.field = field
        self.field = gloo.Texture2D(self.field, 
            format='rg', internalformat='rg32f', interpolation='linear')
        self.shared_program['field'] = self.field

    def update_time(self, event):
        self.time += event.dt
        self.shared_program['time'] = self.time
        self.update()

# def fn(y, x):
#     dx = x-50
#     dy = y-20
#     hyp = (dx**2 + dy**2)**0.5 + 0.01
#     return np.array([100 * dy / hyp**1.7, -100 * dx / hyp**1.8])

def fn(x,y,t=0):
    dx = x-50
    dy = y-50
    # vx = -dy
    # vy = dx
    vx = np.cos(t) * dx + np.sin(t) * dy
    vy = -np.sin(t) * dx + np.cos(t) * dy
    return np.array([vx, vy]) #=[vy,vx]

VectorField = scene.visuals.create_visual_node(VectorFieldVisual)
canvas = scene.SceneCanvas(size=[1600,1600],
    keys='interactive', show=True)
gloo.set_state(
#     # clear_color=(0.30, 0.30, 0.35, 1.00), 
#  #    polygon_offset=(1, 1), 
#  #    blend_func=('src_alpha', 'one_minus_src_alpha'),
    line_width=2,
)
view = canvas.central_widget.add_view(camera='panzoom')
view.camera.set_range()

view.camera.rect = (0,0,100,100)

# text = scene.visuals.Text("Hello world", 
#     color='w',anchor_x='left', 
#     parent=view, pos=(20, 30))

field = np.fromfunction(fn, (100, 100)).transpose(2,1,0).astype('float32')
# field[..., 0] += 10 * np.cos(np.linspace(0, 2 * 3.1415, 100))
vfield = VectorField(field, parent=view.scene)

t = 0
@canvas.connect
def on_key_press(event):
    global t
    t += 0.1
    field = np.fromfunction(fn, (100, 100), t=t).transpose(2,1,0).astype('float32')
    vfield.setField(field)
    print(repr(event))
    print(event.modifiers, event.key)
app.run()