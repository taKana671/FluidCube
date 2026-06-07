import math
import random

import numpy as np
from panda3d.core import NodePath, PandaNode
from panda3d.core import BitMask32, Point3, Vec3, LColor

from shapes import RandomConvexPolyhedron, ShatteredSphere, Box
from utils import clock
from voronoi_generator.voronoi_3d.clip2cube import VoronoiClip2Cube
from voronoi_generator.voronoi_3d.clip2sphere import VoronoiClip2Sphere

# from cynoise import PerlinNoise
# from cynoise.simplex import SimplexNoise
# from noise import Fractal3D
from noise import PerlinCurlNoise3D, SimplexCurlNoise3D


class BoxPiece(NodePath):

    def __init__(self, serial, org_model, pos, color):
        super().__init__(PandaNode(f'box_piece_{serial}'))
        self.model = org_model.copy_to(self)
        # shape = BulletBoxShape(Vec3(0.1))
        # self.node().add_shape(shape)
        # self.node().set_mass(0)
        # self.set_collide_mask(BitMask32.bit(1))
        self.set_pos(pos)
        self.set_color(color)

        self.outof_range = False
        self.default_pos = pos
        self.disappeared = False



# simplex = SimplexNoise()
# perlin = PerlinNoise()
offset_1 = [0, 0, 300]
offset_2 = [0, 0, 600]
noise = PerlinCurlNoise3D(offset_1, offset_2)
# noise = SimplexCurlNoise3D(offset_1, offset_2)

# noise = Fractal3D(simplex.snoise3, octaves=2)
# noise = Fractal3D(perlin.pnoise3, octaves=2)


class Scene:

    def __init__(self):
        self.scene = NodePath('scene')
        self.scene.reparent_to(base.render)

        self.cells = NodePath('cells')
        self.cells.set_pos(Point3(0, 0, 0))
        self.cells.reparent_to(self.scene)
        self.total = 0
        self.pieces = []

    def move_pieces(self, dt, task_time):
        # simplex
        # flow_strength = 0.1
        # noise_scale = 1.05

        # perlin
        # flow_strength = 1.5
        flow_strength = 1.5  # 1.5
        noise_scale = 1

        speed = 0.5
        time_scale = 0.5
        current_time = task_time * time_scale

        scale_speed = 0.5
        angular_speed = [20, 40, 60, 80, 100]

        # import pdb; pdb.set_trace()
        for i, piece in enumerate(self.pieces):

            # pos = piece.default_pos + current_time
            # vec = curl_noise_3d(pos.x, pos.y, pos.z) * flow_strength
            pos = piece.get_pos() * noise_scale
            # vec = curl_noise_3d(pos.x, pos.y, pos.z) * flow_strength * dt
            vec = noise.curl_3d(pos.x, pos.y, pos.z) * flow_strength * dt

            # next_pos = piece.default_pos + Vec3(*vec)
            next_pos = pos + Vec3(*vec)
            piece.set_pos(next_pos)
            speed = random.choice(angular_speed)
            piece.model.set_hpr(piece.model.get_hpr() + Vec3(speed * dt))

            if piece.outof_range:
                if not piece.disappeared:
                    shrink = scale_speed * dt
                    if (scale := piece.get_scale() - shrink) > 0:
                        piece.set_scale(scale)
                    else:
                        # import pdb; pdb.set_trace()
                        piece.detach_node()
                        piece.disappeared = True
            else:
                if math.hypot(*next_pos) > 0.5:
                    piece.outof_range = True

    def create_cube(self):
        start = -0.575
        box_size = 0.05
        count = 15

        org_model = Box(0.05, 0.05, 0.05).create()
        color = LColor(1, 0, 0, 1)

        for i in range(count):
            z = i * box_size + start
            for j in range(count):
                y = j * box_size + start
                for k in range(count):
                    x = k * box_size + start
                    pos = Point3(x, y, z)

                    serial = f'{i}{j}{k}'
                    box = BoxPiece(serial, org_model, pos, color)
                    box.reparent_to(self.cells)
                    self.pieces.append(box)  