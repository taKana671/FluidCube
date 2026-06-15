import sys

from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import AmbientLight, DirectionalLight
from panda3d.core import Point3, Vec3, Vec2, LColor
from panda3d.core import NodePath
from panda3d.core import AntialiasAttrib
from panda3d.core import load_prc_file_data

from box_collection import BoxCollection


load_prc_file_data("", """
    textures-power-2 none
    gl-coordinate-system default
    window-title FluidCube
    filled-wireframe-apply-shader true
    stm-max-views 8
    stm-max-chunk-count 2048
    framebuffer-multisample 1
    multisamples 2""")


class FluidCube(ShowBase):

    def __init__(self):
        super().__init__()
        self.disable_mouse()
        self.render.set_antialias(AntialiasAttrib.MAuto)

        self.camera_root = NodePath('camera_root')
        self.camera_root.reparent_to(self.render)
        self.camera.reparent_to(self.camera_root)
        self.camera.set_pos(Point3(0, -10, 5))
        self.camera.look_at(Point3(0, 0, 0))

        self.particles = BoxCollection()
        self.particles.create()
        self.setup_light()

        self.clicked = False
        self.dragging = False
        self.before_mouse_pos = None
        self.do_move = False

        self.accept('escape', sys.exit)
        self.accept('mouse1', self.mouse_click)
        self.accept('mouse1-up', self.mouse_release)
        self.accept('m', self.start_move_particles)

        self.taskMgr.add(self.update, 'update')

    def setup_light(self):
        ambient_light = NodePath(AmbientLight('ambient_light'))
        ambient_light.reparent_to(self.render)
        ambient_light.node().set_color(LColor(0.6, 0.6, 0.6, 1.0))
        self.render.set_light(ambient_light)

        directional_light = NodePath(DirectionalLight('directional_light'))
        directional_light.node().get_lens().set_film_size(200, 200)
        directional_light.node().get_lens().set_near_far(1, 100)
        directional_light.node().set_color(LColor(1, 1, 1, 1))
        directional_light.set_pos_hpr(Point3(0, 0, 50), Vec3(-30, -45, 0))
        # directional_light.node().show_frustom()
        self.render.set_light(directional_light)
        directional_light.node().set_shadow_caster(True)
        self.render.set_shader_auto()

    def start_move_particles(self):
        delay_time = 0

        if self.particles.all_detached:
            self.particles.reset()
            delay_time = 0.5

        def callback(task):
            self.do_move = True
            return task.done

        base.task_mgr.do_method_later(delay_time, callback, 'start_move')

    def mouse_click(self):
        self.dragging = True
        self.dragging_start_time = globalClock.get_frame_time()

    def mouse_release(self):
        if globalClock.get_frame_time() - self.dragging_start_time < 0.2:
            self.clicked = True

        self.dragging = False
        self.before_mouse_pos = None

    def rotate_camera(self, mouse_pos, dt):
        if self.before_mouse_pos:
            angle = Vec3()

            if (delta := mouse_pos.x - self.before_mouse_pos.x) < 0:
                angle.x += 180
            elif delta > 0:
                angle.x -= 180

            if (delta := mouse_pos.y - self.before_mouse_pos.y) < 0:
                angle.z -= 180
            elif delta > 0:
                angle.z += 180

            angle *= dt
            self.camera_root.set_hpr(self.camera_root.get_hpr() + angle)

        self.before_mouse_pos = Vec2(mouse_pos.xy)

    def update(self, task):
        dt = globalClock.get_dt()

        if self.mouseWatcherNode.has_mouse():
            mouse_pos = self.mouseWatcherNode.get_mouse()

            if self.dragging:
                if globalClock.get_frame_time() - self.dragging_start_time >= 0.2:
                    self.rotate_camera(mouse_pos, dt)

        if self.do_move:
            if self.particles.move(dt):
                self.do_move = False

        return task.cont


if __name__ == '__main__':
    app = FluidCube()
    app.run()