import pygame
from  settings import *

class Wall:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, screen, offset_x, offset_y):
        wall_x = offset_x + self.x * TILE_SIZE
        wall_y = offset_y + self.y * TILE_SIZE

        pygame.draw.rect(screen, BROWN,
                         (wall_x, wall_y, TILE_SIZE, TILE_SIZE))

        for i in range(0, TILE_SIZE, 4):
            for j in range(0, TILE_SIZE, 4):
                if (i // 4 + j // 4) % 2 == 0:
                    brick_color = (120, 60, 0)
                else:
                    brick_color = (150, 75, 0)

                pygame.draw.rect(screen, brick_color,
                                 (wall_x + i, wall_y + j, 4, 4))

        for i in range(0, TILE_SIZE, 8):
            for j in range(0, TILE_SIZE, 8):
                pygame.draw.rect(screen, (80, 40, 0),
                                 (wall_x + i, wall_y + j, 8, 8), 1)