from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import Material, AmbientLight, Spotlight, PerspectiveLens, NodePath, PandaNode, LightRampAttrib, AntialiasAttrib
from direct.filter.CommonFilters import CommonFilters

from math import pi, sin, cos
from pyvista import read
from os import path

class MyApp(ShowBase):
    def __init__(self) -> None:
        ShowBase.__init__(self)
        self.disable_mouse()
        self.render.set_shader_auto()
        self.set_frame_rate_meter(True)

        self.create_scene()
        self.create_model()
        self.add_lights()
        self.cartoon_shading()

        self.camera.set_pos(0, 400, 100)
        self.camera.look_at(self.model)

        self.render.setAntialias(AntialiasAttrib.MMultisample)

        # self.task_mgr.add(self.rotate_camera, 'RotateCamera')
        self.task_mgr.add(self.rotate_model, 'RotateModel')


    def create_scene(self) -> None:
        """Create scene"""
        scale = 1000
        material = Material()
        material.set_ambient(self.to_rgba(125, 125, 125))
        material.set_diffuse(self.to_rgba(125, 125, 125))
        material.set_specular(self.to_rgba(125, 125, 125))

        self.scene = self.loader.load_model('models/box')
        self.scene.set_texture_off(1)
        self.scene.set_scale(scale, scale, 1)
        self.scene.set_pos(-0.5 * scale, -0.5 * scale, -100)
        self.scene.reparent_to(self.render)
        self.scene.set_material(material, 1)

    def create_model(self) -> None:
        """Add model to scene"""
        material = Material()
        material.set_ambient(self.to_rgba(0, 46, 117))
        material.set_diffuse(self.to_rgba(119, 151, 201))
        material.set_specular(self.to_rgba(125, 125, 125))

        filepath = 'zortrax_voronoi_sphere.stl'
        filepath = self.subsurface_division(0, filepath)
        self.model = self.loader.load_model(filepath)
        self.model.reparent_to(self.render)
        self.model.set_pos(0, 0, 0)
        self.model.set_material(material, 1)
  
    def add_lights(self) -> None:
        """Add lights to model"""
        self.ambient_light = AmbientLight('AmbientLight')
        self.ambient_light.set_color((0.5, 0.5, 0.5, 1))
        self.ambient_light_np = self.render.attach_new_node(self.ambient_light)
        self.render.set_light(self.ambient_light_np)

        self.spotlight = Spotlight('Spotlight')
        self.spotlight.set_shadow_caster(True, 4096, 4096)
        self.spotlight.set_color((1, 1, 1, 1))
        self.spotlight.set_lens(PerspectiveLens())
        self.spotlight_np = self.render.attach_new_node(self.spotlight)
        self.spotlight_np.set_pos(500, 500, 250)
        self.spotlight_np.look_at(self.model)
        self.render.set_light(self.spotlight_np)

    def cartoon_shading(self) -> None:
        """Adds cartoon shading to the scene"""

        # Enable a 'light ramp' - this discretizes the lighting,
        # which is half of what makes a model look like a cartoon.
        # Light ramps only work if shader generation is enabled,
        # so we call 'setShaderAuto'.
        tempnode = NodePath(PandaNode("temp node"))
        tempnode.setAttrib(LightRampAttrib.makeSingleThreshold(0.5, 0.4))
        tempnode.setShaderAuto()
        self.cam.node().setInitialState(tempnode.getState())

        # Use class 'CommonFilters' to enable a cartoon inking filter.
        # This can fail if the video card is not powerful enough, if so,
        # display an error and exit.
        self.separation = 2.5  # Pixels
        self.filters = CommonFilters(self.win, self.cam)
        filterok = self.filters.setCartoonInk(separation=self.separation)
        if (filterok == False):
            print('L Graphics Card')
            return

    def rotate_camera(self, task: Task.Task) -> int:
        """Rotates camera each frame"""
        rotation_deg = 20 * task.time
        rotation_rad = rotation_deg * (pi / 180)
        self.camera.set_pos(400 * sin(rotation_rad), 400 * cos(rotation_rad), 100)
        self.camera.look_at(self.model)
        return Task.cont
    
    def rotate_model(self, task: Task.Task) -> int:
        """Rotates object every frame"""
        rotation_deg = 20 * task.time
        self.model.set_hpr(rotation_deg, 0, 0)
        return Task.cont
    
    def to_rgba(self, r: int, g: int, b: int) -> tuple[float, float, float, float]:
        """Converts RGB to normalized RGBA"""
        return (r / 255, g / 255, b / 255, 1)
    
    def subsurface_division(self, nsub: int, filepath: str) -> str:
        """Subdivide stl model surface"""
        if nsub == 0:
            return filepath
        new_filepath = f'{filepath.split(".")[0]}_subdivision_{nsub}.stl'
        if not path.isfile(f'C:/DOCUMENTS/DEVELOPMENT/LegoBuilder/{new_filepath}'):
            mesh = read(filepath)
            mesh = mesh.subdivide(nsub, 'loop')
            mesh.save(new_filepath)
        return new_filepath

app = MyApp()
app.run()
