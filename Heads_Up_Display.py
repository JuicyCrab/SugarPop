import pygame as pg
import time 

class HeadsUpDisplay:
    def __init__(self, screen, font, position=(10, 10), level_position=(10, 50), sugar_position=(10, 90), timer_position=(10, 130)):

        self.screen = screen
        self.font = font
        self.position = position
        self.level_position = level_position
        self.sugar_position = sugar_position
        self.timer_postion = timer_position
        self.level = 1
        self.total_sugar = 0  # Total sugar available in the level
        self.sugar_used = 0   # Sugar grains already used
        self.sugar_grains = []  # Current sugar grains on screen
        self.timer_start = 100  # Timer starts at 100 seconds
        self.time_remaining = self.timer_start
        self.timer_last_tick = time.time()
        

    def update_level(self, level):
        """Update the current level."""
        self.level = level

    def update_sugar_count(self, total_sugar, sugar_used, sugar_grains):
        """Update the sugar count values."""
        self.total_sugar = total_sugar
        self.sugar_used = sugar_used
        self.sugar_grains = sugar_grains
        

    def draw_level(self):
        """Draw the current level on the screen."""
        level_text = f"Level: {self.level}"
        level_surface = self.font.render(level_text, True, (255, 255, 255))
        self.screen.blit(level_surface, self.level_position)

    def draw_sugar_count(self):
        """Draw the sugar count on the screen."""
        remaining_sugar = self.total_sugar - len(self.sugar_grains)
        sugar_text = f"Sugar Used: {self.sugar_used}/{self.total_sugar} | Remaining Sugar: {remaining_sugar}"
        sugar_surface = self.font.render(sugar_text, True, (255, 255, 255))
        self.screen.blit(sugar_surface, self.sugar_position)

    def draw_bucket_info(self, buckets, moving_buckets):
        """Draw the bucket information on the screen."""
        bucket_text = f"Buckets: {len(buckets)} | Moving Buckets: {len(moving_buckets)}"
        bucket_surface = self.font.render(bucket_text, True, (255, 255, 255))
        self.screen.blit(bucket_surface, self.position)

    def draw(self, buckets, moving_buckets):
        """
        Draw all HUD components on the screen.
        
        Args:
            buckets: List of static buckets.
            moving_buckets: List of moving buckets.
        """
        self.draw_level()
        self.draw_sugar_count()
        self.draw_bucket_info(buckets, moving_buckets)



