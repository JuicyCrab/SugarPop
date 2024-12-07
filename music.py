#############################################################
# Module Name: Sugar Pop Dynamic Item Module
# Project: Sugar Pop Program
# Date: Dec 6, 2024
# By: Eyasu Smieja 
# Description: The music item of the sugar pop game
#############################################################

import pygame as pg 
from pygame import mixer


class Music:
    def __init__(self):
        # Initialize Pygame mixer
        pg.init()
        pg.mixer.init()

        self.music_songs = {
            "background": pg.mixer.Sound("./music/Game.mp3"),
            "bucket": pg.mixer.Sound("./music/Explosion_Sound.wav"),
            "add_ball": pg.mixer.Sound("./music/Add_ball.wav"),
            "complete_level": pg.mixer.Sound("./music/Complete_level.wav"),
            "failed_level": pg.mixer.Sound("./music/Failed_level.wav"),
        }

        # channels
        self.channel1 = pg.mixer.Channel(0)  # Channel 0 for background music
        self.channel2 = pg.mixer.Channel(1)  # Channel 1 for bucket sound
        self.channel3 = pg.mixer.Channel(2)  # Channel 2 for add ball sound
        self.channel4 = pg.mixer.Channel(3)  # Channel 3 for Complete level sound
        self.channel5 = pg.mixer.Channel(4)  # Channel 4 for Failed level sound
    
    def play(self, key):
        """Play looping background music."""
        sound = self.music_songs.get(key)
        if sound:
            self.channel1.play(sound, loops=0)  # Loop background music indefinitely

    def stop(self):
        """Stop the background music."""
        self.channel1.stop()

    def play_sound_effect(self, key):
        """Play sound effects on their respective channels."""
        sound = self.music_songs.get(key)
        if sound:
            # Assign appropriate channels for specific sound effects
            if key == "bucket":
                self.channel2.play(sound)
            elif key == "add_ball":
                self.channel3.play(sound)
            elif key == "complete_level":
                self.channel4.play(sound)
            elif key == "failed_level":
                self.channel5.play(sound)

