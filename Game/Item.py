import pygame
from settings import *
# Класс предмета
class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.type = item_type

    def draw(self, screen, offset_x, offset_y):
        item_x = offset_x + self.x * TILE_SIZE + (TILE_SIZE - ITEM_SIZE) // 2
        item_y = offset_y + self.y * TILE_SIZE + (TILE_SIZE - ITEM_SIZE) // 2

        if self.type == "health":
            pygame.draw.rect(screen, RED,
                             (item_x, item_y, ITEM_SIZE, ITEM_SIZE))
            pygame.draw.rect(screen, WHITE,
                             (item_x, item_y, ITEM_SIZE, ITEM_SIZE), 2)
            pygame.draw.line(screen, WHITE,
                             (item_x + 4, item_y + ITEM_SIZE // 2),
                             (item_x + ITEM_SIZE - 4, item_y + ITEM_SIZE // 2), 3)
            pygame.draw.line(screen, WHITE,
                             (item_x + ITEM_SIZE // 2, item_y + 4),
                             (item_x + ITEM_SIZE // 2, item_y + ITEM_SIZE - 4), 3)
        elif self.type == "key":
            pygame.draw.rect(screen, YELLOW,
                             (item_x, item_y, ITEM_SIZE, ITEM_SIZE))
            for i in range(3):
                height = ITEM_SIZE // 3
                pygame.draw.rect(screen, ORANGE,
                                 (item_x + ITEM_SIZE // 2 - 1,
                                  item_y + i * height,
                                  2, height))
        elif self.type == "treasure":
            pygame.draw.rect(screen, GOLD,
                             (item_x, item_y, ITEM_SIZE, ITEM_SIZE))
            points = [
                (item_x + ITEM_SIZE // 2, item_y + 2),
                (item_x + ITEM_SIZE - 2, item_y + ITEM_SIZE // 2),
                (item_x + ITEM_SIZE // 2, item_y + ITEM_SIZE - 2),
                (item_x + 2, item_y + ITEM_SIZE // 2)
            ]
            pygame.draw.polygon(screen, YELLOW, points)
        elif self.type == "potion":
            pygame.draw.rect(screen, PURPLE,
                             (item_x, item_y, ITEM_SIZE, ITEM_SIZE))
            neck_width = ITEM_SIZE // 2
            pygame.draw.rect(screen, PURPLE,
                             (item_x + (ITEM_SIZE - neck_width) // 2,
                              item_y - 4,
                              neck_width, 4))
