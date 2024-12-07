import pygame as pg
import pymunk
from settings import SCALE, HEIGHT, WIDTH
from music import Music
from bucket import Bucket

class MovingBucket:
    def __init__(self, space, x, y, width, height, needed_sugar):
        self.space = space
        self.width = width / SCALE
        self.height = height / SCALE
        self.needed_sugar = needed_sugar
        self.music = Music()
        self.current_bucket = Bucket(space, x, y, width, height, needed_sugar)

    def move(self, new_x, new_y):
        """
        Move the bucket to a new position and create a new bucket instance at the new position.
        """
        # Destroy the current bucket (remove walls, etc.)
        self.current_bucket.delete()

        # Create a new bucket at the new position
        self.current_bucket = Bucket(self.space, new_x, new_y, self.width * SCALE, self.height * SCALE, self.needed_sugar)
        self.music.play_sound_effect("move_bucket")  # Optional: play a sound when moving the bucket

    def draw(self, screen):
        """
        Draw the current bucket to the screen.
        """
        self.current_bucket.draw(screen)

    def get_collected_count(self):
        """
        Return the number of collected sugar grains in the current bucket.
        """
        return self.current_bucket.get_collected_count()

    def collect(self, sugar_grain):
        """
        Collect sugar grains with the current bucket.
        """
        return self.current_bucket.collect(sugar_grain)
