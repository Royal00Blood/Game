import pygame
import random
import sys
import os
import numpy as np
from Chest import Chest
from Enemy import Enemy
from Item import Item
from Player import Player
from QTE import QTE
from VideoPlayer import VideoPlayer
from Wall import Wall

# Инициализация PyGame
pygame.init()
pygame.mixer.init()

from settings import *

# Основной класс игры
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Бродилка: Лабиринт с видео-финалами")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)

        # Инициализация видеоплеера
        self.video_player = VideoPlayer(self.screen)

        # Загружаем видео (если есть)
        self.video_loaded_game_over = self.video_player.load_video(
            "assets/videos/game_over.mp4", "game_over"
        )
        self.video_loaded_victory = self.video_player.load_video(
            "assets/videos/victory.mp4", "victory"
        )

        # Звуки
        self.sound_enabled = True
        self.load_sounds()

        # Центрирование карты
        self.map_width_px = MAP_WIDTH * TILE_SIZE
        self.map_height_px = MAP_HEIGHT * TILE_SIZE
        self.map_offset_x = (SCREEN_WIDTH - self.map_width_px) // 2
        self.map_offset_y = (SCREEN_HEIGHT - self.map_height_px) // 2

        self.reset_game()

    def load_sounds(self):
        """Загружает звуковые эффекты"""
        try:
            # Простые звуки
            self.sounds = {
                'death': self.create_sound(200, 100, 1000),
                'victory': self.create_sound(400, 800, 2000),
                'hit': self.create_sound(300, 200, 500),
                'collect': self.create_sound(600, 400, 300)
            }
        except:
            self.sound_enabled = False

    def create_sound(self, freq_start, freq_end, duration):
        """Создает простой звуковой эффект"""
        sample_rate = 44100
        t = np.linspace(0, duration / 1000, int(sample_rate * duration / 1000))

        # Частотная модуляция
        freq = np.linspace(freq_start, freq_end, len(t))
        wave = 0.5 * np.sin(2 * np.pi * freq * t)

        # Затухание
        envelope = np.exp(-t * 5)
        wave = wave * envelope

        # Конвертируем в звук pygame
        sound_array = (wave * 32767).astype(np.int16)
        sound_array = np.repeat(sound_array[:, np.newaxis], 2, axis=1)

        return pygame.sndarray.make_sound(sound_array)

    def generate_maze(self):
        """Генерация лабиринта"""
        # Создаем сетку полностью заполненную стенами
        grid = [[1 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

        # Алгоритм backtracking
        start_x, start_y = 1, 1
        grid[start_y][start_x] = 0
        stack = [(start_x, start_y)]
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]

        while stack:
            x, y = stack[-1]
            possible_dirs = []

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 1 <= nx < MAP_WIDTH - 1 and 1 <= ny < MAP_HEIGHT - 1 and grid[ny][nx] == 1:
                    neighbors = 0
                    for ddx, ddy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                        nnx, nny = nx + ddx, ny + ddy
                        if 0 <= nnx < MAP_WIDTH and 0 <= nny < MAP_HEIGHT and grid[nny][nnx] == 0:
                            neighbors += 1
                    if neighbors <= 1:
                        possible_dirs.append((dx, dy))

            if possible_dirs:
                dx, dy = random.choice(possible_dirs)
                wx, wy = x + dx // 2, y + dy // 2
                nx, ny = x + dx, y + dy

                grid[wy][wx] = 0
                grid[ny][nx] = 0
                stack.append((nx, ny))
            else:
                stack.pop()

        # Создаем внешние стены
        for x in range(MAP_WIDTH):
            grid[0][x] = 1
            grid[MAP_HEIGHT - 1][x] = 1
        for y in range(MAP_HEIGHT):
            grid[y][0] = 1
            grid[y][MAP_WIDTH - 1] = 1

        # Преобразуем сетку в объекты Wall
        walls = []
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if grid[y][x] == 1:
                    walls.append(Wall(x, y))

        return walls

    def find_free_position(self, walls, occupied_positions=None, min_distance=2):
        """Находит свободную позицию"""
        if occupied_positions is None:
            occupied_positions = []

        max_attempts = 100
        for _ in range(max_attempts):
            x = random.randint(1, MAP_WIDTH - 2)
            y = random.randint(1, MAP_HEIGHT - 2)

            if any(w.x == x and w.y == y for w in walls):
                continue

            too_close = False
            for ox, oy in occupied_positions:
                if abs(x - ox) < min_distance and abs(y - oy) < min_distance:
                    too_close = True
                    break

            if not too_close:
                return (x, y)

        # fallback
        for y in range(1, MAP_HEIGHT - 2):
            for x in range(1, MAP_WIDTH - 2):
                if not any(w.x == x and w.y == y for w in walls):
                    return (x, y)

        return (1, 1)

    def reset_game(self):
        # Создаем лабиринт
        self.walls = self.generate_maze()

        # Игрок
        start_pos = self.find_free_position(self.walls)
        self.player = Player(start_pos[0], start_pos[1])

        # Список занятых позиций
        occupied_positions = [start_pos]

        # Враги
        self.enemies = []
        enemy_types = ["goblin", "skeleton", "orc", "troll", "goblin", "skeleton", "orc"]

        for enemy_type in enemy_types:
            pos = self.find_free_position(self.walls, occupied_positions, min_distance=3)
            occupied_positions.append(pos)
            self.enemies.append(Enemy(pos[0], pos[1], enemy_type))

        # Предметы
        self.items = []

        # Ключи
        for _ in range(4):
            pos = self.find_free_position(self.walls, occupied_positions, min_distance=2)
            occupied_positions.append(pos)
            self.items.append(Item(pos[0], pos[1], "key"))

        # Аптечки
        for _ in range(4):
            pos = self.find_free_position(self.walls, occupied_positions, min_distance=2)
            occupied_positions.append(pos)
            self.items.append(Item(pos[0], pos[1], "health"))

        # Зелья
        for _ in range(2):
            pos = self.find_free_position(self.walls, occupied_positions, min_distance=2)
            occupied_positions.append(pos)
            self.items.append(Item(pos[0], pos[1], "potion"))

        # Сокровища
        for _ in range(2):
            pos = self.find_free_position(self.walls, occupied_positions, min_distance=2)
            occupied_positions.append(pos)
            self.items.append(Item(pos[0], pos[1], "treasure"))

        # Сундук
        chest_pos = None
        attempts = 0
        while chest_pos is None and attempts < 50:
            x = random.randint(MAP_WIDTH - 5, MAP_WIDTH - 2)
            y = random.randint(MAP_HEIGHT - 5, MAP_HEIGHT - 2)
            if not any(w.x == x and w.y == y for w in self.walls):
                too_close = False
                for ox, oy in occupied_positions:
                    if abs(x - ox) < 3 and abs(y - oy) < 3:
                        too_close = True
                        break
                if not too_close:
                    chest_pos = (x, y)
                    occupied_positions.append(chest_pos)
            attempts += 1

        if chest_pos is None:
            chest_pos = (MAP_WIDTH - 2, MAP_HEIGHT - 2)

        self.chest = Chest(chest_pos[0], chest_pos[1])

        # QTE система
        self.active_qte = None
        self.combat_enemy = None

        # Игровое состояние
        self.game_over = False
        self.victory = False
        self.showing_final_video = False
        self.final_video_timer = 0
        self.final_video_type = None
        self.message = ""
        self.message_timer = 0

        # Останавливаем видео если оно играет
        self.video_player.stop()

    def start_combat(self, enemy):
        self.player.is_in_combat = True
        enemy.is_in_combat = True
        self.combat_enemy = enemy
        self.active_qte = QTE(enemy)
        self.message = "Начался бой! Следуйте указаниям QTE!"
        self.message_timer = 60

        # Звук начала боя
        if self.sound_enabled:
            self.sounds['hit'].play()

    def handle_combat_result(self, success):
        if success:
            damage = random.randint(20, 40)
            self.combat_enemy.health -= damage
            self.message = f"Вы нанесли {damage} урона врагу!"

            if self.combat_enemy.health <= 0:
                self.enemies.remove(self.combat_enemy)
                self.player.score += 100
                self.message = "Вы победили врага! +100 очков"
        else:
            damage = random.randint(10, 25)
            self.player.health -= damage
            self.message = f"Вы получили {damage} урона!"

            if self.player.health <= 0:
                self.game_over = True
                self.final_video_timer = 90  # 1.5 секунды до показа видео
                self.final_video_type = "game_over"
                self.message = "Игра окончена!"

                # Звук смерти
                if self.sound_enabled:
                    self.sounds['death'].play()

        self.player.is_in_combat = False
        if self.combat_enemy and self.combat_enemy in self.enemies:
            self.combat_enemy.is_in_combat = False
            self.combat_enemy.generate_qte_sequence()

        self.combat_enemy = None
        self.active_qte = None
        self.message_timer = 60

    def handle_chest_interaction(self):
        if (abs(self.player.x - self.chest.x) <= 1 and
                abs(self.player.y - self.chest.y) <= 1):

            success, msg = self.chest.try_open(self.player)
            self.message = msg
            self.message_timer = 60

            if success and self.chest.contains_treasure:
                self.victory = True
                self.final_video_timer = 90  # 1.5 секунды до показа видео
                self.final_video_type = "victory"
                self.message = "ПОБЕДА! Вы нашли главное сокровище!"

                # Звук победы
                if self.sound_enabled:
                    self.sounds['victory'].play()

    def update(self):
        if self.showing_final_video:
            # Обновляем анимацию если видео не загружено
            if hasattr(self.video_player, 'fallback_animation') and self.video_player.fallback_animation:
                self.video_player.update_fallback_animation()
            return

        if (self.game_over or self.victory) and not self.showing_final_video:
            self.final_video_timer -= 1
            if self.final_video_timer <= 0:
                self.showing_final_video = True

                # Пытаемся воспроизвести видео
                video_loaded = (self.final_video_type == "game_over" and self.video_loaded_game_over) or \
                               (self.final_video_type == "victory" and self.video_loaded_victory)

                if video_loaded:
                    self.video_player.play_video(self.final_video_type)
                else:
                    # Используем анимацию
                    self.video_player.play_fallback_animation(self.final_video_type)

            return

        if self.active_qte:
            self.active_qte.update()
            if self.active_qte.result is not None:
                self.handle_combat_result(self.active_qte.result)
            return

        for enemy in self.enemies:
            enemy.move_towards_player(self.player, self.walls)

        for enemy in self.enemies:
            if (enemy.x == self.player.x and enemy.y == self.player.y and
                    not self.player.is_in_combat and not enemy.is_in_combat):
                self.start_combat(enemy)
                break

        for item in self.items[:]:
            if item.x == self.player.x and item.y == self.player.y:
                if item.type == "health":
                    self.player.health = min(self.player.max_health, self.player.health + 40)
                    self.message = "Вы нашли аптечку! +40 здоровья"
                    self.player.score += 20
                elif item.type == "key":
                    self.player.keys += 1
                    self.message = "Вы нашли ключ!"
                    self.player.score += 30
                elif item.type == "treasure":
                    self.player.score += 150
                    self.message = "Вы нашли сокровище! +150 очков"
                elif item.type == "potion":
                    self.player.health = min(self.player.max_health, self.player.health + 60)
                    self.message = "Вы выпили зелье! +60 здоровья"
                    self.player.score += 40

                # Звук сбора предмета
                if self.sound_enabled:
                    self.sounds['collect'].play()

                self.items.remove(item)
                self.message_timer = 60

        self.handle_chest_interaction()

        if self.message_timer > 0:
            self.message_timer -= 1

    def draw_game_screen(self):
        """Отрисовывает игровой экран"""
        self.screen.fill((30, 30, 50))

        # Фон для карты
        pygame.draw.rect(self.screen, (40, 40, 70),
                         (self.map_offset_x - 10, self.map_offset_y - 10,
                          self.map_width_px + 20, self.map_height_px + 20))

        # Пол
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                tile_x = self.map_offset_x + x * TILE_SIZE
                tile_y = self.map_offset_y + y * TILE_SIZE

                if (x + y) % 2 == 0:
                    floor_color = (60, 60, 90)
                else:
                    floor_color = (50, 50, 80)

                pygame.draw.rect(self.screen, floor_color,
                                 (tile_x, tile_y, TILE_SIZE, TILE_SIZE))

        # Объекты
        for wall in self.walls:
            wall.draw(self.screen, self.map_offset_x, self.map_offset_y)

        for item in self.items:
            item.draw(self.screen, self.map_offset_x, self.map_offset_y)

        self.chest.draw(self.screen, self.map_offset_x, self.map_offset_y)

        for enemy in self.enemies:
            enemy.draw(self.screen, self.map_offset_x, self.map_offset_y)

        self.player.draw(self.screen, self.map_offset_x, self.map_offset_y)

        # QTE
        if self.active_qte:
            self.active_qte.draw(self.screen)

        # Интерфейс
        pygame.draw.rect(self.screen, (20, 20, 40, 220),
                         (0, 0, SCREEN_WIDTH, 60))
        pygame.draw.line(self.screen, YELLOW, (0, 60), (SCREEN_WIDTH, 60), 3)

        # Статистика
        stats = [
            (f"♥ Здоровье: {self.player.health}/{self.player.max_health}", WHITE, 20),
            (f"★ Очки: {self.player.score}", YELLOW, 250),
            (f"🔑 Ключи: {self.player.keys}", YELLOW, 450),
            (f"👹 Врагов: {len(self.enemies)}", RED, 650),
        ]

        for text, color, x in stats:
            text_surface = self.font.render(text, True, color)
            self.screen.blit(text_surface, (x, 20))

        # Сокровище
        treasure_status = "💰 НАЙДЕНО" if self.player.has_treasure else "💰 НЕ НАЙДЕНО"
        treasure_color = GOLD if self.player.has_treasure else GRAY
        treasure_text = self.font.render(treasure_status, True, treasure_color)
        self.screen.blit(treasure_text, (850, 20))

        # Сообщения
        if self.message_timer > 0:
            message_surface = self.small_font.render(self.message, True, YELLOW)
            message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))

            pygame.draw.rect(self.screen, (0, 0, 0, 180),
                             (message_rect.x - 15, message_rect.y - 8,
                              message_rect.width + 30, message_rect.height + 16),
                             border_radius=10)
            pygame.draw.rect(self.screen, YELLOW,
                             (message_rect.x - 15, message_rect.y - 8,
                              message_rect.width + 30, message_rect.height + 16),
                             3, border_radius=10)

            self.screen.blit(message_surface, message_rect)

        # Статус игры
        status_y = SCREEN_HEIGHT - 50
        if self.player.is_in_combat:
            status_text = "⚔️ СРАЖЕНИЕ! Нажимайте стрелки в указанном порядке!"
            color = RED
        elif self.victory or self.game_over:
            if self.victory:
                status_text = "🎉 ПОБЕДА! Секунду..."
                color = GOLD
            else:
                status_text = "💀 ПОРАЖЕНИЕ! Секунду..."
                color = RED
        else:
            status_text = "🗺️ Исследуйте лабиринт, найдите ключи и откройте сундук!"
            color = LIGHT_BLUE

        status_surface = self.small_font.render(status_text, True, color)
        self.screen.blit(status_surface,
                         (SCREEN_WIDTH // 2 - status_surface.get_width() // 2, status_y))

        # Управление
        controls = self.small_font.render("Управление: Стрелки/WASD - движение, R - перезапуск, ESC - выход",
                                          True, GRAY)
        self.screen.blit(controls,
                         (SCREEN_WIDTH // 2 - controls.get_width() // 2, status_y + 25))

    def draw(self):
        if self.showing_final_video:
            # Показываем видео или анимацию
            self.video_player.draw()

            # Кнопка перезапуска поверх видео
            font = pygame.font.Font(None, 48)
            restart_text = font.render("Нажмите R для новой игры", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2,
                                                         SCREEN_HEIGHT - 50))

            # Фон для текста
            pygame.draw.rect(self.screen, (0, 0, 0, 150),
                             (restart_rect.x - 20, restart_rect.y - 10,
                              restart_rect.width + 40, restart_rect.height + 20),
                             border_radius=10)
            pygame.draw.rect(self.screen, YELLOW,
                             (restart_rect.x - 20, restart_rect.y - 10,
                              restart_rect.width + 40, restart_rect.height + 20),
                             3, border_radius=10)

            self.screen.blit(restart_text, restart_rect)

        else:
            self.draw_game_screen()

            # Если игра окончена/победа, но еще не показываем видео
            if (self.game_over or self.victory) and not self.showing_final_video:
                # Затемняем экран
                dark_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                dark_alpha = min(180, 180 - self.final_video_timer * 2)
                dark_surf.fill((0, 0, 0, dark_alpha))
                self.screen.blit(dark_surf, (0, 0))

                # Анимация перед видео
                font_large = pygame.font.Font(None, 72)
                countdown = max(0, (self.final_video_timer - 30) // 60)

                if countdown > 0:
                    countdown_text = font_large.render(str(countdown), True,
                                                       RED if self.game_over else GOLD)
                    countdown_rect = countdown_text.get_rect(center=(SCREEN_WIDTH // 2,
                                                                     SCREEN_HEIGHT // 2))

                    # Пульсация
                    pulse = (pygame.time.get_ticks() % 1000) / 1000
                    scale = 1.0 + pulse * 0.5

                    scaled_text = pygame.transform.scale_by(countdown_text, scale)
                    scaled_rect = scaled_text.get_rect(center=(SCREEN_WIDTH // 2,
                                                               SCREEN_HEIGHT // 2))

                    self.screen.blit(scaled_text, scaled_rect)

    def run(self):
        running = True

        while running:
            key_pressed = None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.video_player.stop()

                if event.type == pygame.KEYDOWN:
                    key_pressed = event.key

                    if event.key == pygame.K_ESCAPE:
                        running = False
                        self.video_player.stop()

                    if event.key == pygame.K_r:
                        # Всегда можно перезапустить
                        self.reset_game()

                    if not self.showing_final_video and not self.game_over and not self.victory:
                        if self.active_qte:
                            self.active_qte.update(key_pressed)
                        elif not self.player.is_in_combat:
                            if event.key in (pygame.K_UP, pygame.K_w):
                                self.player.move(0, -1, self.walls)
                            elif event.key in (pygame.K_DOWN, pygame.K_s):
                                self.player.move(0, 1, self.walls)
                            elif event.key in (pygame.K_LEFT, pygame.K_a):
                                self.player.move(-1, 0, self.walls)
                            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                                self.player.move(1, 0, self.walls)

            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


# Создание видеофайлов (если их нет)
def create_video_files():
    """Создает простые видеофайлы для поражения и победы"""
    import cv2

    os.makedirs("assets/videos", exist_ok=True)

    # Создаем видео поражения
    create_game_over_video()

    # Создаем видео победы
    create_victory_video()

    print("Видеофайлы созданы в папке assets/videos/")


def create_game_over_video():
    """Создает видео поражения"""
    try:
        import cv2
        import numpy as np

        width, height = 800, 600
        fps = 30
        duration = 5
        total_frames = fps * duration

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter('assets/videos/game_over.mp4', fourcc, fps, (width, height))

        for frame_num in range(total_frames):
            progress = frame_num / total_frames

            # Темный фон с красными оттенками
            frame = np.zeros((height, width, 3), dtype=np.uint8)

            # Красное свечение
            glow_intensity = int(100 * (1 - progress))
            for y in range(height):
                for x in range(width):
                    dist_to_center = np.sqrt((x - width / 2) ** 2 + (y - height / 2) ** 2)
                    if dist_to_center < 300:
                        red_value = min(100, int(100 * (1 - dist_to_center / 300)))
                        frame[y, x] = (0, 0, red_value + glow_intensity)

            # Трещины
            for i in range(5):
                start_x = random.randint(0, width)
                start_y = random.randint(0, height)
                for j in range(10):
                    end_x = start_x + random.randint(-50, 50)
                    end_y = start_y + random.randint(0, 20)
                    color_intensity = int(100 + 155 * progress)
                    cv2.line(frame, (start_x, start_y), (end_x, end_y),
                             (0, 0, color_intensity), 2)
                    start_x, start_y = end_x, end_y

            # Текст
            text = "GAME OVER"
            font_scale = 1.5 + progress * 1.0
            thickness = 5

            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
            text_x = (width - text_size[0]) // 2
            text_y = (height + text_size[1]) // 2

            # Тень
            cv2.putText(frame, text, (text_x + 3, text_y + 3),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (30, 30, 30), thickness)

            # Основной текст
            text_color = (0, 0, 100 + int(155 * progress))
            cv2.putText(frame, text, (text_x, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, thickness)

            video.write(frame)

        video.release()
        print("Видео поражения создано")
    except ImportError:
        print("OpenCV не установлен, видео не будет создано")


def create_victory_video():
    """Создает видео победы"""
    try:
        import cv2
        import numpy as np

        width, height = 800, 600
        fps = 30
        duration = 5
        total_frames = fps * duration

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter('assets/videos/victory.mp4', fourcc, fps, (width, height))

        for frame_num in range(total_frames):
            progress = frame_num / total_frames

            # Золотой фон
            frame = np.zeros((height, width, 3), dtype=np.uint8)

            # Градиент от темно-золотого к светлому
            for y in range(height):
                gold_value = 100 + int(100 * (y / height))
                frame[y, :] = (0, gold_value * 0.8, gold_value)

            # Сияющие частицы
            for _ in range(20):
                x = random.randint(0, width)
                y = random.randint(0, height)
                size = random.randint(5, 15)
                brightness = int(200 + 55 * np.sin(frame_num * 0.1))
                cv2.circle(frame, (x, y), size, (0, brightness * 0.8, brightness), -1)

            # Текст
            text = "VICTORY"
            font_scale = 2.0 + progress * 0.5
            thickness = 8

            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
            text_x = (width - text_size[0]) // 2
            text_y = (height + text_size[1]) // 2

            # Сияние
            for offset in range(10, 0, -2):
                glow_color = (0, 100 + offset * 5, 150 + offset * 10)
                cv2.putText(frame, text, (text_x, text_y),
                            cv2.FONT_HERSHEY_SIMPLEX, font_scale, glow_color, offset)

            # Основной текст
            text_color = (0, 200, 255)
            cv2.putText(frame, text, (text_x, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, thickness)

            video.write(frame)

        video.release()
        print("Видео победы создано")
    except ImportError:
        print("OpenCV не установлен, видео не будет создано")


if __name__ == "__main__":
    # Создаем видеофайлы если их нет
    if not os.path.exists("assets/videos/game_over.mp4") or not os.path.exists("assets/videos/victory.mp4"):
        print("Видеофайлы не найдены, создаем...")
        create_video_files()

    # Запускаем игру
    game = Game()
    game.run()