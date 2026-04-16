import pygame
from settings import *
import pygame
import random
from moviepy.editor import VideoFileClip

# Класс врага
class Enemy:
    def __init__(self, x, y, enemy_type="goblin"):
        self.x = x
        self.y = y
        self.health = 50
        self.max_health = 50
        self.type = enemy_type
        self.is_in_combat = False
        self.qte_keys = []
        self.current_qte_index = 0
        self.qte_timer = 0
        self.qte_duration = 90
        self.direction = "down"
        self.generate_qte_sequence()

    def key_to_symbol(self, key):
        """Конвертируем код клавиши в символ - ТОЛЬКО СТРЕЛКИ"""
        key_symbols = {
            pygame.K_UP: "↑",
            pygame.K_DOWN: "↓",
            pygame.K_LEFT: "←",
            pygame.K_RIGHT: "→"
            # УБИРАЕМ WASD клавиши, так как мы их больше не используем
        }
        return key_symbols.get(key, "?")

    def generate_qte_sequence(self):
        # Используем стрелки И WASD
        keys = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,
                pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]
        sequence_length = random.randint(3, 5)

        # Проверяем, чтобы не запросить больше клавиш, чем есть
        if sequence_length > len(keys):
            sequence_length = len(keys)

        self.qte_keys = random.sample(keys, sequence_length)
        self.current_qte_index = 0
        self.qte_timer = self.qte_duration

    def move_towards_player(self, player, walls):
        if player.is_in_combat or self.is_in_combat:
            return

        if abs(self.x - player.x) <= 8 and abs(self.y - player.y) <= 8:
            dx = 0
            dy = 0

            if player.x < self.x:
                dx = -1
                self.direction = "left"
            elif player.x > self.x:
                dx = 1
                self.direction = "right"

            if player.y < self.y:
                dy = -1
                self.direction = "up"
            elif player.y > self.y:
                dy = 1
                self.direction = "down"

            if random.random() < 0.3:
                dx = random.choice([-1, 0, 1])
                dy = random.choice([-1, 0, 1])

            new_x = self.x + dx
            new_y = self.y + dy

            if not any(wall.x == new_x and wall.y == new_y for wall in walls):
                self.x = new_x
                self.y = new_y

    def draw(self, screen, offset_x, offset_y):
        enemy_x = offset_x + self.x * TILE_SIZE
        enemy_y = offset_y + self.y * TILE_SIZE

        if self.type == "goblin":
            color = GREEN
        elif self.type == "skeleton":
            color = GRAY
        elif self.type == "orc":
            color = DARK_GREEN
        else:
            color = DARK_RED

        pygame.draw.rect(screen, color,
                         (enemy_x, enemy_y, ENEMY_SIZE, ENEMY_SIZE))

        head_size = ENEMY_SIZE // 2
        pygame.draw.rect(screen, color,
                         (enemy_x, enemy_y - head_size // 2, ENEMY_SIZE, head_size))

        eye_size = ENEMY_SIZE // 8
        pygame.draw.circle(screen, RED,
                           (enemy_x + ENEMY_SIZE // 3, enemy_y + ENEMY_SIZE // 3),
                           eye_size)
        pygame.draw.circle(screen, RED,
                           (enemy_x + 2 * ENEMY_SIZE // 3, enemy_y + ENEMY_SIZE // 3),
                           eye_size)

        if self.health < self.max_health:
            health_width = 40
            health_height = 6
            health_x = enemy_x - (health_width - ENEMY_SIZE) // 2
            health_y = enemy_y - 12

            pygame.draw.rect(screen, DARK_RED,
                             (health_x, health_y, health_width, health_height))

            current_health_width = (self.health / self.max_health) * health_width
            pygame.draw.rect(screen, GREEN,
                             (health_x, health_y, current_health_width, health_height))