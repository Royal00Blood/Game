import pygame
import random
import os
from moviepy.editor import VideoFileClip
import threading
import time
import numpy as np

# Инициализация PyGame
pygame.init()
pygame.mixer.init()

from settings import *

class VideoPlayer:
    def __init__(self, screen):
        self.screen = screen
        self.video = None
        self.playing = False
        self.video_surface = None
        self.video_thread = None
        self.current_frame = 0
        self.video_type = None  # "game_over" или "victory"

    def load_video(self, video_path, video_type):
        """Загружает видео файл"""
        try:
            if os.path.exists(video_path):
                self.video = VideoFileClip(video_path)
                self.video_type = video_type
                return True
            else:
                print(f"Видео файл не найден: {video_path}")
                return False
        except Exception as e:
            print(f"Ошибка загрузки видео: {e}")
            return False

    def play_video(self, video_type):
        """Воспроизводит видео в зависимости от типа"""
        self.video_type = video_type
        self.playing = True
        self.current_frame = 0

        # Воспроизводим видео в отдельном потоке
        self.video_thread = threading.Thread(target=self._play_video_thread)
        self.video_thread.daemon = True
        self.video_thread.start()

    def _play_video_thread(self):
        """Поток для воспроизведения видео"""
        try:
            fps = self.video.fps
            frame_duration = 1.0 / fps

            for frame in self.video.iter_frames(fps=fps, dtype='uint8'):
                if not self.playing:
                    break

                # Конвертируем кадр в поверхность pygame
                frame_surface = pygame.image.frombuffer(
                    frame.tobytes(),
                    frame.shape[1::-1],
                    "RGB"
                )

                # Масштабируем под размер экрана
                self.video_surface = pygame.transform.scale(
                    frame_surface,
                    (SCREEN_WIDTH, SCREEN_HEIGHT)
                )

                self.current_frame += 1
                time.sleep(frame_duration)

        except Exception as e:
            print(f"Ошибка воспроизведения видео: {e}")
        finally:
            self.playing = False

    def play_fallback_animation(self, video_type):
        """Альтернативная анимация если видео недоступно"""
        self.playing = True
        self.video_type = video_type
        self.fallback_animation = True

        if video_type == "game_over":
            self._init_game_over_animation()
        else:  # victory
            self._init_victory_animation()

    def _init_game_over_animation(self):
        """Инициализация анимации поражения"""
        # Создаем анимацию крови
        self.blood_particles = []
        for _ in range(200):
            self.blood_particles.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'vx': random.uniform(-5, 5),
                'vy': random.uniform(-5, 5),
                'size': random.randint(3, 10),
                'color': (random.randint(150, 255), 0, 0),
                'life': random.randint(30, 90)
            })

        # Эффект затемнения
        self.darken_alpha = 0
        self.text_alpha = 0
        self.text_y_offset = 100
        self.flash_timer = 0

    def _init_victory_animation(self):
        """Инициализация анимации победы"""
        # Создаем анимацию конфетти
        self.confetti_particles = []
        for _ in range(300):
            self.confetti_particles.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(-100, 0),
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(1, 3),
                'size': random.randint(2, 6),
                'color': random.choice([(255, 215, 0), (255, 0, 0), (0, 255, 0),
                                        (0, 120, 255), (255, 165, 0), (128, 0, 128)]),
                'life': random.randint(60, 120),
                'shape': random.choice(['circle', 'rect'])
            })

        # Эффект сияния
        self.glow_alpha = 0
        self.text_alpha = 0
        self.text_y_offset = 100
        self.star_particles = []
        self.sparkle_timer = 0

    def update_fallback_animation(self):
        """Обновляет альтернативную анимацию"""
        if not hasattr(self, 'fallback_animation'):
            return

        if self.video_type == "game_over":
            self._update_game_over_animation()
        else:
            self._update_victory_animation()

    def _update_game_over_animation(self):
        """Обновляет анимацию поражения"""
        # Обновляем частицы крови
        for p in self.blood_particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.1  # гравитация
            p['life'] -= 1

            # Отскок от границ
            if p['x'] < 0 or p['x'] > SCREEN_WIDTH:
                p['vx'] *= -0.8
            if p['y'] < 0 or p['y'] > SCREEN_HEIGHT:
                p['vy'] *= -0.8
                p['y'] = min(max(p['y'], 0), SCREEN_HEIGHT)

        # Увеличиваем затемнение
        self.darken_alpha = min(200, self.darken_alpha + 5)
        self.text_alpha = min(255, self.text_alpha + 3)
        self.text_y_offset = max(0, self.text_y_offset - 2)
        self.flash_timer += 1

    def _update_victory_animation(self):
        """Обновляет анимацию победы"""
        # Обновляем конфетти
        for p in self.confetti_particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vx'] += random.uniform(-0.05, 0.05)  # случайное движение
            p['life'] -= 0.5

            # Если конфетти упало, создаем новое сверху
            if p['y'] > SCREEN_HEIGHT or p['life'] <= 0:
                p['x'] = random.randint(0, SCREEN_WIDTH)
                p['y'] = random.randint(-100, 0)
                p['vx'] = random.uniform(-2, 2)
                p['vy'] = random.uniform(1, 3)
                p['life'] = random.randint(60, 120)

        # Создаем звездочки для эффекта сияния
        if random.random() < 0.3:
            self.star_particles.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'size': random.randint(10, 30),
                'alpha': 255,
                'growth': random.uniform(0.5, 1.5)
            })

        # Обновляем звездочки
        for star in self.star_particles[:]:
            star['alpha'] -= 5
            star['size'] += star['growth']
            if star['alpha'] <= 0:
                self.star_particles.remove(star)

        # Эффекты
        self.glow_alpha = min(100, self.glow_alpha + 2)
        self.text_alpha = min(255, self.text_alpha + 3)
        self.text_y_offset = max(0, self.text_y_offset - 2)
        self.sparkle_timer += 1

    def draw(self):
        """Отрисовывает видео или анимацию"""
        if self.playing:
            if hasattr(self, 'fallback_animation') and self.fallback_animation:
                if self.video_type == "game_over":
                    self._draw_game_over_animation()
                else:
                    self._draw_victory_animation()
            elif self.video_surface:
                # Рисуем текущий кадр видео
                self.screen.blit(self.video_surface, (0, 0))

                # Добавляем затемнение для лучшей читаемости текста
                dark_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                dark_surf.fill((0, 0, 0, 100))
                self.screen.blit(dark_surf, (0, 0))

    def _draw_game_over_animation(self):
        """Отрисовывает анимацию поражения"""
        # Черный фон
        self.screen.fill(BLACK)

        # Рисуем частицы крови
        for p in self.blood_particles:
            if p['life'] > 0:
                alpha = min(255, p['life'] * 3)
                color_with_alpha = (*p['color'], alpha)

                # Создаем поверхность для частицы
                particle_surf = pygame.Surface((p['size'] * 2, p['size'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, color_with_alpha,
                                   (p['size'], p['size']), p['size'])
                self.screen.blit(particle_surf,
                                 (p['x'] - p['size'], p['y'] - p['size']))

        # Затемнение
        dark_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dark_surf.fill((0, 0, 0, self.darken_alpha))
        self.screen.blit(dark_surf, (0, 0))

        # Текст "GAME OVER"
        font_large = pygame.font.Font(None, 120)
        font_small = pygame.font.Font(None, 36)

        # Эффект кровавого текста
        game_over_text = font_large.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2,
                                                    SCREEN_HEIGHT // 2 - self.text_y_offset))

        # Тень текста
        shadow_text = font_large.render("GAME OVER", True, DARK_RED)
        shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH // 2 + 4,
                                                   SCREEN_HEIGHT // 2 - self.text_y_offset + 4))

        self.screen.blit(shadow_text, shadow_rect)

        # Основной текст с прозрачностью
        text_surf = pygame.Surface(game_over_text.get_size(), pygame.SRCALPHA)
        text_surf.blit(game_over_text, (0, 0))
        text_surf.set_alpha(self.text_alpha)
        self.screen.blit(text_surf, text_rect)

        # Дополнительный текст
        restart_text = font_small.render("Нажмите R для перезапуска", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2,
                                                     SCREEN_HEIGHT // 2 + 50))

        restart_surf = pygame.Surface(restart_text.get_size(), pygame.SRCALPHA)
        restart_surf.blit(restart_text, (0, 0))
        restart_surf.set_alpha(self.text_alpha)
        self.screen.blit(restart_surf, restart_rect)

        # Эффект вспышки
        if self.text_alpha > 200:
            flash_alpha = int((pygame.time.get_ticks() % 1000) / 1000 * 100)
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash_surf.fill((255, 255, 255, flash_alpha))
            self.screen.blit(flash_surf, (0, 0))

    def _draw_victory_animation(self):
        """Отрисовывает анимацию победы"""
        # Темно-синий фон
        self.screen.fill((10, 10, 50))

        # Рисуем конфетти
        for p in self.confetti_particles:
            alpha = min(255, p['life'] * 2)
            color_with_alpha = (*p['color'], alpha)

            # Создаем поверхность для конфетти
            confetti_surf = pygame.Surface((p['size'] * 2, p['size'] * 2), pygame.SRCALPHA)

            if p['shape'] == 'circle':
                pygame.draw.circle(confetti_surf, color_with_alpha,
                                   (p['size'], p['size']), p['size'])
            else:  # прямоугольник
                pygame.draw.rect(confetti_surf, color_with_alpha,
                                 (0, 0, p['size'] * 2, p['size'] * 2))

            self.screen.blit(confetti_surf,
                             (p['x'] - p['size'], p['y'] - p['size']))

        # Рисуем звездочки
        for star in self.star_particles:
            star_surf = pygame.Surface((star['size'] * 2, star['size'] * 2), pygame.SRCALPHA)

            # Рисуем звезду
            points = []
            for i in range(5):
                angle = 2 * np.pi * i / 5 - np.pi / 2
                outer_x = star['size'] + star['size'] * 0.8 * np.cos(angle)
                outer_y = star['size'] + star['size'] * 0.8 * np.sin(angle)
                points.append((outer_x, outer_y))

                inner_angle = angle + 2 * np.pi / 10
                inner_x = star['size'] + star['size'] * 0.4 * np.cos(inner_angle)
                inner_y = star['size'] + star['size'] * 0.4 * np.sin(inner_angle)
                points.append((inner_x, inner_y))

            star_color = (255, 255, 200, star['alpha'])
            pygame.draw.polygon(star_surf, star_color, points)
            self.screen.blit(star_surf, (star['x'] - star['size'], star['y'] - star['size']))

        # Эффект сияния
        glow_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        glow_color = (255, 255, 200, self.glow_alpha // 2)
        pygame.draw.circle(glow_surf, glow_color,
                           (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                           SCREEN_WIDTH // 3)
        self.screen.blit(glow_surf, (0, 0))

        # Текст "ПОБЕДА!"
        font_large = pygame.font.Font(None, 120)
        font_medium = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 36)

        # Эффект золотого текста
        victory_text = font_large.render("ПОБЕДА!", True, GOLD)
        text_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2,
                                                  SCREEN_HEIGHT // 2 - self.text_y_offset))

        # Тень текста
        shadow_text = font_large.render("ПОБЕДА!", True, (200, 150, 0))
        shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH // 2 + 4,
                                                   SCREEN_HEIGHT // 2 - self.text_y_offset + 4))

        self.screen.blit(shadow_text, shadow_rect)

        # Основной текст с прозрачностью
        text_surf = pygame.Surface(victory_text.get_size(), pygame.SRCALPHA)
        text_surf.blit(victory_text, (0, 0))
        text_surf.set_alpha(self.text_alpha)
        self.screen.blit(text_surf, text_rect)

        # Подзаголовок
        subtitle_text = font_medium.render("Сокровище найдено!", True, YELLOW)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2,
                                                       SCREEN_HEIGHT // 2 + 30))
        subtitle_surf = pygame.Surface(subtitle_text.get_size(), pygame.SRCALPHA)
        subtitle_surf.blit(subtitle_text, (0, 0))
        subtitle_surf.set_alpha(self.text_alpha)
        self.screen.blit(subtitle_surf, subtitle_rect)

        # Дополнительный текст
        restart_text = font_small.render("Нажмите R для новой игры", True, LIGHT_BLUE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2,
                                                     SCREEN_HEIGHT // 2 + 90))

        restart_surf = pygame.Surface(restart_text.get_size(), pygame.SRCALPHA)
        restart_surf.blit(restart_text, (0, 0))
        restart_surf.set_alpha(self.text_alpha)
        self.screen.blit(restart_surf, restart_rect)

        # Эффект мерцания
        if self.sparkle_timer % 20 < 10:
            sparkle_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            sparkle_alpha = 50 + int(50 * np.sin(self.sparkle_timer * 0.1))
            sparkle_surf.fill((255, 255, 255, sparkle_alpha))
            self.screen.blit(sparkle_surf, (0, 0))

    def stop(self):
        """Останавливает воспроизведение"""
        self.playing = False
        if self.video:
            self.video.close()
        if hasattr(self, 'fallback_animation'):
            self.fallback_animation = False