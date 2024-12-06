import pymunk
import pygame as pg
from settings import HEIGHT, WIDTH

class MovingBucket:
    def __init__(self, space, x, y, width, height, speed):
        self.space = space
        self.width = width
        self.height = height
        self.speed = speed
        self.collected_sugar = 0  # Tracks the number of sugar grains collected
        self.needed_sugar = 10   # Example threshold to "fill" the bucket
        self.exploded = False    # Tracks if the bucket has exploded (optional)

        # Create bucket's body (dynamic)
        self.body = pymunk.Body(1000, float('inf'), pymunk.Body.DYNAMIC)
        self.body.position = x, HEIGHT - y  # Keep y directly consistent with the simulation

        # Custom velocity function to restrict vertical movement
        def limit_vertical_velocity(body, gravity, damping, dt):
            body.velocity = body.velocity.x, 0  # Restrict vertical velocity to 0
        self.body.velocity_func = limit_vertical_velocity

        # Create the segments (walls of the bucket)
        self.bottom = pymunk.Segment(self.body, (-width / 2, 0), (width / 2, 0), 5)
        self.left = pymunk.Segment(self.body, (-width / 2, 0), (-width / 2, -height), 5)
        self.right = pymunk.Segment(self.body, (width / 2, 0), (width / 2, -height), 5)

        # Set the elasticity and friction for interactions
        for shape in [self.bottom, self.left, self.right]:
            shape.elasticity = 0.1
            shape.friction = 0.5
            shape.filter = pymunk.ShapeFilter(categories=0b1)  # Assign collision layer 1

        self.space.add(self.body, self.bottom, self.left, self.right)

    def move(self, direction):
        # Apply force for smoother movement
        force = direction * self.speed
        self.body.apply_force_at_local_point((force, 0))

    def collect(self, sugar_grain):
        """
        Check if a sugar grain is inside the bucket and collect it.
        """
        bucket_left = self.body.position.x - self.width / 2
        bucket_right = self.body.position.x + self.width / 2
        bucket_top = self.body.position.y
        bucket_bottom = self.body.position.y - self.height

        # Get the sugar grain's position
        grain_pos = sugar_grain.body.position

        # Check if the grain is within the bucket's bounds
        if bucket_left <= grain_pos.x <= bucket_right and bucket_bottom <= grain_pos.y <= bucket_top:
            self.collected_sugar += 1
            sugar_grain.delete()  # Remove the grain from the simulation
            print(f"Collected sugar! Total: {self.collected_sugar}")

            # Check if the bucket is "full" (optional)
            if self.collected_sugar >= self.needed_sugar and not self.exploded:
                self.explode()

    def explode(self):
        """
        Handle what happens when the bucket is full (optional).
        """
        print("Bucket is full and explodes!")
        self.exploded = True
        # Add any additional logic, such as playing an animation or removing the bucket

    def draw(self, screen):
        # Draw the bucket on the screen
        color = (200, 0, 200) if not self.exploded else (255, 0, 0)
        pos = self.body.position
        pg.draw.line(screen, color, (pos.x - self.width / 2, pos.y), (pos.x + self.width / 2, pos.y), 3)
        pg.draw.line(screen, color, (pos.x - self.width / 2, pos.y), (pos.x - self.width / 2, pos.y - self.height), 3)
        pg.draw.line(screen, color, (pos.x + self.width / 2, pos.y), (pos.x + self.width / 2, pos.y - self.height), 3)



