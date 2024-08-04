import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np
import random

from ui import *

class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

def drawOrigin():
    glBegin(GL_LINES)
    glColor(1,0,0)
    glVertex3f(0,0,0)
    glVertex3f(100,0,0)
    glColor(0,1,0)
    glVertex3f(0,0,0)
    glVertex3f(0,100,0)
    glColor(0,0,1)
    glVertex3f(0,0,0)
    glVertex3f(0,0,100)
    glEnd()

def drawControls(cam, ctrl_state, first_person_ui):
    glPointSize(3)
    
    # aileron, elevator
    drawRectangle2D(7, -3, 10, -6, Color(1, 0, 1), cam, first_person_ui)
    drawPoint2D(8.5 - ctrl_state[0], -4.5 - ctrl_state[1], Color(1, 0, 1), cam, first_person_ui)
    # rudder
    drawRectangle2D(7, -2, 10, -3, Color(1, 0, 1), cam, first_person_ui)
    drawPoint2D(8.5 + ctrl_state[2], -2.5, Color(1, 0, 1), cam, first_person_ui)
    
    glPointSize(1)

def drawPoint(p, color):

    glColor(color.r, color.g, color.b)
        
    glPushMatrix()
    glTranslatef(p.pos[0], p.pos[1], p.pos[2])

    glBegin(GL_POINTS)
    glVertex3f(0, 0, 0)
    glEnd()

    glPopMatrix()

def drawFlatland(cam, flatland, size=5000, divisions=50):
    spacing = 10**(int(math.log(abs(cam.pos[1] - flatland.height) + 2, 10)) + 1)
    # size = abs(cam.pos.y) * 10

    # subdivisions
    scene_spacing = spacing / 10
    N = divisions * 10
    corner_x = (-cam.pos[0] - N * 0.5 * scene_spacing) + cam.pos[0] % (scene_spacing)
    corner_z = (-cam.pos[2] - N * 0.5 * scene_spacing) + cam.pos[2] % (scene_spacing)

    glColor(flatland.color.r/2, flatland.color.g/2, flatland.color.b/2)
    glBegin(GL_LINES)
    for i in range(N + 1):
        cx = corner_x + i * scene_spacing
        z0 = corner_z
        z1 = corner_z + N * scene_spacing
        glVertex3f(cx, flatland.height, z0)
        glVertex3f(cx, flatland.height, z1)

    for i in range(N + 1):
        x0 = corner_x
        x1 = corner_x + N * scene_spacing
        cz = corner_z + i * scene_spacing
        glVertex3f(x0, flatland.height, cz)
        glVertex3f(x1, flatland.height, cz)
    glEnd()

    # superdivisions
    scene_spacing = spacing
    N = divisions
    corner_x = (-cam.pos[0] - N * 0.5 * scene_spacing) + cam.pos[0] % (scene_spacing)
    corner_z = (-cam.pos[2] - N * 0.5 * scene_spacing) + cam.pos[2] % (scene_spacing)

    glColor(flatland.color.r, flatland.color.g, flatland.color.b)
    glBegin(GL_LINES)
    for i in range(N + 1):
        cx = corner_x + i * scene_spacing
        z0 = corner_z
        z1 = corner_z + N * scene_spacing
        glVertex3f(cx, flatland.height, z0)
        glVertex3f(cx, flatland.height, z1)

    for i in range(N + 1):
        x0 = corner_x
        x1 = corner_x + N * scene_spacing
        cz = corner_z + i * scene_spacing
        glVertex3f(x0, flatland.height, cz)
        glVertex3f(x1, flatland.height, cz)
    glEnd()

def drawForces(forces):
    
    for f in forces:
        glPushMatrix()

        scaler = 0.2
        start_position = f.point.pos
        end_position = f.point.pos + f.force
        f_vector = f.force * scaler
        
        f_dir = f_vector.normalized()
        arrowhead_start = f.force * scaler * 0.8

        if not f_dir.cross(vec3(1,0,0)) == vec3(0,0,0):
            arrowhead_vector1 = f_dir.cross(vec3(1,0,0))
        else:
            arrowhead_vector1 = f_dir.cross(vec3(0,1,0))

        arrowhead_vector2 = arrowhead_vector1.cross(f_dir)

        arrowhead_vector1 = arrowhead_vector1 * f.force.mag() * scaler * 0.1
        arrowhead_vector2 = arrowhead_vector2 * f.force.mag() * scaler * 0.1
            
        arrowhead_pt1 = arrowhead_start + arrowhead_vector1
        arrowhead_pt2 = arrowhead_start - arrowhead_vector1

        arrowhead_pt3 = arrowhead_start + arrowhead_vector2
        arrowhead_pt4 = arrowhead_start - arrowhead_vector2
        
        glTranslate(start_position.x, start_position.y, start_position.z)
        glColor(1,0,1)

        glBegin(GL_LINES)

        glVertex3f(0,0,0)
        glVertex3f(f_vector.x, f_vector.y, f_vector.z)

        glVertex3f(arrowhead_pt1.x, arrowhead_pt1.y, arrowhead_pt1.z)
        glVertex3f(arrowhead_pt3.x, arrowhead_pt3.y, arrowhead_pt3.z)

        glVertex3f(arrowhead_pt2.x, arrowhead_pt2.y, arrowhead_pt2.z)
        glVertex3f(arrowhead_pt4.x, arrowhead_pt4.y, arrowhead_pt4.z)

        glVertex3f(arrowhead_pt2.x, arrowhead_pt2.y, arrowhead_pt2.z)
        glVertex3f(arrowhead_pt3.x, arrowhead_pt3.y, arrowhead_pt3.z)

        glVertex3f(arrowhead_pt1.x, arrowhead_pt1.y, arrowhead_pt1.z)
        glVertex3f(arrowhead_pt4.x, arrowhead_pt4.y, arrowhead_pt4.z)

        glVertex3f(arrowhead_pt1.x, arrowhead_pt1.y, arrowhead_pt1.z)
        glVertex3f(f_vector.x, f_vector.y, f_vector.z)

        glVertex3f(arrowhead_pt2.x, arrowhead_pt2.y, arrowhead_pt2.z)
        glVertex3f(f_vector.x, f_vector.y, f_vector.z)

        glVertex3f(arrowhead_pt3.x, arrowhead_pt3.y, arrowhead_pt3.z)
        glVertex3f(f_vector.x, f_vector.y, f_vector.z)

        glVertex3f(arrowhead_pt4.x, arrowhead_pt4.y, arrowhead_pt4.z)
        glVertex3f(f_vector.x, f_vector.y, f_vector.z)

        glEnd()

        glPopMatrix()

def drawModel(model, pos, orient, scale, color=Color(1, 1, 1)):
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    glColor(color.r, color.g, color.b)

    glBegin(GL_LINES)
    for lines in model.lines:
        v1 = model.vertices[lines[0]]
        v2 = model.vertices[lines[1]]

        v1_rot = np.array([[v1[0] * orient[0][0] + v1[1] * orient[1][0] + v1[2] * orient[2][0]],
                           [v1[0] * orient[0][1] + v1[1] * orient[1][1] + v1[2] * orient[2][1]],
                           [v1[0] * orient[0][2] + v1[1] * orient[1][2] + v1[2] * orient[2][2]]])

        v2_rot = np.array([[v2[0] * orient[0][0] + v2[1] * orient[1][0] + v2[2] * orient[2][0]],
                           [v2[0] * orient[0][1] + v2[1] * orient[1][1] + v2[2] * orient[2][1]],
                           [v2[0] * orient[0][2] + v2[1] * orient[1][2] + v2[2] * orient[2][2]]])
        
        glVertex3f(v1_rot[0], v1_rot[1], v1_rot[2])
        glVertex3f(v2_rot[0], v2_rot[1], v2_rot[2])
    glEnd()

    
    for faces in model.faces:
        glBegin(GL_POLYGON)
        vnum = len(faces)
        for i in range(vnum):
            v = model.vertices[faces[i]]
            v_rot = np.array([[v[0] * orient[0][0] + v[1] * orient[1][0] + v[2] * orient[2][0]],
                              [v[0] * orient[0][1] + v[1] * orient[1][1] + v[2] * orient[2][1]],
                              [v[0] * orient[0][2] + v[1] * orient[1][2] + v[2] * orient[2][2]]])

            glVertex3f(v_rot[0], v_rot[1], v_rot[2])
        glEnd()
    
    glPopMatrix()

def drawWFModel(model, pos, orient, scale, color=Color(1, 1, 1)):
    glPushMatrix()
    glTranslate(pos[0], pos[1], pos[2])
    glScale(scale, scale, scale)
    glColor(color.r, color.g, color.b)

    for mesh in model.mesh_list:
        glPolygonMode(GL_FRONT, GL_LINE)
        glBegin(GL_LINES)

        for face in mesh.faces:
            for vertex_i in face:
                glVertex3d(*model.vertices[vertex_i])
        glEnd()

    glPopMatrix()

def drawLightning(building):
    glPushMatrix()
    glColor(1, 1, 1)
    glBegin(GL_LINE_STRIP)
    
    for v in building.lightning_poses:
        glVertex3f(v[0], v[1], v[2])

    glEnd()
    glPopMatrix()

class BRParticle:
    def __init__(self, pos, vel):
        self.pos = pos
        self.vel = vel
        self.destructflag = False

    def update(self, dt):
        self.vel = self.vel + np.array([0, -9.81, 0]) * dt
        self.pos = self.pos + self.vel * dt

        if self.pos[1] <= 0:
            self.destructflag = True

def drawRiseParticles(building, dt, intensity=5):
    if building.time > building.rise_time:
        if hasattr(building, 'particles') and len(building.particles) == 0:
            return
    
    if not hasattr(building, 'particles'):
        building.particles = []

    if building.time < building.rise_time and random.uniform(0, 100) < intensity:
        pos_x = building.pos[0] + random.uniform(0, building.width * 0.5) * random.choice([-1, 1])
        pos_y = 0.1
        pos_z = building.pos[2] + random.uniform(0, building.depth * 0.5) * random.choice([-1, 1])

        vel_y = random.uniform(30, 45)
        vel_x = random.uniform(-5, 5)
        vel_z = random.uniform(-5, 5)
        
        new_particle = BRParticle(np.array([pos_x, pos_y, pos_z]),
                                  np.array([vel_x, vel_y, vel_z]))
        building.particles.append(new_particle)

    for p in building.particles:
        p.update(dt)
        if p.destructflag:
            building.particles.remove(p)
            del p
        
    glPushMatrix()
    glColor(0, 1, 1)
    glBegin(GL_POINTS)

    for p in building.particles:
        glVertex3f(p.pos[0], p.pos[1], p.pos[2])
    
    glEnd()
    glPopMatrix()

def drawScreentext(screentext, cam):
    y_limit_top = 2.5
    y_limit_bottom = -2.75
    x_limit_left = -5.5
    x_limit_right = 5.5

    pline_y = random.uniform(y_limit_bottom, y_limit_top)
    pline_x = random.uniform(x_limit_left, x_limit_right)

    str_len = len(screentext)
    
    if str_len < 31:
        str_graphics_size = str_len * 0.075 * 1.75
    else:
        str_graphics_size = str_len * 0.06 * 1.75
        
    if str_len < 31:
        render_AN(screentext, [1,0,0.2], [max(pline_x - str_graphics_size, -5.5), pline_y], cam, 0.075)
    else:
        render_AN(screentext, [1,0,0.2], [max(pline_x - str_graphics_size, -5.5), pline_y], cam, 0.06)
    
def drawScene(cam, dt, flatland, bodies, scenery_objects, rise_buildings, items, screentext, screentext_timer, first_person_ui=False):
    drawFlatland(cam, flatland)
    for o in scenery_objects[::-1]:
        if o.model_type != "WF":
            drawModel(o.model, o.pos, np.eye(3), 1, o.color)
        else:
            drawWFModel(o.model.modelObj, o.pos, np.eye(3), o.scale, o.color)

    for rb in rise_buildings:
        if rb.lightning_flag:
            drawLightning(rb)

    if len(rise_buildings):
        drawRiseParticles(rise_buildings[-1], dt)

    for itm in items:
        if itm.model_type != "WF":
            drawModel(itm.model, itm.pos, np.eye(3), 1, itm.color)
        else:
            drawWFModel(itm.model.modelObj, itm.pos, np.eye(3), itm.scale, itm.color)

    for b in bodies:
        if b != cam.lock and np.linalg.norm(b.pos - cam.pos) < 1e5:
            drawModel(b.model, b.pos, b.orient, 1, Color(1, 0, 0))
        else:
            drawPoint(o, Color(1, 0, 0))

    if screentext_timer > 0:
        drawScreentext(screentext, cam)

