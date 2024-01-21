import math
import random
import spacials
from colors import *
import image_3D
import pygame as pg
import math as m
import polygon
from position import Position

""" Camera Class

    Camera comes with a separate class Display.
    This will ensure that in multi_user games, camera's can switch displays for side by side or full view
    
    Camera will project a 3D world on a 2D screen.
    For now only perspectiveFlat is acceptable
    
    Position object defines position AND orientation for any object in space
    Position provides coordinate transformation between world and object
    Position object can be shared between multiple objects (e.g. airplane,front_cam,back_cam)
    
@Robin Berger
"""


class Display:
    def __init__(self, win, r, x0, y0, z0, zoom_factor):
        self.r = r
        self.zoom_factor = zoom_factor
        self.x0, self.y0, self. z0 = x0, y0, z0
        self.x_min = self.left()
        self.x_max = self.right()
        self.y_min = self.top()
        self.y_max = self.bottom()
        self.window = win

        #self.pos_TL = Position(0, 0, 0, m.atan2((self.y0 - self.y_min) / self.zoom_factor, self.z0),
        #                       -m.atan2((self.x_min - self.x0) / self.zoom_factor, self.z0), 0)
        #self.pos_TR = Position(0, 0, 0, m.atan2((self.y0 - self.y_min) / self.zoom_factor, self.z0),
        #                       -m.atan2((self.x_max - self.x0) / self.zoom_factor, self.z0), 0)
        #self.pos_BR = Position(0, 0, 0, m.atan2((self.y0 - self.y_max) / self.zoom_factor, self.z0),
        #                       -m.atan2((self.x_max - self.x0) / self.zoom_factor, self.z0), 0)
        #self.pos_BL = Position(0, 0, 0, m.atan2((self.y0 - self.y_max) / self.zoom_factor, self.z0),
        #                       -m.atan2((self.x_min - self.x0) / self.zoom_factor, self.z0), 0)

        # Next routines: thanks to Simon Vanspeybroeck
        self.pos_TL = Position(0, 0, 0, self.x_angle(self.x_min,self.y_min), self.y_angle(self.x_min), 0)
        self.pos_TR = Position(0, 0, 0, self.x_angle(self.x_max,self.y_min), self.y_angle(self.x_max), 0)
        self.pos_BR = Position(0, 0, 0, self.x_angle(self.x_max,self.y_max), self.y_angle(self.x_max), 0)
        self.pos_BL = Position(0, 0, 0, self.x_angle(self.x_min,self.y_max), self.y_angle(self.x_min), 0)
    def y_angle(self, x):
        dx = (x - self.x0) / self.zoom_factor
        dz = self.z0
        return -m.atan2(dx, dz)

    def x_angle(self, x, y):
        dx = (x - self.x0) / self.zoom_factor
        dy = (y - self.y0) / self.zoom_factor
        dz = self.z0
        r = m.sqrt(dx*dx + dy*dy + dz*dz)
        return -m.asin(dy/r)

    def left(self):
        return self.r[0]

    def top(self):
        return self.r[1]

    def right(self):
        return self.r[0] + self.r[2]

    def bottom(self):
        return self.r[1] + self.r[3]

    def width(self):
        return self.r[2]

    def height(self):
        return self.r[3]

    def small_r(self, margin):
        return self.r[0] + margin, self.r[1] + margin, self.r[2] - 2 * margin, self.r[3] - 2 * margin

    def draw(self):
        # Before drawing the content of a display, we first draw the display
        # We set a clip_rect so that we cannot draw outside the display
        self.window.set_clip(self.r)

        # We clear the display area
        pg.draw.rect(self.window, (135, 206, 235), self.r, 0)

        # We draw the outer rectangle (for now, until we have decided on the global graphics)
        pg.draw.rect(self.window, DKGREY, self.r, 4)

        # We set a clip_rect 1 pixel smaller, so that we cannot draw over the border rectangle
        self.window.set_clip(self.small_r(3))


class Camera:
    def __init__(self, pos, display, cam_pos, cam_offset):
        # position of the camera in space (normally shared with a player object or NPC object(like drone cam))
        self.pos = pos
        # for now 1 fixed display per camera
        self.display = display
        # distance between camera and imaginary projection screen
        # self.depth = depth

        # Zoom after projection
        self.zoom = 1.0
        # By using an integer zoom nr that increases or decreases, we avoid rounding effects
        self.zoom_nr = 0

        # cam_pos == 1 means forward view; cam_pos == -1 means rearview
        self.cam_pos = cam_pos
        # moves the camera in the z direction. Example of use:
        #      To see the airplane: cam_offset = -200
        #      To see cockpit: cam_offset = -50
        #      no cockpit cam_offset = 0
        self.cam_offset = cam_offset

    def cam_dist(self, x, y, z):
        # Calculates how far a point is away from camera (to be able to draw furthest points first)
        x, y, z = self.pos.local_coordinates(x, y, z)
        # If point is behind camera, then distance is negative (switch sign for backward camera)
        if z > 0:
            return self.cam_pos * m.sqrt(x**2 + y**2 + z**2)
        else:
            return -self.cam_pos * m.sqrt(x**2 + y**2 + z**2)

    def perspective(self, x, y, z):
        z += self.cam_offset
        z *= self.cam_pos
        if z == 0:
            cam_pos, xp, yp = 0, 0, 0
        else:
            if z > 0:
                cam_pos = 1
                xp = self.display.zoom_factor * x * (self.display.z0 / z)
                yp = -self.display.zoom_factor * y * (self.display.z0 / z)

            else:   # Needed later on for drawing lines near z=0
                cam_pos = -1
                xp = self.display.zoom_factor * x * (self.display.z0 / - z)
                yp = -self.display.zoom_factor * y * (self.display.z0 / - z)

            # Define 0,0 usually a bit below center of screen (sky is more interesting than ground)
            xp += self.display.x0
            yp += self.display.y0

        return xp, yp, cam_pos

    def local_perspective(self, x1, y1, z1):
        # Always convert to camera coordinates first
        x1, y1, z1 = self.pos.local_coordinates(x1, y1, z1)
        # Calculate perspective
        _x1, _y1, cam_pos = self.perspective(x1, y1, z1)
        return _x1, _y1, cam_pos

    def zoom_cam(self, zoom_step):
        # zoom can step up or down
        self.zoom_nr += zoom_step
        # effective zoom is exponential: every step is 10% (1,1)
        self.zoom = m.pow(1.1, self.zoom_nr)

    def draw_circle(self, c, x1, y1, z1, r):
        # ONLY WORKS CORRECTLY for circles that are not rotated around x or y
        _x1, _y1, cam_pos = self.local_perspective(x1, y1, z1)
        if cam_pos > 0:
            pg.draw.circle(self.display.window, c, (_x1, _y1), r, 1)

    def point_line_sign(self, x, y, p1, p2):
        # compares at what side of the line (p1,p2) a point (x,y) is
        _x1, _y1, cam_pos1 = self.perspective(p1[0], p1[1], p1[2])
        _x2, _y2, cam_pos2 = self.perspective(p2[0], p2[1], p2[2])
        _sign = (x-_x1)*(x-_x2)+(y-_y1)*(y-_y2)
        if _sign < 0:
            return 1
        elif _sign > 0:
            return -1
        else:
            return 0

    def point_in_polygon(self, x, y, pt):
        # If we look at point_line_sign for all sides of a polygon, + means the point is inside
        # pt is an array of points that are ordered by their order in the polygon
        # For polygons that have a visible a non-visible side, visible side must be ordered clockwise.
        # Works only for CONVEX polygons.
        first = True
        inside = True
        last_p = pt[len(pt)]
        line_side = None
        for p in pt:
            if first:
                line_side = self.point_line_sign(x, y, last_p, p)
            elif inside:
                inside = line_side == self.point_line_sign(x, y, last_p, p)
            last_p = p
        # line_side indicates that visible or invisible side was clicked
        return inside, line_side

    def draw_line(self, c, x1, y1, z1, x2, y2, z2):
        # This routine is no longer used, as we now draw everything with polygons
        # TODO: change function arguments to use points that have point.p_prj
        _x1, _y1, cam_pos1 = self.local_perspective(x1, y1, z1)
        _x2, _y2, cam_pos2 = self.local_perspective(x2, y2, z2)

        # For now, we only draw the line if both points are in front of the camera (z>0)
        if cam_pos1 == 1 == cam_pos2:
            pg.draw.line(self.display.window, c, (_x1, _y1), (_x2, _y2), 1)
        elif cam_pos1 == -1 == cam_pos2:
            pass
        elif cam_pos1 == 0 == cam_pos2:
            pass
        elif cam_pos1 == 1 == -cam_pos2:
            # TODO: Part of line needs to be calculated and drawn
            pass
        elif -cam_pos1 == 1 == cam_pos2:
            # TODO: Part of line needs to be calculated and drawn
            pass
        elif cam_pos1 == 0:
            if cam_pos2 == 1:
                # TODO: Part of line needs to be calculated and drawn
                pass
            else:
                pass
        elif cam_pos2 == 0:
            if cam_pos1 == 1:
                # TODO: Part of line needs to be calculated and drawn
                pass
            else:
                pass
        else:
            pass

    def check_polygon_invisible(self, points):
        p_r_overlap = polygon.polygon_rect_intersect(points, self.display.r)
        if p_r_overlap is None:
            return True
        return False

    def get_projection_points(self, points):
        pt = []
        # Calculate projection of all points in the polygon
        for point in points:
            _x1, _y1, cam_pos = point.p_prj.coords()
            if cam_pos > 0:
                pt.append((_x1, _y1))
        return pt

    def draw_polygon_texture(self, points, tx):
        pts = self.get_projection_points(points)
        if len(pts) > 2:
            tx.draw_polygon_with_texture(self.display.window, pts)

        #    def draw_polygon_texture_refs(self, pt, tx):
        #        if len(pt) > 2:
        #            tx.draw_face(self.display.window, pt)

        #    def draw_polygon_texture(self, points, tx):
        #        if self.check_polygon_invisible(points):
        #            return
        #        pt = self.get_projection_points(points)
        #        if len(pt) > 2:
        #            tx.tempTexture.draw_face(self.display.window, pt)

    def draw_polygon(self, c, points, filled):
        # Skip polygons that are not visible on camera
        if self.check_polygon_invisible(points):
            return
        pt = self.get_projection_points(points)

        # If more than 1 point in front of camera, draw polygon
        # TODO: make this more accurate near z=0
        if len(pt) > 2:
            if filled:
                pg.draw.polygon(self.display.window, c, pt, 0)
            else:
                pg.draw.polygon(self.display.window, c, pt, 1)

    def draw_img(self, _img: image_3D.img3D, x, y, z, w, h):
        # Draws image at projection x,y if in front of Camera
        _x1, _y1, cam_pos = self.perspective(x, y, z)
        # TODO: calculate scaling using perspective (z0/z)
        if cam_pos > 1:
            self.display.window.blit(_img.imgScaled, (_x1 - w // 2, _y1 - h // 2))

###################################################################################################################
#         DRAW POLYGONS THAT PASS THROUGH CAMERA PLANE
###################################################################################################################
    def intersect_2Dx(self, x1, y1, x2, y2, x_border):
        dx, dy = x2 - x1, y2 - y1
        if x1 == x2:
            return
        k = (x_border - x1) / dx
        if 0 < k < 1:
            return x1 + k*dx, y1 + k*dy
        else:
            return

    def intersect_2Dy(self, x1, y1, x2, y2, y_border):
        dx, dy = x2 - x1, y2 - y1
        if y1 == y2:
            return
        k = (y_border - y1) / dy
        if 0 < k < 1:
            return x1 + k*dx, y1 + k*dy
        else:
            return

    def intersect_points_width_display(self, x1, y1, x2, y2):
        pt = []
        x0, y0 = self.display.x0, self.display.y0
        x_min, x_max = self.display.x_min, self.display.x_max
        y_min, y_max = self.display.y_min, self.display.y_max

        p1_in_rect = x_min <= x1 <= x_max and y_min <= y1 <= y_max
        p2_in_rect = x_min <= x2 <= x_max and y_min <= y2 <= y_max
        if p1_in_rect and p2_in_rect:
             return pt
        # Intersection with top of display
        p = self.intersect_2Dy(x1, y1, x2, y2, y_max)
        if p is not None:
            x, y = p
            if x_min < x < x_max:
                pt.append(p)
        # Intersection with bottom of display
        p = self.intersect_2Dy(x1, y1, x2, y2, y_min)
        if p is not None:
            x, y = p
            if x_min < x < x_max:
                pt.append(p)
        # Intersection with left of display
        p = self.intersect_2Dx(x1, y1, x2, y2, x_min)
        if p is not None:
            x, y = p
            if y_min < y < y_max:
                pt.append(p)
        # Intersection with right of display
        p = self.intersect_2Dx(x1, y1, x2, y2, x_max)
        if p is not None:
            x, y = p
            if y_min < y < y_max:
                pt.append(p)
        # SORT BY DISTANCE TO P1. AVOID SQR and SQRT
        if len(pt) == 2:
            if x1 == x2:
                if abs(y1-pt[0][1]) > abs(y1-pt[1][1]):
                    pt[0], pt[1] = pt[1], pt[0]
            else:
                if abs(x1 - pt[0][0]) > abs(x1 - pt[1][0]):
                    pt[0], pt[1] = pt[1], pt[0]
        return pt

    def intersect_3D(self, x1, y1, z1, x2, y2, z2, a, b, c):
        # this function only works for ax+by+cz=0, not for ax+by+cz=d
        # line is P1 + k * direction vector
        # Calculate the direction vector of the line
        dx, dy, dz = x2 - x1, y2 - y1, z2 - z1
        # what if line // plane (direction vector lies in plane)
        if a * dx + b * dy + c * dz == 0:
            return None
        # line is P = P1 + k * dP (direction vector)
        k = -(a * x1 + b * y1 + c * z1) / (a * dx + b * dy + c * dz)
        # Only return points if P between P1 and P2
        if k < 0 or k > 1:
            return None
        # print("intersect_3D", x1 + k * dx, y2 + k * dy, z1 + k * dz)
        # return P = P1 + k * dP
        return spacials.Pt(x1 + k * dx, y2 + k * dy, z1 + k * dz)

    def distance_2D(self,x1, y1, x2, y2):
        return math.sqrt((x2-x1)**2 + (y2-y1)**2)
    def intersect_points_width_pyramid(self, x1, y1, z1, x2, y2, z2):
        # result points have NO P_PRJ, so P_PRJ for extra point has to be handled by caller!!!
        # THIS FUNCTION ASSUMES THAT 0 < x0 < w  and  0 < y0 < h
        pt = []

        x0, y0, z0 = self.display.x0, self.display.y0, self.display.z0
        x_min, x_max = self.display.x_min, self.display.x_max
        y_min, y_max = self.display.y_min, self.display.y_max
        # Intersection with top
        p = self.intersect_3D(x1, y1, z1, x2, y2, z2, 0, z0, -y_min)
        if p is not None:
            if p.z * x_min < p.x * z0 < p.z * x_max:
                x, y, cam_pos = self.perspective(p.x, p.y, p.z)
                pt.append((x, y))
        # Intersection with bottom
        p = self.intersect_3D(x1, y1, z1, x2, y2, z2, 0, z0, -y_max)
        if p is not None:
            if p.z * x_min < p.x * z0 < p.z * x_max:
                x, y, cam_pos = self.perspective(p.x, p.y, p.z)
                pt.append((x, y))
        # Intersection with left
        p = self.intersect_3D(x1, y1, z1, x2, y2, z2, z0, 0, -x_min)
        if p is not None:
            if p.z * y_min < p.y * z0 < p.z * y_max:
                x, y, cam_pos = self.perspective(p.x, p.y, p.z)
                pt.append((x, y))
        # Intersection with right
        p = self.intersect_3D(x1, y1, z1, x2, y2, z2, z0, 0, -x_max)
        if p is not None:
            if p.z * y_min < p.y * z0 < p.z * y_max:
                x, y, cam_pos = self.perspective(p.x, p.y, p.z)
                pt.append((x, y))
        # SORT BY DISTANCE TO P1. AVOID SQR and SQRT
        if len(pt) == 2:
            if x1 == x2:
                if abs(y1-pt[0][1]) > abs(y1-pt[1][1]):
                    pt[0], pt[1] = pt[1], pt[0]
            else:
                if abs(x1 - pt[0][0]) > abs(x1 - pt[1][0]):
                    pt[0], pt[1] = pt[1], pt[0]

        # if len(pt) == 0 and random.randint(1,10) > 5:
        #    pt.append((x_min, y_max))
        #    pt.append((x_min, y_min))
        return pt


    def precalc_for_cam(self, edges):
        for edge in edges:
            edge.q1 = None
            edge.q2 = None
            edge.q3 = None
            p1 = edge.p1
            p2 = edge.p2
            x1, y1, z1 = p1.p_cam.coords()
            x2, y2, z2 = p2.p_cam.coords()
            if z1 < 0 and z2 < 0:  # check for missing corner points
                edge.cross_type = spacials.EDGE_BEHIND  # Must be calculated during draw (uses other Edges of Face)
            if z1 >= 0 and z2 >= 0:  # use projection points
                edge.cross_type = spacials.EDGE_IN_FRONT
                px1, py1 = p1.p_prj.coords_2D()
                px2, py2 = p2.p_prj.coords_2D()
                new_pts = self.intersect_points_width_display(px1, py1, px2, py2)
                if len(new_pts) > 0:
                    edge.q1 = new_pts[0]
                    if len(new_pts) > 1:
                        edge.q2 = new_pts[1]
            if z2 * z1 < 0:  # if we cross camera plane, use camera points 3D
                edge.cross_type = spacials.EDGE_CROSSES
                if z1 > 0:
                    edge.kx = m.copysign(1, z1*(x2-x1)-x1*(z2-z1))
                    edge.ky = m.copysign(1, z1*(y2-y1)-y1*(z2-z1))
                else:
                    edge.kx = m.copysign(1, z2*(x1-x2)-x2*(z1-z2))
                    edge.ky = m.copysign(1, z2*(y1-y2)-y2*(z1-z2))

                new_pts = self.intersect_points_width_pyramid(x1, y1, z1, x2, y2, z2)
                if len(new_pts) > 0:
                    edge.q1 = new_pts[0]
                    if len(new_pts) > 1:
                        edge.q2 = new_pts[1]


    def origin_inside_polygon(self,corner_pos,pt,c):
        inside = True
        x1, y1, z1 = pt[-1].p_cam.coords()
        _x1, _y1, _z1 = corner_pos.local_coordinates(x1, y1, z1)
        test_pt = []
        for p in pt:
            test_pt.append((self.display.x0+_x1, self.display.y0+_y1))
            x2, y2, z2 = p.p_cam.coords()
            _x2, _y2, _z2 = corner_pos.local_coordinates(x2, y2, z2)
            # Teken z-coordinaat vectorieel product geeft draairichting, moet > 0 zijn
            if _x1 * _y2 - _x2 * _y1 > 0:
                #print("False",_x1, _y1,_x2, _y2)
                inside = False
            _x1, _y1 = _x2, _y2
        #pg.draw.polygon(self.display.window,c,test_pt,2)
        #pg.draw.line(self.display.window, YELLOW,(self.display.x0,self.display.y_min), (self.display.x0,self.display.y_max))
        #pg.draw.line(self.display.window, YELLOW,(self.display.x_min,self.display.y0), (self.display.x_max,self.display.y0))
        return inside

    def get_display_intersect_polygon(self, face):
        # creation of a polygon that is the projection of the visible part of the face
        # first check if any point is in front of camera.
        all_edges_behind = True
        for face_edge in face.face_edge:
            edge = face_edge.edge
            all_edges_behind = all_edges_behind and (edge.cross_type == spacials.EDGE_BEHIND)
        # first no point is in front of camera, skip and do not return polygon
        if all_edges_behind:
            return None
        new_pt = []
        corners_needed = False
        for face_edge in face.face_edge:
            # Edges can be oriented in the wrong way, so use p1=P1(), p2=P2()
            # edge, orientation = face_edge.edge, face_edge.orientation
            p1, p2 = face_edge.P1(), face_edge.P2()
            q1, q2 = face_edge.Q1(), face_edge.Q2()
            if q1 is None and p1.cam_pos != spacials.CAM_POS_VISIBLE:
                corners_needed = True
            if p1.cam_pos == spacials.CAM_POS_VISIBLE:
                new_pt.append(p1.p_prj.tuplet())
                if q1 is not None:
                    new_pt.append(q1)
                if q2 is not None:
                    new_pt.append(q2)
            elif p1.cam_pos == spacials.CAM_POS_FRONT_INVISIBLE:
                if q1 is not None:
                    new_pt.append(q1)
                if q2 is not None:
                    new_pt.append(q2)
            elif p1.cam_pos == spacials.CAM_POS_BACK:
                if q1 is not None:
                    new_pt.append(q1)
                if q2 is not None:
                    new_pt.append(q2)

        needs_sorting = False
        if corners_needed:
            #print("corners needed")
            if self.origin_inside_polygon(self.display.pos_TL, face.pt , BLUE):
                needs_sorting = True
                new_pt.append((self.display.x_min, self.display.y_min))
            if self.origin_inside_polygon(self.display.pos_TR, face.pt, GREY):
                needs_sorting = True
                new_pt.append((self.display.x_max, self.display.y_min))
            if self.origin_inside_polygon(self.display.pos_BR, face.pt, GREEN):
                needs_sorting = True
                new_pt.append((self.display.x_max, self.display.y_max))
            if self.origin_inside_polygon(self.display.pos_BL, face.pt, RED):
                needs_sorting = True
                new_pt.append((self.display.x_min, self.display.y_max))
        if needs_sorting:
            n, x, y = len(new_pt), 0, 0
            if n:
                for p in new_pt:
                    x += p[0]
                    y += p[1]
                x_mid, y_mid = x // n, y // n
                new_pt = sorted(new_pt, key=lambda p: -m.atan2(p[0]-x_mid, p[1]-y_mid), reverse=False)
            #print(p)
        #print(new_pt)
        return new_pt

###################################################################################################################
#         END: DRAW POLYGONS THAT PASS THROUGH CAMERA PLANE
###################################################################################################################
