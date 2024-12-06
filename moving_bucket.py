import pygame as pg 
import pymunk 
def create_bucket(space, x, y, width, height):
    # Create bucket's body
    bucket_body = pymunk.Body(1000, float('inf'), pymunk.Body.DYNAMIC)
    bucket_body.position = x, y
    bucket_body.gravity_scale = 0

    # Bottom platform
    bottom = pymunk.Segment(bucket_body, (-width / 2, 0), (width / 2, 0), 5)
    bottom.elasticity = 0.5
    bottom.friction = 1.0

    # Left wall
    left_wall = pymunk.Segment(bucket_body, (-width / 2, 0), (-width / 2, -height), 5)
    left_wall.elasticity = 0.5

    # Right wall
    right_wall = pymunk.Segment(bucket_body, (width / 2, 0), (width / 2, -height), 5)
    right_wall.elasticity = 0.5

    # Add to space
    space.add(bucket_body, bottom, left_wall, right_wall)

    return bucket_body

# Create a floor
def create_floor(space):
    floor = pymunk.Segment(space.static_body, (0, 50), (WIDTH, 50), 5)
    floor.elasticity = 0.8
    space.add(floor)

# Create a ball
def create_ball(space, x, y, radius=10):
    body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, radius))
    body.position = x, y
    shape = pymunk.Circle(body, radius)
    shape.elasticity = 0.6
    shape.friction = 0.8
    space.add(body, shape)
    return shape

# Draw the bucket
def draw_bucket(screen, bucket_body, width, height):
    color = (200, 0, 200)
    pos = bucket_body.position
    pg.draw.line(screen, color, to_pygame((pos.x - width / 2, pos.y)), to_pygame((pos.x + width / 2, pos.y)), 3)  # Bottom
    pg.draw.line(screen, color, to_pygame((pos.x - width / 2, pos.y)), to_pygame((pos.x - width / 2, pos.y - height)), 3)  # Left
    pg.draw.line(screen, color, to_pygame((pos.x + width / 2, pos.y)), to_pygame((pos.x + width / 2, pos.y - height)), 3)  # Right
