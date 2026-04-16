import pygame
from settings import *
# Класс игрока
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 100
        self.max_health = 100
        self.keys = 0
        self.score = 0
        self.has_treasure = False
        self.is_in_combat = False
        self.direction = "down"

    def move(self, dx, dy, walls):
        if self.is_in_combat:
            return

        new_x = self.x + dx
        new_y = self.y + dy

        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
        elif dy > 0:
            self.direction = "down"
        elif dy < 0:
            self.direction = "up"

        if not any(wall.x == new_x and wall.y == new_y for wall in walls):
            self.x = new_x
            self.y = new_y

    def draw(self, screen, offset_x, offset_y):
        player_x = offset_x + self.x * TILE_SIZE
        player_y = offset_y + self.y * TILE_SIZE

        pygame.draw.rect(screen, BLUE,
                         (player_x, player_y, PLAYER_SIZE, PLAYER_SIZE))

        head_radius = PLAYER_SIZE // 3
        pygame.draw.circle(screen, BLUE,
                           (player_x + PLAYER_SIZE // 2, player_y - head_radius // 2),
                           head_radius)

        eye_size = PLAYER_SIZE // 8
        if self.direction == "right":
            pygame.draw.circle(screen, WHITE,
                               (player_x + 3 * PLAYER_SIZE // 4, player_y + PLAYER_SIZE // 3),
                               eye_size)
        elif self.direction == "left":
            pygame.draw.circle(screen, WHITE,
                               (player_x + PLAYER_SIZE // 4, player_y + PLAYER_SIZE // 3),
                               eye_size)
        else:
            pygame.draw.circle(screen, WHITE,
                               (player_x + PLAYER_SIZE // 3, player_y + PLAYER_SIZE // 3),
                               eye_size)
            pygame.draw.circle(screen, WHITE,
                               (player_x + 2 * PLAYER_SIZE // 3, player_y + PLAYER_SIZE // 3),
                               eye_size)

        if self.is_in_combat:
            if self.direction == "right":
                sword_start = (player_x + PLAYER_SIZE, player_y + PLAYER_SIZE // 2)
                sword_end = (player_x + PLAYER_SIZE + 15, player_y + PLAYER_SIZE // 2)
            elif self.direction == "left":
                sword_start = (player_x, player_y + PLAYER_SIZE // 2)
                sword_end = (player_x - 15, player_y + PLAYER_SIZE // 2)
            elif self.direction == "up":
                sword_start = (player_x + PLAYER_SIZE // 2, player_y)
                sword_end = (player_x + PLAYER_SIZE // 2, player_y - 15)
            else:
                sword_start = (player_x + PLAYER_SIZE // 2, player_y + PLAYER_SIZE)
                sword_end = (player_x + PLAYER_SIZE // 2, player_y + PLAYER_SIZE + 15)

            pygame.draw.line(screen, SILVER, sword_start, sword_end, 3)
            pygame.draw.circle(screen, BROWN, sword_start, 4)

        health_width = 60
        health_height = 8
        health_x = player_x - (health_width - PLAYER_SIZE) // 2
        health_y = player_y - 15

        pygame.draw.rect(screen, RED,
                         (health_x, health_y, health_width, health_height))

        current_health_width = (self.health / self.max_health) * health_width
        pygame.draw.rect(screen, GREEN,
                         (health_x, health_y, current_health_width, health_height))

        pygame.draw.rect(screen, WHITE,
                         (health_x, health_y, health_width, health_height), 1)