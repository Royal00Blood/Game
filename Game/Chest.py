import pygame
from settings import *

# Класс сундука
class Chest:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_open = False
        self.contains_treasure = True
        self.requires_key = True

    def try_open(self, player):
        if self.is_open:
            return False, "Сундук уже открыт!"

        if self.requires_key and player.keys <= 0:
            return False, "Нужен ключ чтобы открыть сундук!"

        self.is_open = True
        if self.requires_key:
            player.keys -= 1

        if self.contains_treasure:
            player.score += 500
            player.has_treasure = True
            return True, "Вы открыли сундук и нашли главное сокровище! +500 очков"
        else:
            player.score += 100
            return True, "Вы открыли сундук. +100 очков"

    def draw(self, screen, offset_x, offset_y):
        chest_x = offset_x + self.x * TILE_SIZE
        chest_y = offset_y + self.y * TILE_SIZE

        if self.is_open:
            pygame.draw.rect(screen, DARK_BROWN,
                             (chest_x, chest_y, CHEST_SIZE, CHEST_SIZE))
            pygame.draw.rect(screen, (70, 35, 0),
                             (chest_x + 4, chest_y + 4,
                              CHEST_SIZE - 8, CHEST_SIZE - 8))
            pygame.draw.rect(screen, GOLD,
                             (chest_x + 8, chest_y + 8,
                              CHEST_SIZE - 16, CHEST_SIZE - 16))
        else:
            pygame.draw.rect(screen, ORANGE,
                             (chest_x, chest_y, CHEST_SIZE, CHEST_SIZE))
            pygame.draw.rect(screen, SILVER,
                             (chest_x, chest_y, CHEST_SIZE, 4))
            pygame.draw.rect(screen, SILVER,
                             (chest_x, chest_y + CHEST_SIZE - 4, CHEST_SIZE, 4))
            pygame.draw.rect(screen, SILVER,
                             (chest_x, chest_y, 4, CHEST_SIZE))
            pygame.draw.rect(screen, SILVER,
                             (chest_x + CHEST_SIZE - 4, chest_y, 4, CHEST_SIZE))
            pygame.draw.rect(screen, YELLOW,
                             (chest_x + CHEST_SIZE // 2 - 6,
                              chest_y + CHEST_SIZE // 2 - 6,
                              12, 12))