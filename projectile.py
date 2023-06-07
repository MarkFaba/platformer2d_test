import pygame
from pygame.math import Vector2


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, image, velocity, magnitude, target, obstacle_group):
        super().__init__()
        # self.image = pygame.Surface([5, 5])
        # self.image.fill(REDSTONE)
        # self.image = pygame.image.load("assets/missile.png")
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.position = Vector2(x, y)
        # self.velocity = Vector2(50, 50)
        self.velocity = velocity.normalize()
        self.magnitude = magnitude
        self.obstacle_group = obstacle_group
        self.target = target

    def update(self):
        # self.rect.move_ip(self.velocity)
        self.rect.center = self.position
        self.position += self.velocity * self.magnitude
        if self.rect.right < 0 or self.rect.left > 1184 or self.rect.bottom < 0 or self.rect.top > 800:
            self.kill()
        if pygame.sprite.spritecollideany(self, self.obstacle_group):
            self.kill()
        if pygame.sprite.collide_rect(self, self.target):
            self.target.hit(20)
            print(self.target.current_health)
            print("hit")
            self.kill()

    def homing(self):
        self.velocity = self.target.position_center.normalize()

    def accelerate(self, speed):
        self.magnitude += speed