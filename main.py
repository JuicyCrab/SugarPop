#############################################################
# Module Name: Sugar Pop Main Module
# Project: Sugar Pop Program
# Date: Nov 17, 2024
# By: Brett W. Huffman
# Description: The main implementation of the sugar pop game
#############################################################

import pygame as pg
import pymunk  # Import Pymunk library
import sys
from settings import *
import random
import static_item
import dynamic_item
from sugar_grain import Sugar_Grain
import bucket  
import level
import message_display
from music import Music  
from moving_bucket import MovingBucket 
from Heads_Up_Display import HeadsUpDisplay




class Game:
    def __init__(self) -> None:
        #pygame intialization 
        pg.init()

        #Setup screen  
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()
        self.iter = 0
        self.level = None 

        #game music 
        pg.mixer.pre_init()
        self.music = Music()
        # Play game music when the game starts
        self.music.channel1.play(pg.mixer.Sound("./music/Game.mp3"))

        


        # HeadsUpDisplay
        self.font = pg.font.SysFont("Impact", 18)
        self.hud = HeadsUpDisplay(self.screen,self.font,position=(self.screen.get_width()- 230, self.screen.get_height()- 40),level_position=(self.screen.get_width() - 70, 10),
            sugar_position=(2, 0))
        self.sugar_used = 0 

        #Boolean for intro 
        self.is_intro = True

        # Create a Pymunk space with gravity
        self.current_level = 2 #start the level 
        self.level_complete = False
        self.space = pymunk.Space()
        self.space.gravity = (0, -4.8)  # Gravity pointing downwards in Pymunk's coordinate system
        # Iterations defaults to 10. Higher is more accurate collison detection
        self.space.iterations = 30 
        self.is_paused = False 
        self.game_over = False

        self.drawing_lines = []
        self.sugar_grains = []
        self.buckets = []
        #Moving Bucket class intializer 
        self.moving_bucket = MovingBucket(self.space, 335, 678, 50, 46, 10)


        
        self.statics = []
        self.teleportation_zones = []
        self.total_sugar_count = None
        self.level_spout_position = None
        self.level_grain_dropping = None
        self.mouse_down = False
        self.current_line = None
        self.message_display = message_display.MessageDisplay(font_size=72)
        self.total_sugar = 100
        

        # Load the intro image
        self.intro_image = pg.image.load("./images/SugarPop.png").convert()  # Load the intro image
        # Get new height based on correct scale
        scale_height = int(self.intro_image.get_height() * (WIDTH / self.intro_image.get_width()))
        self.intro_image = pg.transform.scale(self.intro_image, (WIDTH, scale_height))  # Scale to screen resolution
        
        pg.time.set_timer(LOAD_NEW_LEVEL, 2000)  # Load in 2 seconds

    def load_level(self, levelnumber=0):
        #The gravity resets for each level. 
        self.space.gravity = (0, -4.8)

        # Destroy any current game objects
        for item in self.sugar_grains:
            item.delete()  # Delete all sugar grains
        for item in self.drawing_lines:
            item.delete() 
        for item in self.buckets:
            item.delete() 
        for item in self.statics:
            item.delete() 
        self.sugar_grains = []
        self.drawing_lines = []  # Clear the list
        self.buckets = []
        self.statics = []
        self.teleportation_zones = []

        new_level = LEVEL_FILE_NAME.replace("X", str(levelnumber))
        self.level = level.Level(new_level)
        
        # Make sure the file was found
        if not self.level or not self.level.data:
            return False

        else:  # Do final steps to start the level
            self.level_grain_dropping = False
            self.level_spout_position = (self.level.data['spout_x'], self.level.data['spout_y'])
            self.build_main_walls()

            if 'teleportations' in self.level.data:  # Ensure teleportations are defined in the JSON
                for tp in self.level.data['teleportations']:
                    self.teleportation_zones.append({
                    'entry': (tp['entry'][0], tp['entry'][1]),  # x and y from entry list
                    'exit': (tp['exit'][0], tp['exit'][1]),    # x and y from exit list 
                    'radius': tp.get('entry_radius', 15)        # radius = 15 
                })
                print(f"Loaded teleportation zones: {self.teleportation_zones}") 
           
            # Load buckets
            for nb in self.level.data['buckets']:
                self.buckets.append(bucket.Bucket(self.space, nb['x'], nb['y'], nb['width'], nb['height'], nb['needed_sugar']))

           #load statics 
            for nb in self.level.data['statics']:
                self.statics.append(static_item.StaticItem(self.space, nb['x1'], nb['y1'], nb['x2'], nb['y2'], nb['color'], nb['line_width'], nb['friction'], nb['restitution']))
            
            #Sugar count 
            self.total_sugar_count = self.level.data['number_sugar_grains']
            pg.time.set_timer(START_FLOW, 5 * 1000)  # 5 seconds
            self.message_display.show_message("Level Up", 10)
            self.level_complete = False
            self.total_sugar_count = self.level.data.get('number_sugar_grains', 0)  # Use 0 as fallback
            self.sugar_used = 0  # Reset sugar used

            #Heads Up display when the level loads
            self.hud.update_level(self.current_level)
            self.hud.update_sugar_count(self.total_sugar, self.sugar_used, self.sugar_grains)   
            return True
        

    def build_main_walls(self):
        '''Build the walls, ceiling, and floor of the screen'''
        # Floor
        floor = static_item.StaticItem(self.space, 0, 0, WIDTH, 0, 'green', 5)
        self.statics.append(floor)
        # Left Wall
        left_wall = static_item.StaticItem(self.space, 0, 0, 0, HEIGHT, 'green')
        self.statics.append(left_wall)
        # Right Wall
        right_wall = static_item.StaticItem(self.space, WIDTH, 0, WIDTH, HEIGHT, 'green')
        self.statics.append(right_wall)
        # Ceiling
        ceiling = static_item.StaticItem(self.space, 0, HEIGHT, WIDTH, HEIGHT, 'green')
        self.statics.append(ceiling)
    
    def check_all_buckets_exploded(self):
        """
        Check if all buckets have exploded.
        """
        return all(bucket.exploded for bucket in self.buckets and self.moving_bucket)

    def update(self):
        '''Update the program physics'''
    
        if self.is_paused or self.game_over:
            return 
       #When the level completes the HUD dissapers and when the level starts it reappears 
        if self.level_complete:
            self.hud_visible = False
        else:
            self.hud_visible = True

        # Keep an overall iterator
        self.iter += 1
        
        # Calculate time since last frame
        delta_time = self.clock.tick(FPS) / 1000.0  # Convert milliseconds to seconds

        # Cap delta_time to prevent instability from large time steps
        time_step = min(delta_time, MAX_TIME_STEP)

        # Step the physics simulation forward with the calculated time_step
        self.space.step(time_step)

        
        # Update our game counter
        if self.iter == 60:
            self.iter = 0

        pg.display.set_caption(f'fps: {self.clock.get_fps():.1f}')
        for grain in self.sugar_grains:
            grain.check_teleport() 
            
        # Only do the following every 20 frames for less system stress
        if self.iter % 20 == 0:
            # Update any messages
            self.message_display.update()
            
            # Calculate buckets count by counting each grain's position
            # First, explode or reset the counter on each bucket
            for i in range(len(self.buckets)-1, -1, -1):
                bucket = self.buckets[i]
                if bucket.exploded and bucket.count >= bucket.needed_sugar:
                    bucket.explode(self.sugar_grains)
                    del self.buckets[i]
                    # Check if all buckets exploded
                    if not self.level_complete and self.check_all_buckets_exploded():
                        self.level_complete = True
                        self.message_display.show_message("Level Complete!", 2)
                        self.music.channel4.play(pg.mixer.Sound("./music/Complete_level.wav"))
                        pg.time.set_timer(LOAD_NEW_LEVEL, 2000)  # Schedule next level load
                        self.hud_visible = False

            # Count the grains in the un-exploded buckets
            for grain in self.sugar_grains:
                for bucket in self.buckets:
                    bucket.collect(grain)
    
            # Collect for moving bucket
            for grain in self.sugar_grains:
                self.moving_bucket.collect(grain)

            for grain in self.sugar_grains:
                #Grains only teleport for level 2 
                if self.current_level == 2:
                    for tp in self.teleportation_zones:
                        entry_x, entry_y = tp['entry']
                        exit_x, exit_y = tp['exit']
                        entry_radius = tp['radius']
                        grain_x = grain.body.position.x
                        grain_y = grain.body.position.y
                
                        # Calculate the distance from the grain to the entry point
                        dx = grain_x - entry_x
                        dy = grain_y - entry_y
                        distance_to_entry = (dx**2 + dy**2) ** 0.5

                        # If the sugar grain's entry radius, teleport the grain
                        if distance_to_entry <= entry_radius:
                            print(f"Teleporting grain to ({exit_x}, {exit_y})")
                            grain.body.position = (exit_x, exit_y)
                            grain.body.velocity = (0, 0)  # Reset motion
                            self.space.reindex_shapes_for_body(grain.body)  
                            break 
                       

                
            # Drop sugar if needed
            if self.level_grain_dropping and not self.game_over:
                # Create new sugar to drop
                new_sugar = Sugar_Grain(self.space, self.level_spout_position[0], self.level_spout_position[1], 0.1)
                self.sugar_grains.append(new_sugar)
                # Check if it's time to stop
                if len(self.sugar_grains) >= self.total_sugar_count:
                    self.level_grain_dropping = False

            #HUD for displaying the level while playing a level
            self.hud.update_level(self.current_level)



    def draw(self):
        '''Draw the overall game. Should call individual item draw() methods'''
        # Clear the screen
        self.screen.fill('dark green')
    

        # Only show the intro screen if we haven't loaded a level yet
        if self.intro_image:
            self.screen.blit(self.intro_image, (0, 0)) 
        else: # Draw the intro image
    
            for bucket in self.buckets:
                bucket.draw(self.screen)

            #draw moving bucket for level 3 
            if self.current_level == 3:
                self.moving_bucket.draw(self.screen) 

            # Draw each sugar grain
            for grain in self.sugar_grains:
                grain.draw(self.screen)

            # Draw the current dynamic line
            if self.current_line is not None:
                self.current_line.draw(self.screen)
            
            # Draw the user-drawn lines
            for line in self.drawing_lines:
                line.draw(self.screen)
            
                
            # Draw any static items
            for static in self.statics:
                static.draw(self.screen)

            if not self.game_over and not self.level_complete and self.level_spout_position:
                    pg.draw.line(
                        self.screen, 
                        (255, 165, 144), 
                        (self.level_spout_position[0], HEIGHT - self.level_spout_position[1] - 10), 
                        (self.level_spout_position[0], HEIGHT - self.level_spout_position[1]), 
                        5
                    )

            # Draw the nozzle (Remember to subtract y from the height)
            for tp in self.teleportation_zones:
                entry_x, entry_y = tp['entry']
                exit_x, exit_y = tp['exit']
                entry_radius = tp['radius']
                pg.draw.circle(self.screen, pg.Color('blue'), (int(entry_x), HEIGHT - int(entry_y)), 20)
                pg.draw.circle(self.screen, pg.Color('pink'), (int(exit_x), HEIGHT - int(exit_y)), 10)


            # Draw the heads-up display
            if not self.game_over and not self.level_complete:

            # Draw the heads-up display
                self.hud.draw(self.buckets, [self.moving_bucket])

            # Show any messages needed        
            self.message_display.draw(self.screen)

        # Update the display
        pg.display.update()

    def check_events(self):
        '''Check for keyboard and mouse events'''
        for event in pg.event.get():
            if event.type == EXIT_APP or event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()

            elif event.type == pg.KEYDOWN and event.key == pg.K_r: #restart 
                    self.current_level -= 1
                    self.message_display.show_message("Restart", 1)
                    pg.time.set_timer(LOAD_NEW_LEVEL, 2000) 

                

            elif event.type == pg.KEYDOWN and event.key == pg.K_UP:
                self.message_display.show_message("Reverse Gravity", 2)  # Show message for 2 seconds
                self.space.gravity = (0, 4.8)
   
            elif event.type == pg.KEYDOWN and event.key == pg.K_DOWN:
                self.message_display.show_message("Normal Gravity ", 2)
                self.space.gravity = (0, -4.8)
               

            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                self.is_paused = not self.is_paused #makes it the opposite 
                self.message_display.show_message("Paused", 1)
            
    


            elif event.type == pg.MOUSEBUTTONDOWN:
                self.mouse_down = True
                # Get mouse position and start a new dynamic line
                mouse_x, mouse_y = pg.mouse.get_pos()
                self.current_line = dynamic_item.DynamicItem(self.space, 'blue')
                self.current_line.add_vertex(mouse_x, mouse_y)
                
            elif event.type == pg.MOUSEBUTTONUP:
                self.mouse_down = False
                if self.current_line:
                    self.drawing_lines.append(self.current_line)
                    self.current_line = None
                
            elif event.type == pg.MOUSEMOTION and self.mouse_down:
                # Get mouse position
                mouse_x, mouse_y = pg.mouse.get_pos()
                if mouse_x == 0 or mouse_x == WIDTH or mouse_y == 0 or mouse_y == HEIGHT:
                    self.mouse_down = False
                if self.current_line and self.iter % 10 == 0:
                    self.current_line.add_vertex(mouse_x, mouse_y)

            elif event.type == START_FLOW:
                self.level_grain_dropping = True
                # Disable the timer after the first trigger
                pg.time.set_timer(START_FLOW, 0)
                
            elif event.type == LOAD_NEW_LEVEL:
                pg.time.set_timer(LOAD_NEW_LEVEL, 0)  # Clear the timer
                self.intro_image = None
                self.is_intro = False  # Set to False when intro is done
                self.current_level += 1
                if not self.load_level(self.current_level):
                    self.message_display.show_message("You Win!", 5)
                    self.game_over = True 
                    self.level_grain_dropping = False
                    pg.time.set_timer(EXIT_APP, 5000)  # Quit game after 5 seconds
                else:
                    self.message_display.show_message(f"Level {self.current_level} Start!", 2)
                    self.hud.update_level(self.current_level)

    # Move the bucket based on arrow keys
            elif event.type == pg.KEYDOWN and event.key == pg.K_LEFT: 
                self.moving_bucket.move_bucket(dx=-10, dy=0)  # Move left

            elif event.type == pg.KEYDOWN and event.key == pg.K_RIGHT:
                    self.moving_bucket.move_bucket(dx=10, dy=0)  # Move right
            
    def run(self):
        '''Run the main game loop'''
        while True:
            self.check_events()
            self.update()
            self.draw()

def main():
    game = Game()
    game.run()

if __name__ == '__main__':
    main()