from vispy import app, gloo, visuals, scene
from vispy.geometry import create_cube
import numpy as np
import sys


vshader = '''
varying float line_pos;

void main(){
    vec4 doc_pos = $visual_to_doc(vec4($position, 0, 1));
    vec4 adjusted;
    if ($adjust_dir.x == 0.0){
        adjusted = doc_pos;
        line_pos = 1;
    }else{
        vec4 doc_xy = $visual_to_doc(vec4($adjust_dir.x, $adjust_dir.y, 0, 0));
        adjusted = doc_pos + $line_width * normalize(doc_xy);
        line_pos = 0;
    }
    gl_PointSize = 10.0;
    gl_Position = $doc_to_render(adjusted);
}
'''
fshader = '''
varying float line_pos;
void main(){
    vec4 pos = $fb_to_visual(gl_FragCoord);
    float alpha=0.5;
    if(line_pos*$doc_fb_scale > 0.5 && pos.x > 300){
        alpha = (1-line_pos)*2;
    }else{
        alpha = line_pos*2;
    }
    gl_FragColor = vec4($color.rgb, alpha);
}
'''

class MyRectVisual(visuals.Visual):
    def __init__(self, x,y,w,h, weight=50.0):
        super().__init__(vshader, fshader)
        
        self.weight = weight

        self.position = gloo.VertexBuffer(np.array([
            [x, y], [x, y],
            [x+w, y], [x+w, y],
            [x+w, y+h],[x+w, y+h],
            [x, y+h], [x, y+h],
            [x, y], [x, y],
        ], dtype=np.float32))
        self.shared_program.vert['position'] = self.position

        self.adjust_dir = gloo.VertexBuffer(np.array([
            [0, 0], [1, 1],
            [0, 0], [-1, 1],
            [0, 0], [-1, -1],
            [0, 0], [1, -1],
            [0, 0], [1, 1],
        ], dtype=np.float32))
        self.shared_program.vert['adjust_dir'] = self.adjust_dir
        self.shared_program.vert['line_width'] = self.weight
        self.shared_program.frag['color'] = (0,1,1, 1)
        self.shared_program.vert['line_width'] = 50.0
        
        self._draw_mode = 'triangle_strip'
        self.set_gl_state(cull_face=False)

        


    def _prepare_transforms(self, view):
        view.view_program.vert['visual_to_doc'] = view.transforms.get_transform('visual', 'document')
        view.view_program.vert['doc_to_render'] = view.transforms.get_transform('document', 'render')
        doc_to_fb = view.transforms.get_transform('document', 'framebuffer')
        fbs = np.linalg.norm(doc_to_fb.map([1,0])-doc_to_fb.map([0,0]))
        view.view_program.frag['doc_fb_scale'] = fbs
        view.view_program.frag['fb_to_visual'] = view.transforms.get_transform('framebuffer', 'visual')
        # view.view_program.frag['line_width'] = self.weight * fbs



MyRect = scene.visuals.create_visual_node(MyRectVisual)
canvas = scene.SceneCanvas(
    size=[1600,900],
    keys='interactive')



view = canvas.central_widget.add_view()
view.camera = 'panzoom'
view.camera.rect = (0,0,*canvas.size)
# @canvas.connect
# def on_resize(event):
#     view.camera.rect.size = canvas.size




rects = [
    MyRect(0,0,600,300, parent=view.scene),
    MyRect(0,0,600,300, parent=view.scene)
]

tr = visuals.transforms.MatrixTransform()
# tr.rotate(40, [0,0,1])
tr.translate([20,50,1])
rects[1].transform = tr

text = scene.visuals.Text("Hello world", 
    color='w',anchor_x='left', 
    parent=view, pos=(20, 30))

canvas.show()
if sys.flags.interactive != 1:
    app.run()