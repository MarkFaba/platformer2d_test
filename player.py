import csv
import pygame
from pygame.math import Vector2

TILE_SIZE = 32
# Define colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DIRT = (139, 69, 19)

class UnWalkableTile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

unwalkable_tiles = []

with open('IntGrid_layer.csv', 'r') as f:
    reader = csv.reader(f)
    unwalkable_tiles = list(reader)

unwalkable_tile_group = pygame.sprite.Group()
for row in range(len(unwalkable_tiles)):
    for col in range(len(unwalkable_tiles[row])):
        if unwalkable_tiles[row][col] == '1':
            unwalkable_tile = UnWalkableTile(col * TILE_SIZE, row * TILE_SIZE)
            unwalkable_tile_group.add(unwalkable_tile)

# Air class
class Air:
    def __init__(self):
        self.gravity = 1

    def get_gravity(self):
        return self.gravity


# Ground class
class Dirt:
    def __init__(self):
        self.horizontal_velocity_modifier = 3.0
        self.normal_force = 1000

    def get_horizontal_velocity_modifier(self):
        return self.horizontal_velocity_modifier


# # class soulsand: slowly gain velocity from 0 to 50% of rabbit walk_speed in a span 3 seconds
# # when the rabbit start walking. After 3 seconds, 
# # the rabbit can maintain the 50% walk_speed. 
# # Every time the rabbit stops moving, this is reset.
# class SoulSand:
#     def __init__(self):
#         self.start_time = 0
#         self.speed_modifier = 0

#     def get_speed_modifier(self, is_walking):
#         if is_walking:
#             if self.start_time == 0:
#                 self.start_time = pygame.time.get_ticks()
#             elapsed_time = pygame.time.get_ticks() - self.start_time
#             if elapsed_time < 3000:
#                 self.speed_modifier = elapsed_time / 3000 * 0.5
#             else:
#                 self.speed_modifier = 0.5
#         else:
#             self.start_time = 0
#             self.speed_modifier = 0
#         return self.speed_modifier

# # TODO: class ice: gain velocity from 0 to 200% of rabbit walk_speed in a span of 3 seconds
# # when the rabbit start walking. After 3 seconds,
# # the rabbit can maintain the 200% walk_speed.
# # Every time the rabbit stops moving, this is reset.
# # When the rabbit stops moving, velocity is decayed to 0 in a span of 3 seconds.
# class Ice:
#     def __init__(self):
#         self.start_time = 0
#         self.stop_time = 0
#         self.speed_modifier = 0

#     def get_speed_modifier(self, is_walking):
#         current_time = pygame.time.get_ticks()
#         if is_walking:
#             if self.start_time == 0:
#                 self.start_time = current_time
#             elapsed_time = current_time - self.start_time
#             if elapsed_time < 3000:
#                 self.speed_modifier = elapsed_time / 3000 * 2.0
#             else:
#                 self.speed_modifier = 2.0
#             self.stop_time = 0
#         else:
#             if self.stop_time == 0:
#                 self.stop_time = current_time
#             elapsed_time = current_time - self.stop_time
#             if elapsed_time < 3000:
#                 self.speed_modifier = 2.0 - elapsed_time / 3000 * 2.0
#             else:
#                 self.speed_modifier = 0
#             self.start_time = 0
#         return self.speed_modifier


class Rabbit(pygame.sprite.Sprite):
    def __init__(self, x, y, image, health_capacity, current_health):
        super().__init__()
        self.original_image = image
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.position = Vector2(x, y)
        self.velocity = Vector2(0, 0) 
        self.health_capacity = health_capacity
        self.current_health = current_health
        self.is_walking_left = False
        self.is_walking_right = False
        self.is_on_ground = False
        self.ground_type = Dirt()
        self.air_type = Air()
        print(self.rect)

    def update_image_direction(self):
        if self.is_walking_left:
            self.image = pygame.transform.flip(self.original_image, True, False)
        elif self.is_walking_right:
            self.image = self.original_image

    def check_collision(self):
        current_position = self.position
        # Check collision with unwalkable tiles
        # Duct tape approach
        hit_list = pygame.sprite.spritecollide(self, unwalkable_tile_group, False)
        if len(hit_list) > 0:
            if current_position.y <= hit_list[0].rect.top: # rabbit head above or equal height to tile
                self.rect.bottom = hit_list[0].rect.top # a feature, not a bug
                self.position.y = self.rect.y
                self.land()
                return 
            elif current_position.y > hit_list[0].rect.top: # rabbit head below tile
                self.rect.top = hit_list[0].rect.bottom
                self.position.y = self.rect.y
                self.velocity.y = 0
                return
        else:
            self.is_on_ground = False
    
    def check_collision_horizontal(self):
        current_position = self.position
        # Check collision with unwalkable tiles
        # Duct tape approach
        hit_list = pygame.sprite.spritecollide(self, unwalkable_tile_group, False)
        if len(hit_list) > 0:
            if current_position.x <= hit_list[0].rect.left:
                self.velocity.x = 0
                self.rect.right = hit_list[0].rect.left
                self.position.x = self.rect.x
                return
            elif current_position.x > hit_list[0].rect.left:
                self.velocity.x = 0
                self.rect.left = hit_list[0].rect.right
                self.position.x = self.rect.x
                return
        
    def move(self):
        # Update position based on velocity on that direction
        self.position += self.velocity
        # Update velocity based on air type, only vertical velocity is affected
        if not self.is_on_ground:
            self.velocity.y += self.air_type.get_gravity() # Current value: 1

    def is_moving(self):
        return self.velocity.x != 0 or self.velocity.y != 0

    def jump(self, keys):
        # jump can only be triggered by a key, the rabbit must be on the ground
        # jump creates a vertical velocity boost of 20
        if keys[pygame.K_SPACE] and self.is_on_ground:
            print("Jump")
            self.is_on_ground = False
            self.velocity.y = -20
            
    def land(self):
        # land on the ground, reset vertical velocity, set is_on_ground to True
        # take damage if current vertical velocity is greater than 30
        if self.velocity.y > 30:
            self.current_health -= 1
        self.velocity.y = 0
        self.is_on_ground = True

    def move_left_keys(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a] and not self.is_walking_right:
            if not self.is_walking_left:
                self.velocity.x = -1 * self.ground_type.get_horizontal_velocity_modifier() 
                self.is_walking_left = True
                self.is_walking_right = False
                self.update_image_direction()
                print(f"Rabbit velocity: {self.velocity}")
        else:
            if self.is_walking_left:
                self.velocity.x = 0 
                self.is_walking_left = False
                self.update_image_direction()

    def move_right_keys(self, keys):
        if keys[pygame.K_RIGHT] or keys[pygame.K_d] and self.is_on_ground and not self.is_walking_left:
            if not self.is_walking_right:
                self.velocity.x = 1 * self.ground_type.get_horizontal_velocity_modifier()
                self.is_walking_right = True
                self.is_walking_left = False
                self.update_image_direction()
                print(f"Rabbit velocity: {self.velocity}")
        else:
            if self.is_walking_right:
                self.velocity.x = 0
                self.is_walking_right = False
                self.update_image_direction()

    def hit(self, damage):
        self.current_health -= damage
        if self.current_health <= 0:
            pass

    def shoot(self):
        pass

    def update(self, keys):
        self.rect.topleft = self.position
        self.check_collision()
        self.check_collision_horizontal()
        self.jump(keys)
        self.move_left_keys(keys)  
        self.move_right_keys(keys)
        self.move()
        if self.position.y > 750: # Fall off to lava
            self.position.y = 600
            self.position.x = 925
            self.rect.topleft = self.position
            self.velocity.y = 0
            self.velocity.x = 0
        if self.position.y <= 0: # Hit ceiling
            self.position.y += 64
            

# Chocolate is a sprite, when the rabbit collides with it, the player wins.
class Chocolate(pygame.sprite.Sprite):
    def __init__(self, x, y, image, width, height):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.position = Vector2(x, y)
        self.width = width
        self.height = height

    def update(self):
        self.rect.topleft = self.position


def main():
    pygame.init()
    pygame.display.set_caption("Platformer Game Test")

    width, height = 1184, 800
    screen = pygame.display.set_mode((width, height))
    level_image = pygame.image.load("_composite.png")

    original_image = pygame.image.load("rabbit.png")
    resized_image = pygame.transform.scale(original_image, (32, 32))

    chocolate_image = pygame.image.load("chocolate.png")
    resized_chocolate_image = pygame.transform.scale(chocolate_image, (32, 32))

    rabbit = Rabbit(925, 600, resized_image, 100, 100)
    chocolate = Chocolate(164, 195, resized_chocolate_image, 100, 100)
    sprites = pygame.sprite.Group(rabbit, chocolate)

    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        rabbit.update(keys)

        # Draw the level
        screen.blit(level_image, (0, 0))

        sprites.draw(screen)
        pygame.display.flip()
        screen.fill((0, 0, 0))  

        clock.tick(80) 

    pygame.quit()

if __name__ == "__main__":
    main()