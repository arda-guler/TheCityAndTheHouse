import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
from scipy.spatial.transform import Rotation

class Camera:
    def __init__(self, name, pos, orient, active, lock=None):
        self.name = name
        self.pos = pos
        self.orient = orient
        self.active = active
        self.lock = lock
        self.offset_amount = 0

        self.yaw = 0
        self.pitch = 0

        self.max_pitch = 60
        self.min_pitch = -80
        
    def get_name(self):
        return self.name

    def get_pos(self):
        return self.pos

    def set_pos(self, new_pos):
        req_trans = new_pos - self.pos
        glTranslate(req_trans[0], req_trans[1], req_trans[2])
        self.pos = new_pos

    def move(self, movement):
        if not self.lock:
            glTranslate((movement[0] * self.orient[0][0]) + (movement[1] * self.orient[1][0]) + (movement[2] * self.orient[2][0]),
                        (movement[0] * self.orient[0][1]) + (movement[1] * self.orient[1][1]) + (movement[2] * self.orient[2][1]),
                        (movement[0] * self.orient[0][2]) + (movement[1] * self.orient[1][2]) + (movement[2] * self.orient[2][2]))

            self.pos = np.array([self.pos[0] + (movement[0] * self.orient[0][0]) + (movement[1] * self.orient[1][0]) + (movement[2] * self.orient[2][0]),
                                 self.pos[1] + (movement[0] * self.orient[0][1]) + (movement[1] * self.orient[1][1]) + (movement[2] * self.orient[2][1]),
                                 self.pos[2] + (movement[0] * self.orient[0][2]) + (movement[1] * self.orient[1][2]) + (movement[2] * self.orient[2][2])])

        else:
            # this handles zooming in and out
            self.offset_amount += movement[2]
            if self.offset_amount <= 0:
                self.offset_amount -= movement[2]

    def get_orient(self):
        return self.orient

    def get_textmtx(self):
        return self.textmtx
    
    def get_active(self):
        return self.active

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def get_lock(self):
        return self.lock

    def calculate_orientation_matrix(self):
        # Calculate the 3x3 orientation matrix based on yaw and pitch
        yaw_matrix = np.array([[np.cos(self.yaw), 0, -np.sin(self.yaw)],
                               [0, 1, 0],
                               [np.sin(self.yaw), 0, np.cos(self.yaw)]])

        pitch_matrix = np.array([[1, 0, 0],
                                 [0, np.cos(self.pitch), np.sin(self.pitch)],
                                 [0, -np.sin(self.pitch), np.cos(self.pitch)]])

        orientation_matrix = np.dot(yaw_matrix, pitch_matrix)
        return orientation_matrix

    def calculate_text_matrix(self):
        # Calculate the 3x3 orientation matrix based on yaw and pitch
        yaw_matrix = np.array([[np.cos(-self.yaw), 0, -np.sin(-self.yaw)],
                               [0, 1, 0],
                               [np.sin(-self.yaw), 0, np.cos(-self.yaw)]])

        pitch_matrix = np.array([[1, 0, 0],
                                 [0, np.cos(-self.pitch), np.sin(-self.pitch)],
                                 [0, -np.sin(-self.pitch), np.cos(-self.pitch)]])

        orientation_matrix = np.dot(pitch_matrix, yaw_matrix)
        return orientation_matrix

    def rotate(self, rotation):
        yaw_delta = rotation[1]
        pitch_delta = rotation[0]

        if self.pitch > np.deg2rad(self.max_pitch) and pitch_delta > 0:
            pitch_delta = 0
        elif self.pitch < np.deg2rad(self.min_pitch) and pitch_delta < 0:
            pitch_delta = 0
        
        # Update yaw and pitch based on input deltas
        self.yaw += yaw_delta
        self.pitch += pitch_delta

        # Keep the pitch within a certain range to avoid gimbal lock
        self.pitch = np.clip(self.pitch, -np.pi / 2, np.pi / 2)

        # Update the orientation matrix
        self.orient = self.calculate_orientation_matrix()
        self.orient[2] = np.cross(self.orient[0], self.orient[1])

        self.textmtx = self.calculate_text_matrix()
        self.textmtx[2] = np.cross(self.textmtx[0], self.textmtx[1])

        # Use OpenGL's glRotate to update the view matrix
        glTranslate(-self.pos[0], -self.pos[1], -self.pos[2])
        glRotatef(np.degrees(yaw_delta), 0, 1, 0)
        glRotatef(np.degrees(pitch_delta), np.cos(self.yaw), 0, np.sin(self.yaw))
        glTranslate(self.pos[0], self.pos[1], self.pos[2])

    def lock_to_target(self, target):
        self.lock = target
        self.set_pos(-self.lock.pos - self.orient[2] * self.offset_amount)

    def unlock(self):
        self.lock = None

    def move_with_lock(self, dt):
        if self.lock:
            self.set_pos(-self.lock.pos - self.orient[2] * self.offset_amount)
            #rot = np.array([self.lock.ang_vel[0], -self.lock.ang_vel[1], self.lock.ang_vel[2]])
            #self.rotate(np.rad2deg(rot * dt))

    def rotate_with_lock(self, dt):
        if self.lock:
            if np.linalg.norm(self.lock.ang_vel) > 0:

                about_pos = -self.lock.pos
                rotation = -self.lock.ang_vel * dt * 180 / 3.14159
        
                glTranslate(-about_pos[0], -about_pos[1], -about_pos[2])
                glRotate(-rotation[0], self.orient[0][0], self.orient[0][1], self.orient[0][2])
                glTranslate(about_pos[0], about_pos[1], about_pos[2])

                glTranslate(-about_pos[0], -about_pos[1], -about_pos[2])
                glRotate(-rotation[1], self.orient[1][0], self.orient[1][1], self.orient[1][2])
                glTranslate(about_pos[0], about_pos[1], about_pos[2])

                glTranslate(-about_pos[0], -about_pos[1], -about_pos[2])
                glRotate(-rotation[2], self.orient[2][0], self.orient[2][1], self.orient[2][2])
                glTranslate(about_pos[0], about_pos[1], about_pos[2])
        
                self.orient = self.lock.orient
