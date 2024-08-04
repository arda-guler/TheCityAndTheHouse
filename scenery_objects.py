import random
import pywavefront

from model import *
from graphics import Color

class SceneryObject:
    def __init__(self, model, pos, model_type="Normal"):
        self.model = model
        self.pos = pos
        self.model_type = model_type

class RandomBuilding(SceneryObject):
    def __init__(self, pos):
        self.pos = pos
        self.model = Model("cube")
        self.model_type = "Normal"
        self.color = Color(0, 1, 1)
        rand_height = random.uniform(5, 70)
        rand_width = random.uniform(0.3, 0.7) * rand_height
        rand_depth = random.uniform(0.3, 0.7) * rand_height
        for idx_v, v in enumerate(self.model.vertices):
            self.model.vertices[idx_v] = np.array([self.model.vertices[idx_v][0] * rand_width,
                                                   self.model.vertices[idx_v][1] * rand_height,
                                                   self.model.vertices[idx_v][2] * rand_depth])

class RiseBuilding:
    def __init__(self, pos, target_pos, rise_time=10):
        self.pos = pos
        self.model = Model("cube")
        self.original_model = Model("Cube")
        self.model_type = "Normal"
        self.time = 0
        self.rise_time = rise_time
        self.color = Color(0, 1, 1)
        
        self.total_height = random.uniform(5, 70)
        self.width = random.uniform(0.3, 0.7) * self.total_height
        self.depth = random.uniform(0.3, 0.7) * self.total_height

        self.current_height = 0

        self.lightning_poses = []
        self.target_pos = target_pos
        self.lightning_flag = False
        self.lightning_timer = 0
        self.lightning_step_timer = 0
        self.tomb_trigger = False
        
        for idx_v, v in enumerate(self.model.vertices):
            self.model.vertices[idx_v] = np.array([self.model.vertices[idx_v][0] * self.width,
                                                   self.model.vertices[idx_v][1] * self.current_height,
                                                   self.model.vertices[idx_v][2] * self.depth])

    def update(self, dt):
        self.tomb_trigger = False
        
        # RISE
        if self.time <= self.rise_time:
            self.time += dt
            self.current_height = self.total_height * min(self.time/self.rise_time, 1)

            for idx_v, v in enumerate(self.model.vertices):
                self.model.vertices[idx_v] = np.array([self.original_model.vertices[idx_v][0] * self.width,
                                                       self.original_model.vertices[idx_v][1] * self.current_height,
                                                       self.original_model.vertices[idx_v][2] * self.depth])

        # LIGHTNING
        else:
            if self.lightning_step_timer < 0 and not self.lightning_flag:
                # go up
                if len(self.lightning_poses) == 0:
                    self.lightning_poses.append(self.pos + np.array([random.uniform(-3, 3), random.uniform(30, 70), random.uniform(-3, 3)]))
                elif len(self.lightning_poses) < 3:
                    self.lightning_poses.append(self.lightning_poses[-1] + np.array([random.uniform(-3, 3), random.uniform(10, 20), random.uniform(-3, 3)]))

                # go towards target
                else:
                    if np.linalg.norm(self.lightning_poses[-1] - self.target_pos) > 50:
                        new_lightning_pos = self.lightning_poses[-1] + (self.target_pos - self.lightning_poses[-1]) / np.linalg.norm((self.target_pos - self.lightning_poses[-1])) * 20 + np.array([random.uniform(-5, 5), random.uniform(-5, 5), random.uniform(-5, 5)])
                        self.lightning_poses.append(new_lightning_pos)

                    else:
                        self.lightning_poses.append(self.target_pos + np.array([random.uniform(-3, 3), random.uniform(-3, 3),random.uniform(-3, 3)]))

                        # do the lightning
                        self.lightning_flag = True
                        self.tomb_trigger = True
                        self.lightning_timer = 0.3

                self.lightning_step_timer = 2

        self.lightning_timer -= dt
        self.lightning_step_timer -= dt
        
        if self.lightning_timer <= 0 and self.lightning_flag == True:
            self.lightning_flag = False
            self.lightning_poses = []

class Korganhaus:
    def __init__(self, pos, model):
        self.pos = pos
        self.model = model
        self.model_type = "WF"
        self.scale = 1.5
        self.color = Color(1, 0, 0)

class Tombstone:
    def __init__(self, pos, model):
        self.pos = pos
        self.model = model
        self.model_type = "WF"
        self.color = Color(158/255, 87/255, 118/255)
        self.scale = 1.3

class Item:
    def __init__(self, pos, radius, model, message, key=None):
        self.pos = pos
        self.radius = radius
        self.model = model
        self.message = message
        
        self.model_type = "WF"
        self.color = Color(1, 0, 0)
        self.scale = 1.5

        self.key = key
        
