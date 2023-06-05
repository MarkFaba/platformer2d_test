import pygame

# Initialize Pygame
pygame.init()

# Set the dimensions of the window
window_width = 800
window_height = 600

# Create the window
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Movable Platform Example")

# Define colors
WHITE = (255, 255, 255)

# Define the MovablePlatform class
class MovablePlatform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Load the platform image
        self.image = pygame.Surface((100, 20))
        self.image.fill(WHITE)

        # Set the position of the platform
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Set the platform's movement speed
        self.speed_x = 5

    def update(self):
        # Move the platform horizontally
        self.rect.x += self.speed_x

        # Reverse direction if the platform reaches the window's edges
        if self.rect.right > window_width or self.rect.left < 0:
            self.speed_x *= -1

# Create a group to hold the platforms
all_sprites = pygame.sprite.Group()

# Create a movable platform object
platform = MovablePlatform(300, 400)
all_sprites.add(platform)

# Run the game loop
running = True
clock = pygame.time.Clock()
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update the sprites
    all_sprites.update()

    # Clear the window
    window.fill((0, 0, 0))

    # Draw the sprites
    all_sprites.draw(window)

    # Update the display
    pygame.display.flip()

    # Set the frame rate
    clock.tick(60)

# Quit the game
pygame.quit()
