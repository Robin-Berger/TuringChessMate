from position import *
from evt_obj import EvtObj
import camera
import re
from colors import *
import time
import textures as tx
from fs_constants import *
import pygame as pg

# from move_functions import *

"""  Point, Face, Spacial Class @Robin Berger

    Objects are defined by points
    Faces are defined by points (clockwise to have the front towards you)
    
    Objects have a definition (points around 0,0,0 e reference frame of the object) and a position.
    This allows for 2 identical Eiffel Towers (definition) to be positioned at 2 positions
    The position spacial.pos can be modified during the game, allowing movement (Balloons, planes, birds, Sun)
        all points are then recalculated 

"""

class Pt(EvtObj):
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def coords(self):
        return self.x, self.y, self.z

    def coords_2D(self):
        return self.x, self.y

    def set_coords(self, coordinates):
        self.x, self.y, self.z = coordinates

    def tuplet(self):
        return (self.x, self.y)

CAM_POS_UNDEFINED = 0
CAM_POS_VISIBLE = 1
CAM_POS_FRONT_INVISIBLE = 2
CAM_POS_BACK = 3

class Point(EvtObj):
    def __init__(self, x, y, z, p_id=0, name="", x_factor=0, y_factor=0, z_factor=0):
        EvtObj.__init__(self)
        self.p_world = Pt(x, y, z)
        self.p_cam = Pt(0,0,0)   # np.array([0.0, 0.0, 0.0])
        self.p_prj = Pt(0,0,0)   # np.array([0.0, 0.0, 0])    # z is replaced by cam_pos = integer = 0,-1 or 1
        self.p_ref = Pt(0,0,0)  # will be of type Point
        self.x_factor, self.y_factor, self.z_factor = x_factor, y_factor, z_factor

        self.cam_pos = CAM_POS_UNDEFINED

        self.p_id = p_id
        self.name = name

    def set_ref_point(self, pt, x_factor, y_factor, z_factor):
        self.p_ref = pt
        self.x_factor, self.y_factor, self.z_factor = x_factor, y_factor, z_factor

    def set(self, x, y, z):
        # How it should be
        # self.p[0], self.p[1], self.p[2] = x, y, z
        self.x, self.y, self.z = x, y, z

    def recalculate(self, pos):
        self.p_world.x, self.p_world.y, self.p_world.z \
            = pos.world_coordinates(self.p_ref.x * self.x_factor,
                                    self.p_ref.y * self.y_factor,
                                    self.p_ref.z * self.z_factor)

    def precalc_for_cam(self, cam):
        self.p_cam.set_coords(cam.pos.local_coordinates(self.p_world.x, self.p_world.y, self.p_world.z))
        self.p_prj.set_coords(cam.perspective(self.p_cam.x, self.p_cam.y, self.p_cam.z))
        if self.p_cam.z < 0:
            self.cam_pos = CAM_POS_BACK
        elif (cam.display.x_min <= self.p_prj.x <= cam.display.x_max
              and cam.display.y_min <= self.p_prj.y <= cam.display.y_max):
            self.cam_pos = CAM_POS_VISIBLE
        else:
            self.cam_pos = CAM_POS_FRONT_INVISIBLE


EDGE_IN_FRONT = 0
EDGE_CROSSES = 1
EDGE_BEHIND = 2

class Edge(EvtObj):
    def __init__(self, p1, p2):
        EvtObj.__init__(self)
        self.p1, self.p2 = p1, p2
        self.q1, self.q2, self.q3 = None, None, None
        # Next properties give direction of crossing screen plane
        self.cross_type = 0
        self.kx, self.ky = 0, 0

class Face_Edge:
    def __init__(self, edge, orientation):
        self.edge = edge
        self.orientation = orientation
        self.prev_edge = None
        self.next_edge = None

    def P1(self):
        if self.orientation > 0:
            return self.edge.p1
        else:
            return self.edge.p2

    def P2(self):
        if self.orientation > 0:
            return self.edge.p2
        else:
            return self.edge.p1

    def Q1(self):
        if self.orientation > 0:
            return self.edge.q1
        else:
            if self.edge.q2 is None:
                return self.edge.q1
            else:
                return self.edge.q2

    def Q2(self):
        if self.orientation > 0:
            return self.edge.q2
        else:
            if self.edge.q2 is None:
                return None
            else:
                return self.edge.q1

class Face(EvtObj):
    def __init__(self, pt, fid=0, name=""):
        EvtObj.__init__(self)
        # All Points of the Face
        self.pt = pt    # array of points
        print("len in face",len(pt))
        # All Edges of the face
        self.face_edge = []
        # face id from upload file to make debugging files possible
        self.fid = fid
        # face name from upload file to allow clear popup info (e.g.: East Wall 70% damage)
        self.name = name
        # Placeholder for texture
        self.texture = None
        # default colors that will be overwritten

        self.c_fill = random_color(20, 120)
        self.c_back = BLUE
        self.c_line = RED
        # default front is visible = side where points go clockwise
        self.draw_front = True
        self.draw_back = False
        # Whenever the object is created or moved, the mid is recalculated
        self.mid = Point(0, 0, 0, 0, "mid")
        # For every camera draw cycle, cam_dist will be set to distance of self.mid from camera
        self.cam_dist = 0

    def add_edges(self, spacial):
        prev_p = self.pt[-1]
        for p in self.pt:
            print(p.p_world.coords())
            self.face_edge.append(spacial.get_face_edge(prev_p, p))
            prev_p = p
        prev_face_edge = self.face_edge[-1]
        for face_edge in self.face_edge:
            face_edge.prev_edge = prev_face_edge
            prev_face_edge.next_edge = face_edge
            prev_face_edge = face_edge

    def mid_coords(self):
        # Sometimes we need the x,y,z of mid like this
        return self.mid.x, self.mid.y, self.mid.z

    def recalculate(self):
        self.calc_mid()

    def calc_mid(self):
        x, y, z, n = 0, 0, 0, 0
        for pt in self.pt:
            n += 1
            x, y, z = x + pt.p_world.x, y + pt.p_world.y, z + pt.p_world.z
        self.mid.set(x / n, y / n, z / n)

    def calc_cam_dist(self, cam):
        x, y, z = self.mid_coords()
        self.cam_dist = cam.cam_dist(x, y, z)

    def cam_side(self, cam):
        p1, p2 = self.pt[0],self.pt[1]
        x, y, z = self.mid_coords()
        x, y, z = cam.pos.local_coordinates(x, y, z)
        x1, y1, z1 = cam.pos.local_coordinates(p1.p_world.x, p1.p_world.y, p1.p_world.z)
        x2, y2, z2 = cam.pos.local_coordinates(p2.p_world.x, p2.p_world.y, p2.p_world.z)
        # bereken 2 vectoren hoek-centrum (werkt enkel voor convexe figuren)
        _x1, _y1, _z1 = x1-x, y1-y, z1-z
        _x2, _y2, _z2 = x2-x, y2-y, z2-z
        # bereken de normaal n
        nx, ny, nz = _y1 * _z2 - _z1 * _y2, _z1 * _x2 - _x1 * _z2, _x1 * _y2 - _y1 * _x2
        # return scalair product met midvector van de figuur (=positie t.o.v. camera)
        return nx * x + ny * y + nz * z

    def draw(self, cam, c, face, filled):
        if face.texture and OBJECT_TEXTURES:
            cam.draw_polygon_texture(face.pt, tx.txtures[face.texture])
        else:
            new_pt = cam.get_display_intersect_polygon(face)
            if new_pt is not None:
                if len(new_pt) > 2:
                    pg.draw.polygon(cam.display.window,face.c_fill, new_pt, 0)
                    #for pt in new_pt:
                    #    pg.draw.circle(cam.display.window,RED,(pt[0],pt[1]),12,8)
            #cam.draw_polygon(RED, face.pt, False)


class Spacial(EvtObj):
    def __init__(self, x, y, z, alpha, beta, gamma, name="", move_code=""):
        EvtObj.__init__(self)
        # geeft positie en draaiing van het object
        # bij wijziging van positie worden alle punten van het object herrekend
        self.pos = Position(x, y, z, alpha, beta, gamma)
        # All Points of the Spacial
        self.pt = []
        # All Edges of the Spacial
        self.edge = []
        # All Faces of the Spacial
        self.face = []
        # Whenever the object is created or moved, the mid is recalculated
        self.mid = Point(0, 0, 0, 0, "mid")
        # Extra code that can be executed each cycle
        self.move_code = move_code
        # Allow for a script to be executed at move
        self.script_code = []
        # For every camera draw cycle, cam_dist will be set to distance of self.mid from camera
        self.cam_dist = 0
        # face name from upload file to allow clear popup info (e.g.: Zeppelin is about to explode)
        self.name = name

    def get_face_edge(self, p1, p2):
       # This routine will find the edge corresponding to p1,p2
        for edge in self.edge:
            #print(p1.p_cam.coords(), edge.p1.p_cam.coords())
            if p1 is edge.p1 and p2 is edge.p2:
                #print("a")
                return Face_Edge(edge, 1)
            elif p1 is edge.p2 and p2 is edge.p1:
                #print("b")
                return Face_Edge(edge, -1)
        # If Edge does not exist it will be created
        edge = Edge(p1, p2)
        self.edge.append(edge)
        #print("c")
        return Face_Edge(edge, 1)

    def add_edges(self):
        for face in self.face:
            face.add_edges(self)

    def rp(self, p_id):
        for f in self.face:
            for p in f.pt:
                if p.p_id == p_id:
                    return p.p_ref

    def pid(self, p_id):
        for f in self.face:
            for p in f.pt:
                return p

    def recalculate(self):
        # When we recalculate an object, we have to recalculate all sub-objects
        # Points first, because Faces are based on points
        for point in self.pt:
            point.recalculate(self.pos)
        for face in self.face:
            face.recalculate()
        self.calc_mid()

    def move(self):
        if self.move_code != "" or len(self.script_code) > 0:
            t = time.time()
            ts = int((t / 1000 - int(t / 1000)) * 100000)  # 0-100000
            tt = int((t / 10 - int(t / 10)) * 1000)  # 0-1000
            if tt > 500:
                tt = 1000 - tt

            wt = m.pi * ts / 500
            wt2 = m.pi * tt / 500

            if self.move_code != "":
                # For now we assume that move_code only affects position data
                exec(self.move_code)
                # Because angles may change, we need to recalculate R
                self.pos.calc_R()
                # Because mid and cam_dist may have changed, we do a full recalculate
                self.recalculate()

            if len(self.script_code) > 0:
                # For now we assume that move_code only affects position data
                exec(self.script_code[0])
                # Because angles may change, we need to recalculate R
                self.pos.calc_R()
                # Because mid and cam_dist may have changed, we do a full recalculate
                self.recalculate()

    def mid_coords(self):
        return self.mid.x, self.mid.y, self.mid.z

    def calc_mid(self):
        x, y, z, n = 0, 0, 0, 0
        for face in self.face:
            n += 1
            fmid = face.mid
            x, y, z = x + fmid.x, y + fmid.y, z + fmid.z
        if n:
            self.mid.set(x / n, y / n, z / n)
        else:
            self.mid.set(0, 0, 0)

    def calc_cam_dist(self, cam):
        for face in self.face:
            face.calc_cam_dist(cam)
        self.cam_dist = cam.cam_dist(self.mid.x, self.mid.y, self.mid.z)

    def draw_point(self, cam, c, p):
        cam.draw_line(c, p[0], p[1], p[2], p[0], p[1], p[2])

    def draw(self, cam, filled):
        sorted_faces = sorted(self.face, key=lambda f: f.cam_dist, reverse=True)
        for face in sorted_faces:
            if face.cam_side(cam) < 0:
                if filled:
                    face.draw(cam, face.c_fill, face, True)
                face.draw(cam, face.c_line, face, False)

    def get_points_by_id(self, point_ids):
        return [self.get_point_by_id(point_id) for point_id in point_ids]

    def get_point_by_id(self, p_id):
        for point in self.pt:
            if point.p_id == p_id:
                return point


class CustomShape(Spacial):
    def __init__(self, construction_id, x, y, z, alpha, beta, gamma, name="", move_code=""):
        Spacial.__init__(self, x, y, z, alpha, beta, gamma, name, move_code)
        self.spacial_id = construction_id

    def read_from_file(self, calc_points, file_name, x_factor, y_factor, z_factor):
        with open(file_name, 'r') as city_file:
            building_data = city_file.read()

        construction_pattern = (r'<CONSTRUCTION'
                                r' name="([^"]+)"'  # name="([^"]+)  mandatory field name=abc
                                r'>'
                                r'(.*?)'             # (.*?)  free text
                                r'</CONSTRUCTION>')
        construction_matches = re.findall(construction_pattern, building_data, re.DOTALL)  # re.DOTALL allows returns
        for construction in construction_matches:

            construction_name, construction_text = construction
            script_pattern = r'<SCRIPT id=(\d+)>(.*?)</SCRIPT>'
            script_matches = re.findall(script_pattern, construction_text, re.DOTALL)  # re.DOTALL allows returns
            for script in script_matches:
                #   print(script[1])
                self.script_code.append(script[1])

            point_pattern = (r'<POINT'
                             r' id=(\d+)'           # <POINT id=(\d+)"  mandatory field id=123
                             r'>'
                             r'((?:-?\d+,)+-?\d+)'  # array of numbers (can be negative: -sign ?:- decimal ?\d+)
                             r'</POINT>')
            point_matches = re.findall(point_pattern, construction[1])

            for match in point_matches:
                # TODO: Texture data

                point_id, pt_array = match
                point_id = int(match[0])
                pt = [int(coord) for coord in pt_array.split(',')]
                ref_point = Pt(pt[0], pt[1], pt[2])
                print("refpoint",pt[0], pt[1], pt[2])
                # print(f"Point ID: {point_id}, Coördinaten: {pt}")
                world_point = Point(1, 2, 3, point_id, "")
                world_point.set_ref_point(ref_point, x_factor, y_factor, z_factor)
                #   ALL POINTS MUST BE IN THE RECALC LIST
                calc_points.append(world_point)     # for fast unique recalculation
                self.pt.append(world_point)

            # TODO: Texture data
            # <FACE id=(\d+) name="([^"]+)"     # Mandatory fields <FACE ID="text" name="text"
            # (?: texture="(.*?)")?             # Optional field move between (?: and )?
            # ([\d,]+)                          # array of numbers (MUST be positive decimals ?\d+)
            face_pattern = (r'<FACE id=(\d+)'           # mandatory field id=(\d+)  id=123
                            r' name="([^"]+)"'          # mandatory name="([^"]+)"  name="abc"
                            r'(?: texture="(.*?)")?'    # optional texture="(.*?)")? texture="abc"
                            r'>'
                            r'([\d,]+)'
                            r'</FACE>')
            face_matches = re.findall(face_pattern, construction[1])
            for match in face_matches:
                face_id, face_name, face_texture, point_id_array = match
                point_ids = [int(pid) for pid in point_id_array.split(',')]
                print(f"Face ID: {face_id} Name: {face_name} ,Points: {point_ids}",self.get_points_by_id(point_ids))
                new_face = Face(self.get_points_by_id(point_ids), face_id, face_name)
                self.face.append(new_face)

                # TODO: FILL IN TEXTURE CODE
                if face_texture:
                    new_face.texture = int (face_texture)


                #   ALL POINTS MUST BE IN THE RECALC LIST
                calc_points.append(new_face.mid)  # for fast unique recalculation
            self.add_edges()
