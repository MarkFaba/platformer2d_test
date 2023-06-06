import pygame
import sys

# Color
RED = (255, 0, 0)

# Window dimensions
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, velocity):
        super().__init__()
        self.image = pygame.Surface([5, 5])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.velocity = velocity

    def update(self):
        self.rect.move_ip(self.velocity)
        if self.rect.right < 0 or self.rect.left > WINDOW_WIDTH or self.rect.bottom < 0 or self.rect.top > WINDOW_HEIGHT:
            self.kill()

# Initialize pygame and create a window
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# Create a group for the bullets
bullets = pygame.sprite.Group()

# Set the bullet velocity
bullet_velocity = [2, 2]

# Set up the game clock
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # If spacebar is pressed, create a new bullet
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullet = Bullet(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, bullet_velocity)
                bullets.add(bullet)

    # Update and draw all bullets
    bullets.update()
    screen.fill((0, 0, 0))  # Clear the screen with black
    bullets.draw(screen)  # Draw all bullets

    # Flip the display
    pygame.display.flip()

    # Cap the framerate
    clock.tick(60)
