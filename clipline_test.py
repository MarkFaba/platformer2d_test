import pygame
from pygame.locals import *

def main():
    pygame.init()

    # Set up some constants
    WIDTH, HEIGHT = 640, 480
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    RECT_DIMENSIONS = (50, 50, 200, 200)
    LINE_START, LINE_END = (20, 20), (300, 300)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Create a rect object
    rect = pygame.Rect(RECT_DIMENSIONS)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        screen.fill(BLACK)
        pygame.draw.rect(screen, RED, rect, 2)
        pygame.draw.line(screen, GREEN, LINE_START, LINE_END, 2)

        clipped_line = rect.clipline(LINE_START, LINE_END)

        if clipped_line:
            # If clipped_line is not an empty tuple then the line
            # collides/overlaps with the rect. The returned value contains
            # the endpoints of the clipped line.
            start, end = clipped_line
            pygame.draw.line(screen, RED, start, end, 2)
        else:
            print("No clipping. The line is fully outside the rect.")

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
