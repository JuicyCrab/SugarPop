#############################################################
# Module Name: Sugar Pop Dynamic Item Module
# Project: Sugar Pop Program
# Date: Dec 6, 2024
# By: Eyasu Smieja 
# Description: The Moving bucket implemtation of the sugar pop game
#############################################################

import pygame as pg
import pymunk
from settings import SCALE, HEIGHT, WIDTH
from music import Music
from math import sqrt

class MovingBucket:
    def __init__(self, space, x, y, width, height, needed_sugar):
        self.music = Music()
        self.space = space
        self.width = width / SCALE
        self.height = height / SCALE
        self.count = 0  # Counter for collected sugar grains
        self.needed_sugar = needed_sugar
        self.collected_sugar = []
        self.grain_constraints = [] 

        # Convert Pygame coordinates to Pymunk coordinates
        self.x = x
        self.y = HEIGHT - y  # Adjust for Pygame/Y-axis inversion

        self.width = width / SCALE
        self.height = height / SCALE

    
        """Create or update the walls of the bucket based on its current position."""
        wall_thickness = 0.2  # Thickness of the walls in physics units
        x_pymunk = self.x / SCALE
        y_pymunk = self.y / SCALE

        # Left wall
        left_wall_start = (x_pymunk - self.width / 2, y_pymunk - self.height / 2)
        left_wall_end = (x_pymunk - self.width / 2, y_pymunk + self.height / 2)
        self.left_wall = pymunk.Segment(self.space.static_body, left_wall_start, left_wall_end, wall_thickness)
        self.left_wall.friction = 0.5
        self.left_wall.elasticity = 0.5
        self.space.add(self.left_wall)

        # Right wall
        right_wall_start = (x_pymunk + self.width / 2, y_pymunk - self.height / 2)
        right_wall_end = (x_pymunk + self.width / 2, y_pymunk + self.height / 2)
        self.right_wall = pymunk.Segment(self.space.static_body, right_wall_start, right_wall_end, wall_thickness)
        self.right_wall.friction = 0.5
        self.right_wall.elasticity = 0.5
        self.space.add(self.right_wall)

        # Bottom wall
        bottom_wall_start = (x_pymunk - self.width / 2, y_pymunk - self.height / 2)
        bottom_wall_end = (x_pymunk + self.width / 2, y_pymunk - self.height / 2)
        self.bottom_wall = pymunk.Segment(self.space.static_body, bottom_wall_start, bottom_wall_end, wall_thickness)
        self.bottom_wall.friction = 0.5
        self.bottom_wall.elasticity = 0.5
        self.space.add(self.bottom_wall)

        self.exploded = False  # Track if the bucket has exploded

    def move_bucket(self, dx, dy):
        """Move the bucket by the given dx, dy values and update its walls."""
        if self.exploded:
            return  # Do not move if the bucket has exploded

        # Update bucket position
        self.x += dx
        self.y += dy

        # Remove the old walls
        self.space.remove(self.left_wall, self.right_wall, self.bottom_wall)

        # Create new walls based on the updated position
        wall_thickness = 0.2  # Thickness of the walls in physics units
        x_pymunk = self.x / SCALE
        y_pymunk = self.y / SCALE

        # Left wall
        left_wall_start = (x_pymunk - self.width / 2, y_pymunk - self.height / 2)
        left_wall_end = (x_pymunk - self.width / 2, y_pymunk + self.height / 2)
        self.left_wall = pymunk.Segment(self.space.static_body, left_wall_start, left_wall_end, wall_thickness)

        # Right wall
        right_wall_start = (x_pymunk + self.width / 2, y_pymunk - self.height / 2)
        right_wall_end = (x_pymunk + self.width / 2, y_pymunk + self.height / 2)
        self.right_wall = pymunk.Segment(self.space.static_body, right_wall_start, right_wall_end, wall_thickness)

        # Bottom wall
        bottom_wall_start = (x_pymunk - self.width / 2, y_pymunk - self.height / 2)
        bottom_wall_end = (x_pymunk + self.width / 2, y_pymunk - self.height / 2)
        self.bottom_wall = pymunk.Segment(self.space.static_body, bottom_wall_start, bottom_wall_end, wall_thickness)

        # Add the new walls back into the space
        self.space.add(self.left_wall, self.right_wall, self.bottom_wall)

    
    def get_collected_count(self):
        """Return the number of sugar grains collected in this bucket."""
        return self.count

    def explode(self, grains):
        """Apply a radial force to all grains near the bucket and remove the bucket walls."""
        if self.exploded:
            return  # Prevent multiple explosions

        # Get the bucket's center position
        bucket_center_x = (self.left_wall.a[0] + self.right_wall.a[0]) / 2
        bucket_center_y = (self.left_wall.a[1] + self.left_wall.b[1]) / 2

        # Apply radial force to each grain
        for grain in grains:
            grain_pos = grain.body.position
            dx = grain_pos.x - bucket_center_x
            dy = grain_pos.y - bucket_center_y
            distance = sqrt(dx**2 + dy**2)

            if distance < 2:  # Only affect grains within a certain radius
                if distance > 0:
                    dx /= distance
                    dy /= distance

                # Apply a radial impulse (adjust magnitude as needed)
                impulse_magnitude = 20 / (distance + 0.1)
                impulse = (dx * impulse_magnitude, dy * impulse_magnitude)
                grain.body.apply_impulse_at_world_point(impulse, grain.body.position)

        # Remove constraints
        for constraint in self.grain_constraints:
            self.space.remove(constraint)
        self.grain_constraints.clear()

        # Remove the bucket walls
        self.space.remove(self.left_wall, self.right_wall, self.bottom_wall)
        self.exploded = True

    def draw(self, screen):
        """Draw the bucket with an open top on the Pygame screen."""
        if self.exploded:
            return

        color = (144, 238, 144)  # Light green color

        # Helper function to convert Pymunk coordinates to Pygame coordinates
        def to_pygame(p):
            return int(p[0] * SCALE), int(HEIGHT - p[1] * SCALE)

        # Draw the bucket edges
        pg.draw.line(screen, color, to_pygame(self.left_wall.a), to_pygame(self.left_wall.b), 2)
        pg.draw.line(screen, color, to_pygame(self.right_wall.a), to_pygame(self.right_wall.b), 2)
        pg.draw.line(screen, color, to_pygame(self.bottom_wall.a), to_pygame(self.bottom_wall.b), 2)

    def count_reset(self):
        """Reset the collected count."""
        if not self.exploded:
            self.count = 0

    def collect(self, sugar_grain):
        """
        Check if a sugar grain is within the bucket bounds and, if so, increase the bucket's count.
        
        :param sugar_grain: The sugar grain to check.
        :return: True if the grain was collected, False otherwise.
        """
        if self.exploded:
            return  # Don't count grains if the bucket has exploded

        # Get the grain's position
        grain_pos = sugar_grain.body.position

        # Calculate the bucket boundaries using the wall positions
        left = self.left_wall.a[0]  # x-coordinate of the left wall
        right = self.right_wall.a[0]  # x-coordinate of the right wall
        bottom = self.bottom_wall.a[1]  # y-coordinate of the bottom wall
        top = self.left_wall.b[1]  # y-coordinate of the top of the left wall

        # Check if the grain's position is within the bucket's bounding box
        if left <= grain_pos.x <= right and bottom <= grain_pos.y <= top:
            if sugar_grain not in self.collected_sugar:  # Avoid double-collecting
                self.collected_sugar.append(sugar_grain)
                self.count += 1  # Increase count
                self.music.play_sound_effect("add_ball")  # Play sound effect

                # Check if the bucket should explode
                if self.count >= self.needed_sugar and not self.exploded:
                    self.explode(self.collected_sugar)  # Trigger explosion
                    self.music.play_sound_effect("bucket")
                      # Play explosion sound
                return True  # Indicate successful collection

        return False


    def delete(self):
        """Delete the bucket and its walls."""
        if not self.exploded:
            self.space.remove(self.left_wall, self.right_wall, self.bottom_wall)
            self.exploded = True
