import math as m
import numpy as np

""" Position Class
    Position object defines position AND orientation for any object in the world
    Position provides coordinate transformation between world and object
    Position object can be shared between multiple objects (e.g. airplane,front_cam,back_cam)
"""
angle_mode_xyz = 1
angle_mode_yxz = 2

class Position:
    # Rather than using Euler names alpha,beta,gamma, we use x_angle, y_angle, z_angle because it is clearer
    def __init__(self, x, y, z, x_angle, y_angle, z_angle, angle_mode=angle_mode_yxz):
        # TODO:
        # p_world = np.array([x, y, z])
        # remove self.x, self.y, self.z
        self.angle_mode = angle_mode
        self.x, self.y, self.z = x, y, z
        self.x_angle, self.y_angle, self.z_angle = x_angle, y_angle, z_angle
        # Use numpy arrays for faster calculation
        self.R = np.eye(3)      # 3x3 Identity
        self.R_ = np.eye(3)     # 3x3 Identity
        self.calc_R()

    def calc_R(self):
        if self.angle_mode == angle_mode_xyz:
            self.calc_R_xyz()
        elif self.angle_mode == angle_mode_yxz:
            self.calc_R_yxz()

    def apply_rotation(self, R_rot):
        # We add a rotation to R
        self.R = np.dot(R_rot, self.R)
        # We fix angles accordingly
        self.x_angle, self.y_angle, self.z_angle = self.euler_angles(self.R)

    def calc_R_xyz(self):
        # First version of rotation matrices, x,y,z: no longer used, y, x, z is easier
        sx, cx = m.sin(self.x_angle), m.cos(self.x_angle)
        sy, cy = m.sin(self.y_angle), m.cos(self.y_angle)
        sz, cz = m.sin(self.z_angle), m.cos(self.z_angle)

        self.R[0, 0], self.R[0, 1], self.R[0, 2] = cy * cz, sx * sy * cz - cx * sz, cx * sy * cz + sx * sz
        self.R[1, 0], self.R[1, 1], self.R[1, 2] = cy * sz, sx * sy * sz + cx * cz, cx * sy * sz - sx * cz
        self.R[2, 0], self.R[2, 1], self.R[2, 2] = -sy, sx * cy, cx * cy

        #   RZ-1.RY-1.RX-1 = RZ^T.RY^T.RZ^T = (RZ.RY.RX)^T = R^T:  @CREDITS: SVS
        #   self.R_[0, 0], self.R_[0, 1], self.R_[0, 2] = cy * cz, cy * sz, -sy
        #   self.R_[1, 0], self.R_[1, 1], self.R_[1, 2] = sx * sy * cz - cx * sz, sx * sy * sz + cx * cz, sx * cy
        #   self.R_[2, 0], self.R_[2, 1], self.R_[2, 2] = sy * cx * cz + sx * sz, cx * sy * sz - sx * cz, cx * cy

    def calc_R_yxz(self):
        sx, cx = m.sin(self.x_angle), m.cos(self.x_angle)
        sy, cy = m.sin(self.y_angle), m.cos(self.y_angle)
        sz, cz = m.sin(self.z_angle), m.cos(self.z_angle)

        self.R[0, 0], self.R[0, 1], self.R[0, 2] = cy * cz - sx * sy * sz, -cx * sz, sy*cz + sx * cy * sz
        self.R[1, 0], self.R[1, 1], self.R[1, 2] = cy * sz + sx * sy * cz, cx * cz, sy * sz - sx * cy * cz
        self.R[2, 0], self.R[2, 1], self.R[2, 2] = - cx * sy, sx, cx * cy

        #   RZ-1.RX-1.RY-1 = RZ^T.RX^T.RY^T = (RZ.RX.RY)^T = R^T:  @CREDITS: SVS
        #   self.R_[0, 0], self.R_[0, 1], self.R_[0, 2] = cy * cz - sx * sy * sz, cy * sz + sx * sy * cz, - cx * sy
        #   self.R_[1, 0], self.R_[1, 1], self.R_[1, 2] = - cx * sz, cx * cz, sx
        #   self.R_[2, 0], self.R_[2, 1], self.R_[2, 2] = sy * cz + sx * cy * sz, sy * sz - sx * cy * cz, cx * cy
    def apply_R(self, x, y, z):
        X = np.array([x, y, z])
        Y = np.dot(self.R, X)
        return Y[0], Y[1], Y[2]

    def apply_R_(self, x, y, z):
        X = np.array([x, y, z])
        # Y = np.dot(self.R_, X)    # R_ discontinued
        # X.R = R^T.X^T
        Y = np.dot(X, self.R)
        return Y[0], Y[1], Y[2]

    def translate_xyz(self, x, y, z):
        return x - self.x, y - self.y, z - self.z

    def un_translate_xyz(self, x, y, z):
        return x + self.x, y + self.y, z + self.z

    def local_coordinates(self, x, y, z):
        x, y, z = self.translate_xyz(x, y, z)
        x, y, z = self.apply_R(x, y, z)
        return x, y, z

    def world_coordinates(self, x, y, z):
        x, y, z = self.apply_R_(x, y, z)
        x, y, z = self.un_translate_xyz(x, y, z)
        return x, y, z

    def world_orientation(self, x, y, z):
        x, y, z = self.apply_R_(x, y, z)
        return x, y, z

    def euler_angles(self, R):
        if self.angle_mode == angle_mode_xyz:
            return self.euler_angles_xyz(R)
        elif self.angle_mode == angle_mode_yxz:
            return self.euler_angles_yxz(R)

    def euler_angles_xyz(self, R):
        # First version of euler angles x,y,z: no longer used, y, x, z is easier
        # unique result if order alpha,beta,gamma (x_angle, y_angle, z_angle) is determined
        x_angle = m.atan2(R[2][1], R[2][2])
        y_angle = m.atan2(-R[2][0], m.sqrt(R[0][0]**2+R[1][0]**2))
        z_angle = m.atan2(R[1][0], R[0][0])
        return x_angle, y_angle, z_angle

    def euler_angles_yxz(self, R):
        # Unique result for yxz order (y_angle, x_angle, z_angle)
        # Next line should be ok, because we never increase x_angle ourselves (past 90)
        # We always use matrix + euler conversion, so results always between (-90 .. 90)
        # Using m.asin makes this technically Tait-Bryan @CREDITS: SVS
        x_angle = m.asin(R[2][1])
        y_angle = m.atan2(-R[2][0], R[2][2])
        z_angle = m.atan2(-R[0][1], R[1][1])
        return x_angle, y_angle, z_angle

    def euler_angles_chat(self, R):
        # Version by chatGPT (y and z fixed for right-handed)
        # x_angle kept for inspiration in case m.asin(R[2][1]) in euler_angles_yxz(self,R) gives problems
        # basically atan(sin x, m.sqrt((sinx.cosz)**2+(sinx.siny)**2)=atan(sin x, cos x)=x, so WHY???
        # Unique result for yxz order (y_angle, x_angle, z_angle)
        x_angle = m.atan2(-R[1][2], m.sqrt(R[1][0]**2 + R[1][1]**2))
        y_angle = m.atan2(-R[2][0], R[2][2])
        z_angle = m.atan2(-R[0][1], R[1][1])
        return x_angle, y_angle, z_angle

    def make_angles_small(self):
        self.x_angle = self.convert_2_small(self.x_angle)
        self.y_angle = self.convert_2_small(self.y_angle)
        self.z_angle = self.convert_2_small(self.z_angle)

    def convert_2_small(self, angle):
        # This converts any angle to an angle between -180 and 180
        if angle > m.pi:
            angle -= 2 * m.pi
        elif angle < - m.pi:
            angle += 2 * m.pi
        return angle
