import pygame
from settings import *
# Класс QTE
class QTE:
    def __init__(self, enemy):
        self.enemy = enemy
        self.keys = enemy.qte_keys
        self.current_index = 0
        self.timer = enemy.qte_duration
        self.is_active = True
        self.result = None

    def update(self, key_pressed=None):
        if not self.is_active:
            return

        self.timer -= 1

        if self.timer <= 0:
            self.is_active = False
            self.result = False
            return

        if key_pressed:
            if key_pressed == self.keys[self.current_index]:
                self.current_index += 1
                if self.current_index >= len(self.keys):
                    self.is_active = False
                    self.result = True
            else:
                self.is_active = False
                self.result = False
    def draw(self, screen):
        if not self.is_active:
            return

        qte_width = 600
        qte_height = 200
        qte_x = (SCREEN_WIDTH - qte_width) // 2
        qte_y = (SCREEN_HEIGHT - qte_height) // 2 - 50

        qte_surface = pygame.Surface((qte_width, qte_height), pygame.SRCALPHA)
        qte_surface.fill((20, 20, 40, 220))
        screen.blit(qte_surface, (qte_x, qte_y))

        pygame.draw.rect(screen, YELLOW,
                         (qte_x, qte_y, qte_width, qte_height), 4, border_radius=10)

        font_large = pygame.font.Font(None, 44)
        font_medium = pygame.font.Font(None, 36)
        font_small = pygame.font.Font(None, 32)

        title_text = "⚔️ БОЙ! ⚔️"
        title = font_large.render(title_text, True, RED)
        title_x = qte_x + (qte_width - title.get_width()) // 2
        screen.blit(title, (title_x, qte_y + 15))

        timer_width = qte_width - 40
        progress = self.timer / self.enemy.qte_duration
        current_timer_width = progress * timer_width

        pygame.draw.rect(screen, DARK_RED,
                         (qte_x + 20, qte_y + 60, timer_width, 15),
                         border_radius=7)
        pygame.draw.rect(screen, GREEN,
                         (qte_x + 20, qte_y + 60, current_timer_width, 15),
                         border_radius=7)
        pygame.draw.rect(screen, WHITE,
                         (qte_x + 20, qte_y + 60, timer_width, 15),
                         2, border_radius=7)

        hint_text = "Нажимайте клавиши в указанном порядке:"
        hint = font_small.render(hint_text, True, LIGHT_BLUE)
        hint_x = qte_x + (qte_width - hint.get_width()) // 2
        screen.blit(hint, (hint_x, qte_y + 90))

        key_spacing = 75
        total_keys_width = len(self.keys) * key_spacing
        start_x = qte_x + (qte_width - total_keys_width) // 2
        key_y = qte_y + 120

        for i, key in enumerate(self.keys):
            key_x = start_x + i * key_spacing

            if i < self.current_index:
                key_color = GREEN
                border_color = DARK_GREEN
                text_color = WHITE
            elif i == self.current_index:
                key_color = YELLOW
                border_color = ORANGE
                text_color = BLACK
                pulse = (pygame.time.get_ticks() // 200) % 2
                if pulse:
                    key_color = (255, 255, 150)
            else:
                key_color = GRAY
                border_color = DARK_GRAY
                text_color = WHITE

            pygame.draw.rect(screen, (0, 0, 0, 100),
                             (key_x + 2, key_y + 2, 60, 60),
                             border_radius=8)
            pygame.draw.rect(screen, key_color,
                             (key_x, key_y, 60, 60), border_radius=8)
            pygame.draw.rect(screen, border_color,
                             (key_x, key_y, 60, 60), 3, border_radius=8)

            key_symbol = self.key_to_symbol(key)
            key_font = pygame.font.Font(None, 32)
            symbol_text = key_font.render(key_symbol, True, text_color)
            symbol_rect = symbol_text.get_rect(center=(key_x + 30, key_y + 30))
            screen.blit(symbol_text, symbol_rect)

            num_text = font_medium.render(str(i + 1), True, WHITE)
            num_x = key_x + (60 - num_text.get_width()) // 2
            screen.blit(num_text, (num_x, key_y - 25))

            if i < len(self.keys) - 1:
                arrow_x = key_x + 65
                arrow_y = key_y + 30
                pygame.draw.line(screen, WHITE,
                                 (arrow_x, arrow_y),
                                 (arrow_x + 10, arrow_y), 3)
                pygame.draw.polygon(screen, WHITE,
                                    [(arrow_x + 10, arrow_y - 5),
                                     (arrow_x + 10, arrow_y + 5),
                                     (arrow_x + 20, arrow_y)])

        bottom_hint = "Используйте клавиши стрелок"
        bottom_hint_text = font_small.render(bottom_hint, True, GRAY)
        bottom_hint_x = qte_x + (qte_width - bottom_hint_text.get_width()) // 2
        screen.blit(bottom_hint_text, (bottom_hint_x, qte_y + qte_height - 30))

    def key_to_symbol(self, key):
        key_symbols = {
            pygame.K_UP: "↑",
            pygame.K_DOWN: "↓",
            pygame.K_LEFT: "←",
            pygame.K_RIGHT: "→",
        }
        return key_symbols.get(key, "?")