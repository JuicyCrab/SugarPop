#############################################################
# Module Name: Sugar Pop Dynamic Item Module
# Project: Sugar Pop Program
# Date: Dec 6, 2024
# By: Eyasu Smieja 
# Description: The heads up display of the sugar pop game
#############################################################

from settings import HEIGHT

class HeadsUpDisplay:
    def __init__(self, screen, font, position=(10, 10), level_position=(10, 50), sugar_position=(10, 90)):
        self.screen = screen
        self.font = font
        self.position = position
        self.level_position = level_position
        self.sugar_position = sugar_position
        self.level = 1
        self.total_sugar = 0  # Total sugar available in the level
        self.sugar_used = 0   # Sugar grains already used
        self.sugar_grains = []  # Current sugar grains on screen
        self.moving_bucket_needed_sugar = 15
        

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
        sugar_text = f"Total Sugar: {self.total_sugar} | Remaining Sugar: {remaining_sugar}"
        sugar_surface = self.font.render(sugar_text, True, (255, 255, 255))
        self.screen.blit(sugar_surface, self.sugar_position)

    def draw_bucket_info(self, buckets, moving_buckets):
            """Draw the bucket information on the screen."""
            if self.level != 3 :
                moving_buckets.clear()
        
            bucket_text = f"Buckets: {len(buckets)} | Moving Buckets: {len(moving_buckets)}"
            bucket_surface = self.font.render(bucket_text, True, (255, 255, 255))
            self.screen.blit(bucket_surface, self.position)

    def draw_bucket_counters(self, buckets):
        """Draw the sugar grain counters for each bucket, showing a fraction of collected vs needed sugar."""
        for i, bucket in enumerate(buckets):
            # Assume bucket.x and bucket.y represent the position of each bucket
            bucket_x = bucket.bucketx  # Horizontal position of the bucket
            bucket_y = HEIGHT - bucket.buckety # Vertical stacking of counters
            
            # Get the collected count and total needed sugar for each bucket
            collected_count = bucket.get_collected_count()
            total_needed_sugar = bucket.needed_sugar  # Assuming each bucket has this attribute

            # Display as a fraction (collected / total_needed)
            bucket_text = f"{collected_count}/{total_needed_sugar}"

            # Render the text
            bucket_surface = self.font.render(bucket_text, True, (255, 255, 255))

            # Position the text inside the bucket (center it horizontally and vertically)
            bucket_width = bucket.width  # Example width of the bucket
            bucket_height = bucket.height  # Example height of the bucket

            bucket_text_position = (
                bucket_x + (bucket_width - bucket_surface.get_width()) // 2,  # Center horizontally in the bucket
                bucket_y + (bucket_height - bucket_surface.get_height()) // 2  # Center vertically in the bucket
            )

            # Draw the text on the screen
            self.screen.blit(bucket_surface, bucket_text_position)



    
    def draw_moving_bucket_counter(self,moving_buckets):
        """Draw the bucket information on the screen."""

        # Display information about each moving bucket
        for i, moving_bucket in enumerate(moving_buckets):
            # Get the number of grains collected by the moving bucket
            collected_count = moving_bucket.get_collected_count()
            total_needed_sugar = moving_bucket.needed_sugar

            # Use the moving bucket's x, y attributes for position
            moving_bucket_text = f"Moving Bucket {collected_count}/{total_needed_sugar}"
            moving_bucket_position = (moving_bucket.x - 65, HEIGHT -  moving_bucket.y + 30)  # Display above the bucket
            moving_bucket_surface = self.font.render(moving_bucket_text, True, (255, 255, 255))

            # Draw the text near the moving bucket's position
            self.screen.blit(moving_bucket_surface, moving_bucket_position)



    

    def draw(self, buckets, moving_buckets):
        """
        Draw all HUD components on the screen.
        
        Args:
            buckets: List of static buckets.
            moving_buckets: List of moving buckets.
        """
        self.draw_level()
        self.draw_sugar_count()
        self.draw_bucket_info(buckets, moving_buckets)  # Corrected to use moving_buckets
        self.draw_bucket_counters(buckets)
        self.draw_moving_bucket_counter(moving_buckets)




