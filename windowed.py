import numpy as np
import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
import glfw
import time
import random
import keyboard as kbd
import mouse
from screeninfo import get_monitors
import ctypes

from rigidbody import *
from model import *
from graphics import *
from camera import *
from terrain import *
from ui import *
from scenery_objects import *
from sound import *
from gametext import *

def hide_cursor():
    ctypes.windll.user32.ShowCursor(False)

def show_cursor():
    ctypes.windll.user32.ShowCursor(True)

def main():
    
    def window_resize(window, width, height):
        try:
            # glfw.get_framebuffer_size(window)
            glViewport(0, 0, width, height)
            glLoadIdentity()
            gluPerspective(fov, width/height, near_clip, far_clip)
            glRotatef(np.rad2deg(main_cam.yaw), 0, 1, 0)
            glRotatef(np.rad2deg(main_cam.pitch), np.cos(main_cam.yaw), 0, np.sin(main_cam.yaw))
            glTranslate(main_cam.pos[0], main_cam.pos[1], main_cam.pos[2])
            #player.orient = np.eye(3)
        except ZeroDivisionError:
            # if the window is minimized it makes height = 0, but we don't need to update projection in that case anyway
            pass

    player_model = Model("cube")
    player_CoM = np.array([0, 0, 0])
    player_pos = np.array([0, 1.7, 80])
    player_vel = np.array([0, 0, 0])
    player_accel = np.array([0, 0, 0])
    player_orient = np.array([[1, 0, 0],
                              [0, 1, 0],
                              [0, 0, 1]])
    player_ang_vel = np.array([0, 0, 0])
    player_ang_accel = np.array([0, 0, 0])
    player_mass = 70
    player_inertia = np.array([[1, 0, 0],
                               [0, 1, 0],
                               [0, 0, 1]])
    player_inertia = player_inertia * 500

    player_speed_multiplier = 1
    player_health_timer = 0
    player_keys = []
    
    player = Player(player_model, player_CoM, player_pos, player_vel, player_accel,
                    player_orient, player_ang_vel, player_ang_accel,
                    player_mass, player_inertia)
    bodies = [player]

    # scenery_objects = [pylon1, pylon2]
    scenery_objects = []

    # RISE BUILDING SETTING
    rise_buildings = []
    rise_chance = 0.01
    rise_perimeter = 1000
    rise_sound_radius = 1000
    rise_cooldown = 10 # initial cooldown
    rise_building_limit = 500

    # KORGANHAUS
    korganmodel = WFModel("korgan")
    korgan = Korganhaus(np.array([0, 0, 0]), korganmodel)
    scenery_objects.append(korgan)

    # BREADS
    bread_A = Item(np.array([320, 0, 502]), 3,
                   WFModel("bread"),
                   "Needs and needs...",
                   "bread")

    bread_B = Item(np.array([605, 0, -442]), 3,
                   WFModel("bread"),
                   "Must bring food...",
                   "bread")

    bread_C = Item(np.array([1071, 0, 36]), 3,
                   WFModel("bread"),
                   "Oh my children...",
                   "bread")

    bread_D = Item(np.array([-117, 0, 990]), 3,
                   WFModel("bread"),
                   "Bread...",
                   "bread")

    bread_E = Item(np.array([251, 0, -780]), 3,
                   WFModel("bread"),
                   "Did I deserve this...",
                   "bread")

    items = [bread_A, bread_B, bread_C, bread_D, bread_E]

    # BUS
    bus = Item(np.array([300, 0, -710]), 7,
               WFModel("bus"),
               "",
               "bus")

    items.append(bus)

    # CEMETERY
    cemetery_x = -20
    cemetery_z = 50
    tomb_x_count = 30
    cemetery_count = tomb_x_count * 5
    tombs = []

    # RANDOM BUILDINGS
    Nx = 60
    Nz = 60
    chance = 0.017
    building_spacing_x = 50
    building_spacing_z = 50

    building_area_corner_x = Nx / 2 * building_spacing_x
    building_area_corner_z = Nz / 2 * building_spacing_z

    buildings = []

    for idx_x in range(Nx):
        for idx_z in range(Nz):
            if random.uniform(0, 1) < chance:
                c_x = -building_area_corner_x + idx_x * building_spacing_x
                c_z = -building_area_corner_z + idx_z * building_spacing_z
                new_pos = np.array([c_x, 0, c_z])

                if not np.linalg.norm(new_pos - korgan.pos) < 100 and not np.linalg.norm(new_pos) < 100:
                    new_building = RandomBuilding(new_pos)
                    scenery_objects.append(new_building)

    # TERRAIN
    print("Initializing terrain...")
    floor = Flatland(0, Color(0.1, 0.8, 0.1))

    # MISC PHYSICS
    gravity = np.array([0.0, -9.81, 0])

    # GRAPHICS
    print("Initializing graphics (OpenGL, glfw)...")
    window_x, window_y = 1280, 720
    fov = 60
    near_clip = 1
    far_clip = 10e5
    
    glfw.init()
    window = glfw.create_window(window_x, window_y, "The City and the House",None, None)
    glfw.set_window_pos(window, 100, 100)
    glfw.make_context_current(window)
    glfw.set_window_size_callback(window, window_resize)

    gluPerspective(fov, window_x/window_y, near_clip, far_clip)
    glClearColor(0, 0, 0.3, 1)

    # SCREENTEXT
    screentext_timer = 5
    screentext = "THE CITY AND THE HOUSE"

    # SOUND
    print("Initializing sound (pygame.mixer)...")
    init_sound()
    play_bgm("kumalak")
    play_sfx("khaus", -1, 6, 0)

    footstep_sfx_timer = 0

    # CAMERA
    cam_pos = np.array([0, 0, 0])
    cam_orient = np.array([[-1, 0, 0],
                           [0, 1, 0],
                           [0, 0, -1]])
    main_cam = Camera("main_cam", cam_pos, cam_orient, True)

    #glRotate(-180, 0, 1, 0)
    main_cam.lock_to_target(bodies[0])

    def move_cam(movement):
        main_cam.move(movement)

    def rotate_cam(rotation):
        main_cam.rotate(rotation)

    # CAMERA CONTROLS
    monitor = get_monitors()[0]
    screen_x = monitor.width
    screen_y = monitor.height
    
    cam_pitch_up = "K"
    cam_pitch_dn = "I"
    cam_yaw_left = "J"
    cam_yaw_right = "L"

    first_person_ui = True
    mouse_rot_active = True

    cam_speed = 100
    cam_rot_speed = 0.03

    # PLAYER CONTROLS
    key_player_fwd = "W"
    key_player_bwd = "S"
    key_player_right = "D"
    key_player_left = "A"

    key_player_sprint = "Shift"

    player_speed = 2
    player_run_speed = 5

    # ENDINGS
    running = True
    
    bus_flag = False
    bread_flag = False
    walk_out_flag = False
    ending_flag = False

    walk_out_timer = 20
    
    bread_text_appeared = False
    bread_collected = False
    bread_ending_timer = 5

    bread_peace_timer = 30;

    print("Starting...")
    dt = 0

    hide_cursor()
    while running and not glfw.window_should_close(window):
        t_cycle_start = time.perf_counter()
        glfw.poll_events()

        # === === === === === === === GAMEPLAY === === === === === === === 
        if not ending_flag:
            mouse_activated_this_frame = False
            player_run_frame = False

            # PERIMETER EFFECTS
            hausdist = np.linalg.norm(player.pos)
            if hausdist > 300:
                green_ratio = 0
                floor.color = Color(0.8, 0.8, 0.8)
                glClearColor(0.2, 0.2, 0.2, 1)

            elif hausdist > 150:
                green_ratio = (300 - hausdist) / 150
                floor.color = Color(0.8 - green_ratio * 0.7, 0.8, 0.8 - 0.7 * green_ratio)
                glClearColor(0.2 - 0.2 * green_ratio, 0.2 - 0.2 * green_ratio, 0.2 + 0.1 * green_ratio, 1)

            else:
                green_ratio = 1
                floor.color = Color(0.1, 0.8, 0.1)
                glClearColor(0, 0, 0.3, 1)

            # CONTROLS
            if kbd.is_pressed("N"):
                mouse_rot_active = False
                show_cursor()
            elif kbd.is_pressed("M"):
                mouse_rot_active = True
                mouse_activated_this_frame = True
                hide_cursor()
            
            if kbd.is_pressed(cam_yaw_left):
                rotate_cam([0, -cam_rot_speed, 0])
            elif kbd.is_pressed(cam_yaw_right):
                rotate_cam([0, cam_rot_speed, 0])

            if kbd.is_pressed(cam_pitch_up):
                rotate_cam([cam_rot_speed, 0, 0])
            elif kbd.is_pressed(cam_pitch_dn):
                rotate_cam([-cam_rot_speed, 0, 0])

            if mouse_rot_active:
                if not mouse_activated_this_frame:
                    m_pos = mouse.get_position()
                    rotate_cam([(m_pos[1] - screen_y*0.5) / screen_y,
                                (m_pos[0] - screen_x * 0.5) / screen_x,
                                0])
                mouse.move(screen_x * 0.5, screen_y * 0.5, True)

            if kbd.is_pressed(key_player_fwd):
                player.vel = player.orient[2]
            elif kbd.is_pressed(key_player_bwd):
                player.vel = -player.orient[2]
            else:
                player.vel = np.array([0, 0, 0])

            if kbd.is_pressed(key_player_right):
                player.vel = player.vel + player.orient[0]
            elif kbd.is_pressed(key_player_left):
                player.vel = player.vel - player.orient[0]
            else:
                player.vel = player.vel + np.array([0, 0, 0])

            player_current_vel = np.linalg.norm(player.vel)
            if player_current_vel > 0:
                if not kbd.is_pressed(key_player_sprint):
                    player.vel = player.vel / player_current_vel * player_speed
                else:
                    player.vel = player.vel / player_current_vel * player_run_speed
                    player_run_frame = True

            footstep_sfx_timer -= dt

            if footstep_sfx_timer <= 0 and player_current_vel > 0.2:
                metal_volume = max(min(hausdist / 1000 * 0.4, 0.4), 0)
                play_sfx(random.choice(["steps/m1", "steps/m2", "steps/m3", "steps/m4"]), 0, 3, (1 - green_ratio) * 0.4)

                play_sfx(random.choice(["steps/g1", "steps/g2", "steps/g3"]), 0, 2, green_ratio * 0.4)

                if player_run_frame:
                    footstep_sfx_timer = 0.4
                else:
                    footstep_sfx_timer = 0.6

            elif player_current_vel < 0.2:
                stop_channel(3)
                stop_channel(2)

            # SCREENTEXT
            screentext_timer -= dt

            # RISING BUILDINGS
            rise_perimeter = max(1000 - len(rise_buildings) * 2, 80)
            
            if rise_cooldown <= 0 and len(rise_buildings) < rise_building_limit: 
                if random.uniform(0, 1) < rise_chance:
                    angle = random.uniform(0, 2 * 3.14159)
                    c_x = rise_perimeter * math.cos(angle)
                    c_z = rise_perimeter * math.sin(angle)
                    new_pos = np.array([c_x, 0, c_z])

                    if not np.linalg.norm(new_pos) < 50 and not np.linalg.norm(new_pos) < 50:
                        new_rise_building = RiseBuilding(new_pos, np.array([0, 50, 0]))
                        rise_buildings.append(new_rise_building)
                        scenery_objects.append(new_rise_building)
                        dist = np.linalg.norm(new_pos - player.pos)
                        # 1 at 10m, drops off to 0.01 at 1000 meters
                        rise_vol = max(min(1.0476 * 2.718**(-0.00465*dist), 1), 0)
                        # play_sfx("rise_motor", 0, 5, rise_vol * 0.3)
                        play_sfx("stone", 0, 4, rise_vol)
                        rise_cooldown = 21

            for r in rise_buildings:
                r.update(dt)

                if r.lightning_flag:
                    # play lightning sound
                    lightning_volume = (5000 - np.linalg.norm(player.pos - (r.pos + r.target_pos) * 0.5)) / 5000
                    play_sfx(random.choice(["lightnings/l1", "lightnings/l2", "lightnings/l3", "lightnings/l4", "lightnings/l5"]), 0, 1, lightning_volume)
                    if lightning_volume > 0.85:
                        rand_bright = random.uniform(0, 0.1)
                        glClearColor(0.8 + rand_bright, 0.8 + rand_bright, 0.8 + rand_bright, 1)
                    else:
                        glClearColor(0.2 + lightning_volume * 0.3, 0.2 + lightning_volume * 0.3, 0.2 + lightning_volume * 0.3, 1)
                    play_sfx(random.choice(["thunder/distant_thunder1", "thunder/distant_thunder2", "thunder/distant_thunder3"]), 0, 5, 1)

                    # add a tombstone
                    if r.tomb_trigger:
                        tomb_idx = len(tombs)
                        if tomb_idx < cemetery_count: # to cemetery
                            tomb_x = (tomb_idx % tomb_x_count) * 1.95
                            tomb_z = tomb_idx // tomb_x_count * 6.5
                            new_tomb = Tombstone(np.array([cemetery_x + tomb_x, 0, cemetery_z + tomb_z]), WFModel("tombstone"))
                            tombs.append(new_tomb)
                            scenery_objects.append(new_tomb)
                            screentext = random.choice(text_lightning)
                            screentext_timer = 5
                        else: # overflow
                            tomb_x = random.uniform(30, 1000) * random.choice([-1, 1])
                            tomb_z = random.uniform(30, 1000) * random.choice([-1, 1])
                            new_tomb = Tombstone(np.array([tomb_x, 0, tomb_z]), WFModel("tombstone"))
                            tombs.append(new_tomb)
                            scenery_objects.append(new_tomb)

            rise_cooldown -= dt

            # ITEMS
            for itm in items:
                if itm.key == "bread":
                    if np.linalg.norm(player.pos - itm.pos) < itm.radius:
                        player_keys.append(itm.key)
                        screentext = itm.message
                        screentext_timer = 5
                        items.remove(itm)
                elif itm.key == "bus":
                    if np.linalg.norm(player.pos - itm.pos) < itm.radius:
                        screentext = "PRESS Y IF YOU WISH TO ABANDON THE HOUSE"
                        screentext_timer = 1

                        if kbd.is_pressed("y"):
                            bus_flag = True
                            ending_flag = True

            # PHYSICS

            # player can't approach Korganhaus
            if hausdist < 50 and not bread_collected:
                player.pos += (player.pos)/hausdist * (50 - hausdist)
                player.pos[1] = 1.7
                screentext = random.choice(text_house)
                screentext_timer = 5
            
            for b in bodies:
                b.vel = b.vel + b.accel * dt
                b.pos = b.pos + b.vel * dt

            bodies[0].orient = np.array([[np.cos(main_cam.yaw), 0, np.sin(main_cam.yaw)],
                                         [0, 1, 0],
                                         [np.sin(main_cam.yaw), 0, -np.cos(main_cam.yaw)]])

            # hit flat ground
            for b in bodies:
                if b.pos[1] < floor.height:
                    b.pos[1] = 0
                    b.vel[1] = 0
                    b.vel = b.vel - b.vel * 0.05 * dt

            # WALKING OUT OF CITY
            if 3950 > np.linalg.norm(player.pos) > 3000 and np.dot(player.vel, player.pos) > 0:
                screentext = "I CAN NOT TRAVEL ON FOOT... MUST TURN BACK"
                screentext_timer = 5

            if np.linalg.norm(player.pos) > 4000:
                walk_out_flag = True
                ending_flag = True
                player.pos = player.pos - np.array([0, 1, 0])

            # GOT FOOD
            if player_keys.count("bread") == 5:
                bread_collected = True

            if bread_collected:
                if not bread_text_appeared:
                    screentext = "I SHOULD GO BACK HOME NOW"
                    screentext_timer = 5
                    bread_text_appeared = True

                if hausdist < 50:
                    screentext = "HOME... I AM HOME"
                    screentext_timer = 5

                    bread_ending_timer -= dt

                if bread_ending_timer < 0:
                    bread_flag = True
                    ending_flag = True
                    player.pos = korgan.pos + np.array([4, 5, -3])
                    main_cam.max_pitch = -80
                    main_cam.min_pitch = -20

            # SOUNDS
            city_volume = min(hausdist / 1000, 1)
            set_channel_volume(7, city_volume)

            khaus_volume = max((200 - hausdist) / 200, 0)
            set_channel_volume(6, khaus_volume)

            # GRAPHICS
            main_cam.move_with_lock(dt)
            
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
            drawScene(main_cam, dt, floor, bodies, scenery_objects, rise_buildings, items, screentext, screentext_timer, first_person_ui)
            
            glfw.swap_buffers(window)

        else:
            if bus_flag: # === === === === === === === BUS ENDING === === === === === === ===
                mouse_activated_this_frame = False
                player_run_frame = False
                
                if mouse_rot_active:
                    if not mouse_activated_this_frame:
                        m_pos = mouse.get_position()
                        rotate_cam([(m_pos[1] - screen_y*0.5) / screen_y,
                                    (m_pos[0] - screen_x * 0.5) / screen_x,
                                    0])
                mouse.move(screen_x * 0.5, screen_y * 0.5, True)

                glClearColor(0.2, 0.2, 0.2, 1)
                
                bus.pos = bus.pos + np.array([0, 0, 15]) * dt
                player.pos = bus.pos + np.array([-0.3, 2, 0])

                # RISING BUILDINGS
                rise_perimeter = max(1000 - len(rise_buildings) * 2, 80)
                
                if rise_cooldown <= 0 and len(rise_buildings) < rise_building_limit: 
                    if random.uniform(0, 1) < rise_chance:
                        angle = random.uniform(0, 2 * 3.14159)
                        c_x = rise_perimeter * math.cos(angle)
                        c_z = rise_perimeter * math.sin(angle)
                        new_pos = np.array([c_x, 0, c_z])

                        if not np.linalg.norm(new_pos) < 50 and not np.linalg.norm(new_pos) < 50:
                            new_rise_building = RiseBuilding(new_pos, np.array([0, 50, 0]))
                            rise_buildings.append(new_rise_building)
                            scenery_objects.append(new_rise_building)
                            dist = np.linalg.norm(new_pos - player.pos)
                            # 1 at 10m, drops off to 0.01 at 1000 meters
                            rise_vol = max(min(1.0476 * 2.718**(-0.00465*dist), 1), 0)
                            # play_sfx("rise_motor", 0, 5, rise_vol * 0.3)
                            play_sfx("stone", 0, 4, rise_vol)
                            rise_cooldown = 21

                for r in rise_buildings:
                    r.update(dt)

                    if r.lightning_flag:
                        # play lightning sound
                        lightning_volume = (5000 - np.linalg.norm(player.pos - (r.pos + r.target_pos) * 0.5)) / 5000
                        play_sfx(random.choice(["lightnings/l1", "lightnings/l2", "lightnings/l3", "lightnings/l4", "lightnings/l5"]), 0, 1, lightning_volume)
                        play_sfx(random.choice(["thunder/distant_thunder1", "thunder/distant_thunder2", "thunder/distant_thunder3"]), 0, 5, 1)
                        if lightning_volume > 0.85:
                            rand_bright = random.uniform(0, 0.1)
                            glClearColor(0.8 + rand_bright, 0.8 + rand_bright, 0.8 + rand_bright, 1)
                        else:
                            glClearColor(0.2 + lightning_volume * 0.3, 0.2 + lightning_volume * 0.3, 0.2 + lightning_volume * 0.3, 1)

                        # add a tombstone
                        if r.tomb_trigger:
                            tomb_idx = len(tombs)
                            if tomb_idx < cemetery_count: # to cemetery
                                tomb_x = (tomb_idx % tomb_x_count) * 1.95
                                tomb_z = tomb_idx // tomb_x_count * 6.5
                                new_tomb = Tombstone(np.array([cemetery_x + tomb_x, 0, cemetery_z + tomb_z]), WFModel("tombstone"))
                                tombs.append(new_tomb)
                                scenery_objects.append(new_tomb)
                                screentext = random.choice(text_bus_lightning)
                                screentext_timer = 5
                            else: # overflow
                                tomb_x = random.uniform(30, 1000) * random.choice([-1, 1])
                                tomb_z = random.uniform(30, 1000) * random.choice([-1, 1])
                                new_tomb = Tombstone(np.array([tomb_x, 0, tomb_z]), WFModel("tombstone"))
                                tombs.append(new_tomb)
                                scenery_objects.append(new_tomb)

                rise_cooldown -= dt

                # SCREENTEXT
                screentext_timer -= dt

                # END GAME
                if np.linalg.norm(bus.pos) > 5000:
                    running = False
                    print("\nENDING 1 OF 4: ABANDONED HOUSE")

                # GRAPHICS
                main_cam.move_with_lock(dt)
                
                glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
                drawScene(main_cam, dt, floor, bodies, scenery_objects, rise_buildings, items, screentext, screentext_timer, first_person_ui)
                
                glfw.swap_buffers(window)

            elif walk_out_flag: # === === === === === === === WALK OUT ENDING === === === === === === === 
                walk_out_timer -= dt

                if int(walk_out_timer) % 2 == 0:
                    player_speed = 0.5
                    player_run_speed = 1
                else:
                    player_speed = 0
                    player_run_speed = 0

                if walk_out_timer < 0:
                    running = False
                    print("\nENDING 3 OF 4: NATURE CALLS BACK")

                # CONTROLS
                mouse_activated_this_frame = False
                player_run_frame = False
                
                if kbd.is_pressed(cam_yaw_left):
                    rotate_cam([0, -cam_rot_speed, 0])
                elif kbd.is_pressed(cam_yaw_right):
                    rotate_cam([0, cam_rot_speed, 0])

                if kbd.is_pressed(cam_pitch_up):
                    rotate_cam([cam_rot_speed, 0, 0])
                elif kbd.is_pressed(cam_pitch_dn):
                    rotate_cam([-cam_rot_speed, 0, 0])

                if mouse_rot_active:
                    if not mouse_activated_this_frame:
                        m_pos = mouse.get_position()
                        rotate_cam([(m_pos[1] - screen_y*0.5) / screen_y,
                                    (m_pos[0] - screen_x * 0.5) / screen_x,
                                    0])
                    mouse.move(screen_x * 0.5, screen_y * 0.5, True)

                if kbd.is_pressed(key_player_fwd):
                    player.vel = player.orient[2]
                elif kbd.is_pressed(key_player_bwd):
                    player.vel = -player.orient[2]
                else:
                    player.vel = np.array([0, 0, 0])

                if kbd.is_pressed(key_player_right):
                    player.vel = player.vel + player.orient[0]
                elif kbd.is_pressed(key_player_left):
                    player.vel = player.vel - player.orient[0]
                else:
                    player.vel = player.vel + np.array([0, 0, 0])

                player_current_vel = np.linalg.norm(player.vel)
                if player_current_vel > 0:
                    if not kbd.is_pressed(key_player_sprint):
                        player.vel = player.vel / player_current_vel * player_speed
                    else:
                        player.vel = player.vel / player_current_vel * player_run_speed
                        player_run_frame = True

                for b in bodies:
                    b.vel = b.vel + b.accel * dt
                    b.pos = b.pos + b.vel * dt

                bodies[0].orient = np.array([[np.cos(main_cam.yaw), 0, np.sin(main_cam.yaw)],
                                             [0, 1, 0],
                                             [np.sin(main_cam.yaw), 0, -np.cos(main_cam.yaw)]])

                # RISING BUILDINGS
                glClearColor(0.2, 0.2, 0.2, 1)
                rise_perimeter = max(1000 - len(rise_buildings) * 2, 80)
                
                if rise_cooldown <= 0 and len(rise_buildings) < rise_building_limit: 
                    if random.uniform(0, 1) < rise_chance:
                        angle = random.uniform(0, 2 * 3.14159)
                        c_x = rise_perimeter * math.cos(angle)
                        c_z = rise_perimeter * math.sin(angle)
                        new_pos = np.array([c_x, 0, c_z])

                        if not np.linalg.norm(new_pos) < 50 and not np.linalg.norm(new_pos) < 50:
                            new_rise_building = RiseBuilding(new_pos, np.array([0, 50, 0]))
                            rise_buildings.append(new_rise_building)
                            scenery_objects.append(new_rise_building)
                            dist = np.linalg.norm(new_pos - player.pos)
                            # 1 at 10m, drops off to 0.01 at 1000 meters
                            rise_vol = max(min(1.0476 * 2.718**(-0.00465*dist), 1), 0)
                            # play_sfx("rise_motor", 0, 5, rise_vol * 0.3)
                            play_sfx("stone", 0, 4, rise_vol)
                            rise_cooldown = 21

                for r in rise_buildings:
                    r.update(dt)

                    if r.lightning_flag:
                        # play lightning sound
                        lightning_volume = (5000 - np.linalg.norm(player.pos - (r.pos + r.target_pos) * 0.5)) / 5000
                        play_sfx(random.choice(["lightnings/l1", "lightnings/l2", "lightnings/l3", "lightnings/l4", "lightnings/l5"]), 0, 1, lightning_volume)
                        play_sfx(random.choice(["thunder/distant_thunder1", "thunder/distant_thunder2", "thunder/distant_thunder3"]), 0, 5, 1)
                        if lightning_volume > 0.85:
                            rand_bright = random.uniform(0, 0.1)
                            glClearColor(0.8 + rand_bright, 0.8 + rand_bright, 0.8 + rand_bright, 1)
                        else:
                            glClearColor(0.2 + lightning_volume * 0.3, 0.2 + lightning_volume * 0.3, 0.2 + lightning_volume * 0.3, 1)

                        # add a tombstone
                        if r.tomb_trigger:
                            tomb_idx = len(tombs)
                            if tomb_idx < cemetery_count: # to cemetery
                                tomb_x = (tomb_idx % tomb_x_count) * 1.95
                                tomb_z = tomb_idx // tomb_x_count * 6.5
                                new_tomb = Tombstone(np.array([cemetery_x + tomb_x, 0, cemetery_z + tomb_z]), WFModel("tombstone"))
                                tombs.append(new_tomb)
                                scenery_objects.append(new_tomb)
                                screentext = random.choice(text_bus_lightning)
                                screentext_timer = 5
                            else: # overflow
                                tomb_x = random.uniform(30, 1000) * random.choice([-1, 1])
                                tomb_z = random.uniform(30, 1000) * random.choice([-1, 1])
                                new_tomb = Tombstone(np.array([tomb_x, 0, tomb_z]), WFModel("tombstone"))
                                tombs.append(new_tomb)
                                scenery_objects.append(new_tomb)

                rise_cooldown -= dt

                # SCREENTEXT
                screentext_timer -= dt

                # GRAPHICS
                main_cam.move_with_lock(dt)
                
                glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
                drawScene(main_cam, dt, floor, bodies, scenery_objects, rise_buildings, items, screentext, screentext_timer, first_person_ui)
                
                glfw.swap_buffers(window)

            elif bread_flag: # === === === === === === === BREAD ENDING === === === === === === === 
                mouse_activated_this_frame = False
                player_run_frame = False
                
                if mouse_rot_active:
                    if not mouse_activated_this_frame:
                        m_pos = mouse.get_position()
                        rotate_cam([-0.005,
                                    (m_pos[0] - screen_x * 0.5) / screen_x,
                                    0])
                mouse.move(screen_x * 0.5, screen_y * 0.5, True)

                bread_peace_timer -= dt
                if bread_peace_timer < 0:
                    running = False
                    print("\nENDING 2 OF 4: PEACE AT LAST")

                # RISING BUILDINGS
                glClearColor(0.2, 0.2, 0.2, 1)
                rise_perimeter = max(1000 - len(rise_buildings) * 2, 80)
                
                if rise_cooldown <= 0 and len(rise_buildings) < rise_building_limit: 
                    if random.uniform(0, 1) < rise_chance:
                        angle = random.uniform(0, 2 * 3.14159)
                        c_x = rise_perimeter * math.cos(angle)
                        c_z = rise_perimeter * math.sin(angle)
                        new_pos = np.array([c_x, 0, c_z])

                        if not np.linalg.norm(new_pos) < 50 and not np.linalg.norm(new_pos) < 50:
                            new_rise_building = RiseBuilding(new_pos, np.array([0, 50, 0]))
                            rise_buildings.append(new_rise_building)
                            scenery_objects.append(new_rise_building)
                            dist = np.linalg.norm(new_pos - player.pos)
                            # 1 at 10m, drops off to 0.01 at 1000 meters
                            rise_vol = max(min(1.0476 * 2.718**(-0.00465*dist), 1), 0)
                            # play_sfx("rise_motor", 0, 5, rise_vol * 0.3)
                            play_sfx("stone", 0, 4, rise_vol)
                            rise_cooldown = 21

                for r in rise_buildings:
                    r.update(dt)

                    if r.lightning_flag:
                        # play lightning sound
                        lightning_volume = (5000 - np.linalg.norm(player.pos - (r.pos + r.target_pos) * 0.5)) / 5000
                        play_sfx(random.choice(["lightnings/l1", "lightnings/l2", "lightnings/l3", "lightnings/l4", "lightnings/l5"]), 0, 1, lightning_volume)
                        play_sfx(random.choice(["thunder/distant_thunder1", "thunder/distant_thunder2", "thunder/distant_thunder3"]), 0, 5, 1)
                        if lightning_volume > 0.85:
                            rand_bright = random.uniform(0, 0.1)
                            glClearColor(0.8 + rand_bright, 0.8 + rand_bright, 0.8 + rand_bright, 1)
                        else:
                            glClearColor(0.2 + lightning_volume * 0.3, 0.2 + lightning_volume * 0.3, 0.2 + lightning_volume * 0.3, 1)

                        # add a tombstone
                        if r.tomb_trigger:
                            tomb_idx = len(tombs)
                            if tomb_idx < cemetery_count: # to cemetery
                                tomb_x = (tomb_idx % tomb_x_count) * 1.95
                                tomb_z = tomb_idx // tomb_x_count * 6.5
                                new_tomb = Tombstone(np.array([cemetery_x + tomb_x, 0, cemetery_z + tomb_z]), WFModel("tombstone"))
                                tombs.append(new_tomb)
                                scenery_objects.append(new_tomb)
                                screentext = random.choice(text_house_lightning)
                                screentext_timer = 5
                            else: # overflow
                                tomb_x = random.uniform(30, 1000) * random.choice([-1, 1])
                                tomb_z = random.uniform(30, 1000) * random.choice([-1, 1])
                                new_tomb = Tombstone(np.array([tomb_x, 0, tomb_z]), WFModel("tombstone"))
                                tombs.append(new_tomb)
                                scenery_objects.append(new_tomb)

                rise_cooldown -= dt

                # SCREENTEXT
                screentext_timer -= dt

                # GRAPHICS
                main_cam.move_with_lock(dt)
                
                glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
                drawScene(main_cam, dt, floor, bodies, scenery_objects, rise_buildings, items, screentext, screentext_timer, first_person_ui)
                
                glfw.swap_buffers(window)

        dt = time.perf_counter() - t_cycle_start

    glfw.destroy_window(window)
    fade_out_bgm()
    time.sleep(2)
    show_cursor()

    if not ending_flag:
        print("ENDING 4 OF 4: THE CITY IS VICTORIOUS")

    # ENDING TEXT
    if not ending_flag:
        with open("ending_4_of_4.txt", "w") as file:
            file.write(text_ending_quit)

    else:
        if bread_flag:
            with open("ending_2_of_4.txt", "w") as file:
                file.write(text_ending_house)

        elif walk_out_flag:
            with open("ending_3_of_4.txt", "w") as file:
                file.write(text_ending_walkout)

        elif bus_flag:
            with open("ending_1_of_4.txt", "w") as file:
                file.write(text_ending_bus)

main()
