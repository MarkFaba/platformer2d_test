import csv
import random
import pygame
from pygame.math import Vector2
import pygame_gui

TILE_SIZE = 32
# Define colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
REDSTONE = (255, 0, 0)
DIRT = (139, 69, 19)

class UnWalkableTile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.velocity = Vector2(0, 0)


# Circle, red small bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, velocity, obstacle_group, rabbit):
        super().__init__()
        self.image = pygame.Surface([5, 5])
        self.image.fill(REDSTONE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.position = Vector2(x, y)
        self.velocity = velocity
        self.obstacle_group = obstacle_group
        self.rabbit = rabbit

    def update(self):
        # self.rect.move_ip(self.velocity)
        self.rect.center = self.position
        self.position += self.velocity
        if self.rect.right < 0 or self.rect.left > 1184 or self.rect.bottom < 0 or self.rect.top > 800:
            self.kill()
        if pygame.sprite.spritecollideany(self, self.obstacle_group):
            self.kill()
        if pygame.sprite.collide_rect(self, self.rabbit):
            self.rabbit.hit(20)
            print(self.rabbit.current_health)
            print("hit")
            self.kill()

class MovablePlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, velocity, image, start_x, end_x, start_y, end_y):
        super().__init__()
        self.velocity = velocity
        self.position = Vector2(x, y)
        self.image = image
        self.velocity_reversed_x = -self.velocity.x
        self.velocity_reversed_y = -self.velocity.y

        # Set the position of the platform
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # Set the start and end points for the platform movement
        self.start_point = start_x
        self.end_point = end_x

        # Set the vertical movement boundaries
        self.start_y = start_y
        self.end_y = end_y

    def update(self):
        # Move the platform
        # self.rect.move_ip(self.velocity)
        self.rect.center = self.position
        self.position += self.velocity
        # Reverse direction if the platform reaches the start or end point horizontally
        if self.rect.right > self.end_point:
            self.velocity.x = self.velocity_reversed_x
        if self.rect.left < self.start_point:
            self.velocity.x = self.velocity_reversed_x * -1
        # Reverse direction if the platform reaches the start or end point vertically
        if self.rect.bottom > self.end_y:
            self.velocity.y *= self.velocity_reversed_y
        if self.rect.top < self.start_y:
            self.velocity.y = self.velocity_reversed_y * -1


# Map collusion information, level image, and rabbit spawn position
class Level:
    def __init__(self, csv_file, level_image_file, rabbitspawn_pos, movable_platforms):
        self.csv_file = csv_file
        self.level_image_file = pygame.image.load(level_image_file)
        self.rabbitspawn_pos = rabbitspawn_pos
        self.movable_platforms = movable_platforms
        self.unwalkable_tile_group = self.load_unwalkable_tiles()
        
    def load_unwalkable_tiles(self):
        unwalkable_tiles = []

        with open(self.csv_file, 'r') as f:
            reader = csv.reader(f)
            unwalkable_tiles = list(reader)

        unwalkable_tile_group = pygame.sprite.Group()
        for row in range(len(unwalkable_tiles)):
            for col in range(len(unwalkable_tiles[row])):
                if unwalkable_tiles[row][col] == '1':
                    unwalkable_tile = UnWalkableTile(col * TILE_SIZE, row * TILE_SIZE)
                    unwalkable_tile_group.add(unwalkable_tile)

        if self.movable_platforms:
            for movable_platform in self.movable_platforms:
                unwalkable_tile_group.add(movable_platform)
        return unwalkable_tile_group

    def update(self):
        if self.movable_platforms:
            for movable_platform in self.movable_platforms:
                movable_platform.update()

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
    def __init__(self, x, y, health_capacity, current_health, level):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load("rabbit.png"), (32, 32))
        self.original_image = self.image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.position = Vector2(x, y)
        self.velocity = Vector2(0, 0) 
        self.velocitylr = Vector2(0, 0)
        self.velocityplatform = Vector2(0, 0)
        self.health_capacity = health_capacity
        self.current_health = current_health
        self.is_walking_left = False
        self.is_walking_right = False
        self.is_on_ground = False
        self.ground_type = Dirt()
        self.air_type = Air()
        self.level = level
        self.unwalkable_tile_group = level.unwalkable_tile_group
        self.collected_chocolates = 0
        self.mission_completed = False 
        self.is_on_platform = False
        print(self.rect)

    def update_image_direction(self):
        if self.is_walking_left:
            self.image = pygame.transform.flip(self.original_image, True, False)
        elif self.is_walking_right:
            self.image = self.original_image

    def check_collision(self):
        current_position = self.position
        # Check collision with unwalkable tiles
        hit_list = pygame.sprite.spritecollide(self, self.unwalkable_tile_group, False)
        if len(hit_list) > 0:
            if current_position.y <= hit_list[0].rect.top: # rabbit head above or equal height to tile
                self.rect.bottom = hit_list[0].rect.top # a feature, not a bug
                self.position.y = self.rect.y
                self.land()

                # Calculate effects when rabbit is on platform
                if isinstance(hit_list[0], MovablePlatform):
                    self.is_on_platform = True
                else:
                    self.is_on_platform = False

                if self.is_on_platform:
                    self.velocityplatform = hit_list[0].velocity.copy()
                else:
                    self.velocityplatform = Vector2(0, 0)
                return 
            
            elif current_position.y > hit_list[0].rect.top: # rabbit head below tile
                self.rect.top = hit_list[0].rect.bottom
                if not self.is_on_platform:
                    self.position.y = self.rect.y
                self.velocity.y = 0
                return
        else:
            self.is_on_ground = False
            self.is_on_platform = False


    def check_collision_horizontal(self):
        current_position = self.position
        # Check collision with unwalkable tiles
        hit_list = pygame.sprite.spritecollide(self, self.unwalkable_tile_group, False)
        if len(hit_list) > 0:
            if current_position.x <= hit_list[0].rect.left:
                self.velocity.x = 0
                self.velocitylr.x = 0
                self.velocityplatform.x = 0
                if not isinstance(hit_list[0], MovablePlatform):
                    self.rect.right = hit_list[0].rect.left
                    self.position.x = self.rect.x
                return
            elif current_position.x > hit_list[0].rect.left:
                self.velocity.x = 0
                self.velocitylr.x = 0
                self.velocityplatform.x = 0
                if not isinstance(hit_list[0], MovablePlatform):
                    self.rect.left = hit_list[0].rect.right
                    self.position.x = self.rect.x
                return
        
    def move(self):
        # Update position based on velocity on that direction
        self.position += self.velocity + self.velocitylr + self.velocityplatform
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
            self.hit(self.velocity.y - 30)
        self.velocity.y = 0
        self.is_on_ground = True

    def move_left_keys(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a] and not self.is_walking_right:
            if not self.is_walking_left:
                self.velocitylr.x = -1 * self.ground_type.get_horizontal_velocity_modifier() 
                self.is_walking_left = True
                self.is_walking_right = False
                self.update_image_direction()
                print(f"Rabbit velocity: {self.velocity}")
        else:
            if self.is_walking_left:
                self.velocitylr.x = 0 
                self.is_walking_left = False
                self.update_image_direction()

    def move_right_keys(self, keys):
        if keys[pygame.K_RIGHT] or keys[pygame.K_d] and self.is_on_ground and not self.is_walking_left:
            if not self.is_walking_right:
                self.velocitylr.x = 1 * self.ground_type.get_horizontal_velocity_modifier()
                self.is_walking_right = True
                self.is_walking_left = False
                self.update_image_direction()
                print(f"Rabbit velocity: {self.velocity}")
        else:
            if self.is_walking_right:
                self.velocitylr.x = 0
                self.is_walking_right = False
                self.update_image_direction()

    def hit(self, damage):
        self.current_health -= damage
        print(f"Rabbit hit for {damage} damge! Current health: {self.current_health}")
        if self.current_health <= 0:
            self.respawn()

    def shoot(self):
        # if self.current_health > 0:
        #     if self.is_walking_left:
        #         self.level.add_projectile(Projectile(self.position, Vector2(-1, 0)))
        #     elif self.is_walking_right:
        #         self.level.add_projectile(Projectile(self.position, Vector2(1, 0)))
        #     else:
        #         self.level.add_projectile(Projectile(self.position, Vector2(0, 0)))
        # else:
        #     print("Rabbit is dead, cannot shoot!")
        pass

    def respawn(self):
        self.position = self.level.rabbitspawn_pos.copy()
        self.rect.topleft = self.position
        self.velocity.y = 0
        self.velocity.x = 0
        self.current_health = self.health_capacity
        print("Rabbit respawned!")

    def collected_3_chocolates(self):
        if self.collected_chocolates == 3:
            print("You win!")
            self.collected_chocolates = 0
            self.mission_completed = True
            return True
        else:
            return False

    def update(self, keys):
        self.rect.topleft = self.position
        self.check_collision()
        self.check_collision_horizontal()
        self.jump(keys)
        self.move_left_keys(keys)  
        self.move_right_keys(keys)
        self.move()
        if self.position.y > 750: # Fall off to lava
            self.hit(1000)
        if self.position.y <= 0: # Hit ceiling
            self.position.y += 64
        self.collected_3_chocolates()



class Chocolate(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, rabbit):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load("chocolate.png"), (32, 32))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.position = Vector2(x, y)
        self.width = width
        self.height = height
        self.rabbit = rabbit
        self.exists = True

    def collude_with_rabbit(self):
        return pygame.sprite.collide_rect(self, self.rabbit)

    def update(self):
        self.rect.topleft = self.position
        if self.collude_with_rabbit() and self.exists:
            self.kill()
            self.rabbit.collected_chocolates += 1
            print("Chocolate collected")
            self.exists = False


def main():
    pygame.init()
    pygame.display.set_caption("Platformer Game Test")

    width, height = 1184, 800
    screen = pygame.display.set_mode((width, height))

    platform_image = pygame.transform.scale(pygame.image.load('image/_48c65a6d-0913-4c9e-8821-3b9d00e4b4d3.jpg'), (300, 32))
    platform = MovablePlatform(575, 666, Vector2(2.5, 0), platform_image, 425, 900, 560, 650)

    level = Level('IntGrid_layer.csv', '_composite.png', Vector2(925, 600), [platform])

    rabbit = Rabbit(*level.rabbitspawn_pos, 100, 100, level)

    chocolate = Chocolate(164, 195, 100, 100, rabbit)
    chocolate2 = Chocolate(164, 580, 100, 100, rabbit)
    chocolate3 = Chocolate(548, 515, 100, 100, rabbit)

    sprites = pygame.sprite.Group(rabbit, chocolate, chocolate2, chocolate3, platform)
    bullets = pygame.sprite.Group()

    clock = pygame.time.Clock()
    last_bullet_time = None

    ui_manager = pygame_gui.UIManager((width, height), 'theme.json')
    rabbit_health_bar = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((50, 700), (200, 30)),ui_manager,
                                                            rabbit)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        ui_manager.process_events(event)

        now = pygame.time.get_ticks()
        # Create new bullet every 1 second
        if last_bullet_time is None or now - last_bullet_time >= 1500:
            random_normalized_vector = Vector2(random.random() * 100, random.random() * 100).normalize()
            random_normalized_vector2 = Vector2(random.random() * -100, random.random() * 100).normalize()
            random_normalized_vector3 = Vector2(random.random() * 100, random.random() * -100).normalize()
            random_normalized_vector4 = Vector2(random.random() * -100, random.random() * -100).normalize()
            bullet1 = Bullet(35, 35, random_normalized_vector, level.unwalkable_tile_group, rabbit)
            bullet2 = Bullet(width-35, 35, random_normalized_vector2, level.unwalkable_tile_group, rabbit)
            bullet3 = Bullet(35, height-35, random_normalized_vector3, level.unwalkable_tile_group, rabbit)
            bullet4 = Bullet(width-35, height-35, random_normalized_vector4, level.unwalkable_tile_group, rabbit)
            bullets.add(bullet1, bullet2, bullet3, bullet4)
            last_bullet_time = now

        keys = pygame.key.get_pressed()
        rabbit.update(keys)
        chocolate.update()
        chocolate2.update()
        chocolate3.update()
        level.update()
        bullets.update()

        ui_manager.update(1/60)
        # Draw the level
        screen.blit(level.level_image_file, (0, 0))

        sprites.draw(screen)
        bullets.draw(screen)
        ui_manager.draw_ui(screen)

        pygame.display.flip()
        screen.fill((0, 0, 0))  

        clock.tick(80) 

    pygame.quit()

if __name__ == "__main__":
    main()