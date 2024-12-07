import pygame as pg
import pymunk
import pymunk.pygame_util
import random

# Initialize Pygame and set up the display
pg.init()
WIDTH, HEIGHT = 800, 600
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Moving Bucket with Collecting Balls")
clock = pg.time.Clock()

# Initialize Pymunk space
space = pymunk.Space()
space.gravity = (0, -900)  # Set gravity (downwards)

# Helper to convert Pymunk coordinates to Pygame
def to_pygame(pos):
    return int(pos[0]), int(HEIGHT - pos[1])

# Create the bucket
def create_bucket(space, x, y, width, height):
    # Create bucket's body
    bucket_body = pymunk.Body(1000, float('inf'), pymunk.Body.DYNAMIC)
    bucket_body.position = x, y
    bucket_body.gravity_scale = 0  # Prevent gravity from affecting the bucket

    # Bottom platform
    bottom = pymunk.Segment(bucket_body, (-width / 2, 0), (width / 2, 0), 5)
    bottom.elasticity = 0.5
    bottom.friction = 1.0

    # Left wall
    left_wall = pymunk.Segment(bucket_body, (-width / 2, 0), (-width / 2, -height), 5)
    left_wall.elasticity = 0.5
    left_wall.friction = 1.0

    # Right wall
    right_wall = pymunk.Segment(bucket_body, (width / 2, 0), (width / 2, -height), 5)
    right_wall.elasticity = 0.5
    right_wall.friction = 1.0

    # Add shapes to the space
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

# Draw a ball
def draw_ball(screen, ball):
    pos = to_pygame(ball.body.position)
    pg.draw.circle(screen, (0, 0, 255), pos, int(ball.radius))

# Main function
def main():
    running = True
    bucket_width = 150
    bucket_height = -100
    bucket_x, bucket_y = WIDTH // 2, 150

    # Create floor and bucket
    create_floor(space)
    bucket_body = create_bucket(space, bucket_x, bucket_y, bucket_width, bucket_height)

    # Ball list
    balls = []

    # Counter for collected balls
    collected_count = 0

    # Game loop
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        # Handle user input
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            bucket_body.apply_impulse_at_local_point((-2000, 0))  # Move left
        if keys[pg.K_RIGHT]:
            bucket_body.apply_impulse_at_local_point((2000, 0))  # Move right

        # Spawn new balls periodically
        if random.random() < 0.02:  # 2% chance each frame
            x = random.randint(100, WIDTH - 100)
            balls.append(create_ball(space, x, HEIGHT - 50))

        # Check for collected balls
        for ball in balls[:]:
            ball_x, ball_y = ball.body.position
            bucket_left = bucket_body.position.x - bucket_width / 2
            bucket_right = bucket_body.position.x + bucket_width / 2
            bucket_bottom = bucket_body.position.y
            if bucket_left <= ball_x <= bucket_right and ball_y <= bucket_bottom:
                # Collect the ball
                space.remove(ball, ball.body)
                balls.remove(ball)
                collected_count += 1
                print(f"Ball collected! Total: {collected_count}")

        # Clear the screen
        screen.fill((255, 255, 255))

        # Draw the floor
        pg.draw.line(screen, (0, 0, 0), (0, HEIGHT - 50), (WIDTH, HEIGHT - 50), 5)

        # Draw the bucket
        draw_bucket(screen, bucket_body, bucket_width, bucket_height)

        # Draw the balls
        for ball in balls:
            draw_ball(screen, ball)

        # Step the physics simulation
        dt = 1 / 60.0
        space.step(dt)

        # Update the display
        pg.display.flip()
        clock.tick(60)

    pg.quit()

if __name__ == "__main__":
    main()