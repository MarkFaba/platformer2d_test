import csv
import ctypes
import random
import pygame
from pygame.math import Vector2
import pygame_gui

TILE_SIZE = 32

# Disable windows app scaling 
ctypes.windll.user32.SetProcessDPIAware()

# Define colors
BLACK = pygame.color.Color("#000000")  
GREEN = pygame.color.Color("#00FF00")
BLUE = pygame.color.Color("#0000FF")
CRYSTAL_BLUE = pygame.color.Color("#00FFFF")
REDSTONE = pygame.color.Color("#FF0044")
DIRT = pygame.color.Color("#472522")

class UnWalkableTile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.velocity = Vector2(0, 0)


# Circle, red small bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, velocity, obstacle_group, rabbit, obstacle_group_2=None, obstacle_group_3=None, obstacle_group_4=None, obstacle_group_5=None):
        super().__init__()
        self.image = pygame.Surface([5, 5])
        self.image.fill(REDSTONE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.position = Vector2(x, y)
        self.velocity = velocity
        self.velocity_with_reflected_y = self.velocity.y * -1
        self.obstacle_group = obstacle_group
        self.rabbit = rabbit
        self.obstacle_group_2 = obstacle_group_2
        self.obstacle_group_3 = obstacle_group_3
        self.obstacle_group_4 = obstacle_group_4
        self.obstacle_group_5 = obstacle_group_5

    def update(self):
        # self.rect.move_ip(self.velocity)
        self.rect.center = self.position
        self.position += self.velocity
        if self.rect.right < 0 or self.rect.left > 1184 or self.rect.bottom < 0 or self.rect.top > 800:
            self.kill()
        if pygame.sprite.spritecollideany(self, self.obstacle_group):
            self.kill()
        if self.obstacle_group_2:
            if pygame.sprite.spritecollideany(self, self.obstacle_group_2): # Mirror, unused
                self.velocity.y = self.velocity_with_reflected_y
        if self.obstacle_group_3:
            if pygame.sprite.spritecollideany(self, self.obstacle_group_3):
                self.kill()
        if self.obstacle_group_4:
            if pygame.sprite.spritecollideany(self, self.obstacle_group_4): # Redstone
                self.kill()
        if self.obstacle_group_5:
            if pygame.sprite.spritecollideany(self, self.obstacle_group_5): # Ice
                self.kill()
        if pygame.sprite.collide_rect(self, self.rabbit):
            self.rabbit.hit(20)
            if self.rabbit.direction == "left":
                self.rabbit.velocity_glide_r += 25
                self.rabbit.velocity.y += -6
            elif self.rabbit.direction == "right":
                self.rabbit.velocity_glide_l += 25
                self.rabbit.velocity.y += -6
            print(self.rabbit.current_health)
            print("hit")
            self.kill()

class MovablePlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, velocity, image, start_x, end_x, start_y, end_y, marker='1'):
        super().__init__()
        self.position = Vector2(x, y)
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.marker = marker
        self.velocity = Vector2(velocity)

        self.start_point_x = start_x
        self.end_point_x = end_x

        self.start_point_y = start_y
        self.end_point_y = end_y

    def update(self):
        self.position += self.velocity
        self.rect.topleft = self.position

        if self.rect.right > self.end_point_x or self.rect.left < self.start_point_x:
            self.velocity.x *= -1

        if self.rect.bottom > self.end_point_y or self.rect.top < self.start_point_y:
            self.velocity.y *= -1


# Map collusion information, level image, and rabbit spawn position
class Level:
    def __init__(self, csv_file, level_image_file, rabbitspawn_pos, movable_platforms):
        self.csv_file = csv_file
        self.level_image_file = pygame.image.load(level_image_file)
        self.rabbitspawn_pos = rabbitspawn_pos
        self.movable_platforms = movable_platforms
        self.unwalkable_tile_group = self.load_unwalkable_tiles() # Dirt
        self.unwalkable_tile_group_2 = self.load_unwalkable_tiles(marker='2')
        self.unwalkable_tile_group_3 = self.load_unwalkable_tiles(marker='3')
        self.unwalkable_tile_group_4 = self.load_unwalkable_tiles(marker='4') # Redstone
        self.unwalkable_tile_group_5 = self.load_unwalkable_tiles(marker='5') # Ice
        
    def load_unwalkable_tiles(self, marker='1'):
        unwalkable_tiles = []

        with open(self.csv_file, 'r') as f:
            reader = csv.reader(f)
            unwalkable_tiles = list(reader)

        unwalkable_tile_group = pygame.sprite.Group()
        for row in range(len(unwalkable_tiles)):
            for col in range(len(unwalkable_tiles[row])):
                if unwalkable_tiles[row][col] == marker:
                    unwalkable_tile = UnWalkableTile(col * TILE_SIZE, row * TILE_SIZE)
                    unwalkable_tile_group.add(unwalkable_tile)

        if self.movable_platforms:
            for movable_platform in self.movable_platforms:
                if movable_platform.marker == marker:
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
        self.max_velocity = 30 # More than 30 will cause the rabbit to fall through the ground sometimes

    def get_gravity(self):
        return self.gravity
    
    def get_max_velocity(self):
        return self.max_velocity


# Ground class
class Dirt:
    def __init__(self):
        self.horizontal_velocity_modifier = 3.0
        self.normal_force = 1000
        self.glide_decay = 10.0

    def get_horizontal_velocity_modifier(self):
        return self.horizontal_velocity_modifier


class SoulSand:
    def __init__(self):
        self.horizontal_velocity_modifier = 1.5
        self.normal_force = 1000
        self.glide_decay = 10.0

    def get_horizontal_velocity_modifier(self):
        return self.horizontal_velocity_modifier


class Ice:
    def __init__(self):
        self.horizontal_velocity_modifier = 9.0
        self.glide_force = 15.0
        self.normal_force = 1000
        self.glide_decay = 1.0

    def get_horizontal_velocity_modifier(self):
        return self.horizontal_velocity_modifier

class Mirror:
    def __init__(self):
        self.horizontal_velocity_modifier = 5.0
        self.glide_force = 10.0
        self.normal_force = 1000
        self.glide_decay = 2.0

    def get_horizontal_velocity_modifier(self):
        return self.horizontal_velocity_modifier


class Rabbit(pygame.sprite.Sprite):
    def __init__(self, x, y, health_capacity, current_health, level):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load("rabbit.png"), (32, 32))
        self.original_image = self.image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.position = Vector2(x, y)
        self.position_center = Vector2(x + self.rect.width / 2, y + self.rect.height / 2)
        self.velocity = Vector2(0, 0) 
        self.velocitylr = Vector2(0, 0)
        self.velocityplatform = Vector2(0, 0)
        self.velocity_glide_l = 0
        self.velocity_glide_r = 0
        self.health_capacity = health_capacity
        self.current_health = current_health
        self.is_walking_left = False
        self.is_walking_right = False
        self.direction = "right"
        self.is_on_ground = False
        self.ground_type = Dirt()
        self.air_type = Air()
        self.level = level
        self.unwalkable_tile_group = level.unwalkable_tile_group
        self.unwalkable_tile_group_redstone = level.unwalkable_tile_group_4
        self.unwalkable_tile_group_ice = level.unwalkable_tile_group_5
        self.collected_chocolates = 0
        self.mission_completed = False 
        self.is_on_platform = False
        self.current_time = 0
        self.current_time_switchable = 0
        self.current_time_switch = True

    def update_image_direction(self):
        if self.is_walking_left:
            self.image = pygame.transform.flip(self.original_image, True, False)
            self.direction = "left"
        elif self.is_walking_right:
            self.image = self.original_image
            self.direction = "right"

    def check_collision(self):
        current_position = self.position
        # Check collision with unwalkable tiles
        hit_list = pygame.sprite.spritecollide(self, self.unwalkable_tile_group, False)
        hit_list_ice = pygame.sprite.spritecollide(self, self.unwalkable_tile_group_ice, False)
        hit_list_redstone = pygame.sprite.spritecollide(self, self.unwalkable_tile_group_redstone, False)
        hit_list_all = hit_list + hit_list_ice + hit_list_redstone
        if len(hit_list_all) > 0:
            if current_position.y <= hit_list_all[0].rect.top: # rabbit head above or equal height to tile
                self.rect.bottom = hit_list_all[0].rect.top # a feature, not a bug
                self.position.y = self.rect.y
                # if hit_list_all[0] is in hit_list, then it is a dirt tile, if hit_list_all[0] is in hit_list_ice, then it is an ice tile
                if hit_list_all[0] in hit_list:
                    self.ground_type = Dirt()
                # Take damage if rabbit is on redstone
                if hit_list_all[0] in hit_list_redstone:
                    self.ground_type = Dirt()
                    self.hit(1)
                elif hit_list_all[0] in hit_list_ice:
                    self.ground_type = Ice()
                self.land()

                # Calculate effects when rabbit is on platform
                if isinstance(hit_list_all[0], MovablePlatform):
                    self.is_on_platform = True
                else:
                    self.is_on_platform = False

                if self.is_on_platform:
                    self.velocityplatform = hit_list_all[0].velocity.copy()
                else:
                    self.velocityplatform = Vector2(0, 0)
                return 
            
            elif current_position.y > hit_list_all[0].rect.top: # rabbit head below tile
                self.rect.top = hit_list_all[0].rect.bottom
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
        hit_list_ice = pygame.sprite.spritecollide(self, self.unwalkable_tile_group_ice, False)
        hit_list_redstone = pygame.sprite.spritecollide(self, self.unwalkable_tile_group_redstone, False)
        hit_list_all = hit_list + hit_list_ice + hit_list_redstone
        if len(hit_list_all) > 0:
            if current_position.x <= hit_list_all[0].rect.left:
                self.velocity.x = 0
                self.velocitylr.x = 0
                self.velocityplatform.x = 0
                if hit_list_all[0] in hit_list_redstone:
                    self.hit(1)
                if not isinstance(hit_list_all[0], MovablePlatform):
                    self.rect.right = hit_list_all[0].rect.left
                    self.position.x = self.rect.x
                return
            elif current_position.x > hit_list_all[0].rect.left:
                self.velocity.x = 0
                self.velocitylr.x = 0
                self.velocityplatform.x = 0
                if not isinstance(hit_list_all[0], MovablePlatform):
                    self.rect.left = hit_list_all[0].rect.right
                    self.position.x = self.rect.x
                return

    def move(self):
        # Decay glide velocity
        if self.velocity_glide_l > 0:
            self.velocity_glide_l -= self.ground_type.glide_decay
        self.velocity_glide_l = max(0, self.velocity_glide_l)
        if self.velocity_glide_r > 0:
            self.velocity_glide_r -= self.ground_type.glide_decay
        self.velocity_glide_r = max(0, self.velocity_glide_r)
        # Update position based on velocity on that direction
        self.position += self.velocity + self.velocitylr + self.velocityplatform - Vector2(self.velocity_glide_l, 0) + Vector2(self.velocity_glide_r, 0)
        # Update velocity based on air type, only vertical velocity is affected
        if not self.is_on_ground:
            self.velocity.y += self.air_type.get_gravity() # Current value: 1
            self.velocity.y = min(self.velocity.y, self.air_type.get_max_velocity()) 

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
        # if self.velocity.y > 30:
        #     self.hit(self.velocity.y - 30)
        self.velocity.y = 0
        self.is_on_ground = True

    def move_left_keys(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a] and not self.is_walking_right:
            if not self.is_walking_left:
                # Bug: self.ground_type is not immediately updated when rabbit switches tiles
                self.velocitylr.x = -1 * self.ground_type.get_horizontal_velocity_modifier() 
                self.is_walking_left = True
                self.is_walking_right = False
                self.update_image_direction()
        else:
            if self.is_walking_left:
                self.velocitylr.x = 0
                # Glide effect if on ice
                if isinstance(self.ground_type, Ice):
                    self.velocity_glide_l = self.ground_type.glide_force
                self.is_walking_left = False
                self.update_image_direction()

    def move_right_keys(self, keys):
        if keys[pygame.K_RIGHT] or keys[pygame.K_d] and self.is_on_ground and not self.is_walking_left:
            if not self.is_walking_right:
                self.velocitylr.x = 1 * self.ground_type.get_horizontal_velocity_modifier()
                self.is_walking_right = True
                self.is_walking_left = False
                self.update_image_direction()
        else:
            if self.is_walking_right:
                self.velocitylr.x = 0
                if isinstance(self.ground_type, Ice):
                    self.velocity_glide_r = self.ground_type.glide_force
                self.is_walking_right = False
                self.update_image_direction()

    def hit(self, damage):
        self.current_health -= damage
        # print(f"Rabbit hit for {damage} damge! Current health: {self.current_health}")
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
        self.velocity_glide_l = 0
        self.velocity_glide_r = 0
        self.current_health = self.health_capacity
        print("Rabbit respawned!")

    def collected_3_chocolates(self):
        if self.collected_chocolates == 3:
            print("All chocolates collected!")
            self.collected_chocolates = 0
            self.mission_completed = True
            return True
        else:
            return False

    def update(self, keys):
        self.rect.topleft = self.position
        self.position_center = self.rect.center
        self.check_collision()
        self.check_collision_horizontal()
        self.jump(keys)
        self.move_left_keys(keys)  
        self.move_right_keys(keys)
        self.move()
        if self.position.y > 1600: # Fall off the map
            self.hit(1000)
        self.collected_3_chocolates()
        self.current_time = pygame.time.get_ticks()
        if self.current_time_switch:
            self.current_time_switchable = pygame.time.get_ticks()



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

    width, height = 1184, 832
    screen = pygame.display.set_mode((width, height))

    # Level 1
    # ====================================================================================================
    platform_image = pygame.surface.Surface((300, 32))
    platform_image.fill(DIRT)
    platform = MovablePlatform(575, height - (32*4+16), Vector2(2.5, 0), platform_image, 425, 900, 0, 800)

    level = Level('level1.csv', 'level1.png', Vector2(955, 600), [platform])

    rabbit = Rabbit(*level.rabbitspawn_pos, 100, 100, level)

    chocolate = Chocolate(32 * 4, 259, 100, 100, rabbit)
    chocolate2 = Chocolate(32 * 4, 580, 100, 100, rabbit)
    chocolate3 = Chocolate(32 * 16, 515, 100, 100, rabbit)

    sprites = pygame.sprite.Group(rabbit, platform)
    chocolates = pygame.sprite.Group(chocolate, chocolate2, chocolate3)
    bullets = pygame.sprite.Group()

    # Level 2
    # ====================================================================================================
    level2 = Level('level2.csv', 'level2.png', Vector2(600, 600), [])
    rabbit2 = Rabbit(*level2.rabbitspawn_pos, 130, 130, level2)

    chocolate2_1 = Chocolate(32 * 18, 32*6, 100, 100, rabbit2)
    chocolate2_2 = Chocolate(32 * 7, 32*7, 100, 100, rabbit2)
    chocolate2_3 = Chocolate(32 * 29, 32*7, 100, 100, rabbit2)

    sprites2 = pygame.sprite.Group(rabbit2)
    chocolates2 = pygame.sprite.Group(chocolate2_1, chocolate2_2, chocolate2_3)
    bullets2 = pygame.sprite.Group()
    bullets2_1 = pygame.sprite.Group()
    bullets2_2 = pygame.sprite.Group()

    # Level 3
    # ====================================================================================================
    platform_image = pygame.surface.Surface((32*5, 32))
    platform_image.fill(DIRT)
    platform1 = MovablePlatform(600, 32*8+16, Vector2(2.5, 0), platform_image, 32*5, width - 32*5, 0, 800)

    platform_image = pygame.surface.Surface((32*5, 32))
    platform_image.fill(REDSTONE)
    platform2 = MovablePlatform(400, 32*10+16, Vector2(-3.5, 0), platform_image, 32*5, width - 32*5, 0, 800, marker="4")

    platform_image = pygame.surface.Surface((32*5, 32))
    platform_image.fill(DIRT)
    platform3 = MovablePlatform(400, 32*15+16, Vector2(2.5, 0), platform_image, 32*5, width - 32*5, 0, 800, marker="1")

    level3 = Level('level3.csv', 'level3.png', Vector2(600, 700), [platform1, platform2, platform3])
    rabbit3 = Rabbit(*level3.rabbitspawn_pos, 160, 160, level3)

    sprites3 = pygame.sprite.Group(rabbit3, platform1, platform2, platform3)
    chocolates3 = pygame.sprite.Group()
    bullets3 = pygame.sprite.Group()
    bullets3_1 = pygame.sprite.Group()
    bullets3_2 = pygame.sprite.Group()

    # =====================================================================================================

    clock = pygame.time.Clock()
    last_bullet_time = None
    last_bullet_time2 = None
    last_bullet_time3 = None
    last_bullet_time4 = None
    last_bullet_time5 = None

    ui_manager = pygame_gui.UIManager((width, height), 'theme.json')
    rabbit_health_bar = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.Rect((0, height - 32), (width, 32)),ui_manager,
                                                            rabbit)
    current_mapid = 1
    total_maps = 3
    mapid_label = pygame_gui.elements.UILabel(pygame.Rect((460, 32), (250, 25)), 
                                              f"Map: {current_mapid}/{total_maps}", ui_manager)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        ui_manager.process_events(event)
        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        if current_mapid == 1:
            # Create new bullet every 1 second
            if last_bullet_time is None or now - last_bullet_time >= 1500:
                bullet1 = Bullet(35, 35, Vector2(random.random() * 100, random.random() * 100).normalize(), level.unwalkable_tile_group, rabbit)
                bullet2 = Bullet(width-35, 35, Vector2(random.random() * -100, random.random() * 100).normalize(), level.unwalkable_tile_group, rabbit)
                bullet3 = Bullet(width // 2, 35, Vector2(random.random() * 200 - 100, random.random() * 100).normalize(), level.unwalkable_tile_group, rabbit)
                bullets.add(bullet1, bullet2, bullet3)
                last_bullet_time = now

            rabbit.update(keys)
            chocolates.update()
            level.update()
            bullets.update()

            # Draw the level
            screen.blit(level.level_image_file, (0, 0))

            sprites.draw(screen)
            chocolates.draw(screen)
            bullets.draw(screen)
            if rabbit.mission_completed: # Duck tape: last rabbit
                current_mapid = 2
                sprites.empty()
                bullets.empty()

        if current_mapid == 2:

            if last_bullet_time is None or now - last_bullet_time >= 1500:
                random_normalized_vector = Vector2(random.random() * 100, random.random() * 100).normalize()
                random_normalized_vector2 = Vector2(random.random() * -100, random.random() * 100).normalize()
                bullet1 = Bullet(35, 35, random_normalized_vector, level2.unwalkable_tile_group, rabbit2, obstacle_group_5=level2.unwalkable_tile_group_5)
                bullet2 = Bullet(width-35, 35, random_normalized_vector2, level2.unwalkable_tile_group, rabbit2, obstacle_group_5=level2.unwalkable_tile_group_5)
                
                bullets2.add(bullet1, bullet2)
                last_bullet_time = now

            if last_bullet_time2 is None or now - last_bullet_time2 >= 3000:
                bullet3 = Bullet(32*13-16, 35, Vector2(0, 100).normalize(), level2.unwalkable_tile_group, rabbit2, obstacle_group_5=level2.unwalkable_tile_group_5)
                bullet4 = Bullet(32*25-16, 35, Vector2(0, 100).normalize(), level2.unwalkable_tile_group, rabbit2, obstacle_group_5=level2.unwalkable_tile_group_5)
                bullet5 = Bullet(16, 32*10+16, Vector2(100, 0).normalize(), level2.unwalkable_tile_group, rabbit2, obstacle_group_5=level2.unwalkable_tile_group_5)
                bullet6 = Bullet(16, 32*14+16, Vector2(100, 0).normalize(), level2.unwalkable_tile_group, rabbit2, obstacle_group_5=level2.unwalkable_tile_group_5)

                bullets2_1.add(bullet3, bullet4, bullet5, bullet6)
                last_bullet_time2 = now

            rabbit_health_bar.set_sprite_to_monitor(rabbit2)
            mapid_label.set_text(f"Map: {current_mapid}/{total_maps}")
            rabbit2.update(keys)
            level2.update()
            bullets2.update()
            bullets2_1.update()
            chocolates2.update()

            screen.blit(level2.level_image_file, (0, 0))
            sprites2.draw(screen)
            chocolates2.draw(screen)
            bullets2.draw(screen)
            bullets2_1.draw(screen)
            if rabbit2.mission_completed:
                current_mapid = 3
                sprites2.empty()
                bullets2.empty()
                bullets2_1.empty()

        if current_mapid == 3:
    
            if last_bullet_time3 is None or now - last_bullet_time3 >= 3000:
                bullet1 = Bullet(width // 2, 16, Vector2(random.random() * 200 - 100, random.random() * 100).normalize(), level3.unwalkable_tile_group, rabbit3, obstacle_group_5=level3.unwalkable_tile_group_5)
                bullet2 = Bullet(width // 2, 16, Vector2(random.random() * 200 - 100, random.random() * 100).normalize(), level3.unwalkable_tile_group, rabbit3, obstacle_group_5=level3.unwalkable_tile_group_5)
                bullet3 = Bullet(32*10-16, 16, Vector2(0, 100).normalize(), level3.unwalkable_tile_group, rabbit3, obstacle_group_5=level3.unwalkable_tile_group_5)
                bullet4 = Bullet(32*28-16, 16, Vector2(0, 100).normalize(), level3.unwalkable_tile_group, rabbit3, obstacle_group_5=level3.unwalkable_tile_group_5)
                bullet5 = Bullet(16, 32*6+16, Vector2(100, 0).normalize(), level3.unwalkable_tile_group, rabbit3, obstacle_group_5=level3.unwalkable_tile_group_5)
                bullet6 = Bullet(16, 32*12+16, Vector2(100, 0).normalize(), level3.unwalkable_tile_group, rabbit3, obstacle_group_5=level3.unwalkable_tile_group_5)
                bullets3.add(bullet1, bullet2, bullet3, bullet4, bullet5, bullet6)
                last_bullet_time3 = now

            rabbit_health_bar.set_sprite_to_monitor(rabbit3)
            mapid_label.set_text(f"Map: {current_mapid}/{total_maps}")
            rabbit3.update(keys)
            level3.update()
            bullets3.update()
            chocolates3.update()

            screen.blit(level3.level_image_file, (0, 0))
            sprites3.draw(screen)
            chocolates3.draw(screen)
            bullets3.draw(screen)
            if rabbit3.mission_completed:
                current_mapid = 4
                sprites3.empty()
                bullets3.empty()

        ui_manager.update(1/60)
        ui_manager.draw_ui(screen)
        pygame.display.flip()
        screen.fill((0, 0, 0))  
        clock.tick(80) 

    pygame.quit()

if __name__ == "__main__":
    main()