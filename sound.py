import os
import random

def get_os_type():
    return os.name

def clear_cmd_terminal(os_name):
    if os_name == "nt":
        os.system("cls")
    else:
        os.system("clear")

os_name = get_os_type()
from pygame import mixer
clear_cmd_terminal(os_name) # __|__
bgms = {}
sfxs = {}

def init_sound():
    global bgms, sfxs
    mixer.init()

    for bgm in os.listdir("data/bgm/"):
        try:
            newmsc = mixer.Sound("data/bgm/" + bgm)
            bgms[bgm[:-4]] = newmsc
        except:
            pass

    for sfx in os.listdir("data/sfx/"):
        try:
            newsfx = mixer.Sound("data/sfx/" + sfx)
            sfxs[sfx[:-4]] = newsfx
        except:
            pass

    for sfx in os.listdir("data/sfx/steps/"):
        try:
            newsfx = mixer.Sound("data/sfx/steps/" + sfx)
            sfxs["steps/" + sfx[:-4]] = newsfx
        except:
            pass

    for sfx in os.listdir("data/sfx/lightnings/"):
        try:
            newsfx = mixer.Sound("data/sfx/lightnings/" + sfx)
            sfxs["lightnings/" + sfx[:-4]] = newsfx
        except:
            pass

    for sfx in os.listdir("data/sfx/thunder/"):
        try:
            newsfx = mixer.Sound("data/sfx/thunder/" + sfx)
            sfxs["thunder/" + sfx[:-4]] = newsfx
        except:
            pass

def play_sfx(track, loops=0, channel=1, volume=1):
    global sfxs
    chn = mixer.Channel(channel)
    # track_full = "data/sfx/" + str(track) + ".mp3"
    # snd = mixer.Sound(track_full)
    snd = sfxs[track]
    chn.set_volume(volume)
    chn.play(snd, loops)

def get_channel_busy(channel):
    chn = mixer.Channel(channel)
    return chn.get_busy()

def is_music_playing():
    return get_channel_busy(7)

def set_channel_volume(channel, volume):
    channel = mixer.Channel(channel)
    channel.set_volume(volume)

def stop_channel(channel):
    channel = mixer.Channel(channel)
    channel.stop()

def fade_out_channel(channel_num):
    channel = mixer.Channel(channel_num)
    channel.fadeout(2000)

def fade_out_bgm(fade_time = 2000):
    chn = mixer.Channel(7)
    chn.fadeout(fade_time)

def play_bgm(track, channel=7):
    global bgms
    
    chn = mixer.Channel(7)
    msc = bgms[track]
    chn.set_volume(1)
    chn.play(msc, -1)

def play_random_bgm(channel=7):
    chn = mixer.Channel(7)
    
    if get_channel_busy(7):
        chn.fadeout(2000)
        
    msc = random.choice(list(bgms.values()))
        
    chn.set_volume(1)
    chn.play(msc)
