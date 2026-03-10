import pygame
import os
import random
import math

pygame.init()

# Global Constants
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Загрузка спрайтов персонажа и препятствий
RUNNING = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png"))]
JUMPING = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png"))
DUCKING = [pygame.image.load(os.path.join("Assets/Dino", "DinoDuck1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoDuck2.png"))]

SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]

BIRD = [pygame.image.load(os.path.join("Assets/Bird", "Bird1.png")),
        pygame.image.load(os.path.join("Assets/Bird", "Bird2.png"))]

CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))
BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))

# Новый ретро-фон заката
class RetroSunsetBackground:
    def __init__(self):
        # Создаем поверхность для статического фона
        self.background_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Цвета для градиента заката (ретро-палитра)
        self.colors = [
            (255, 94, 77),    # Красновато-оранжевый
            (255, 150, 79),   # Оранжевый
            (255, 201, 99),   # Желтый
            (173, 216, 230),  # Голубой
            (135, 206, 235),  # Небесно-голубой
            (70, 130, 180)    # Стальной синий
        ]
        
        # Создаем статический фон один раз
        self.create_static_background()
        
        # Динамические элементы (облака и солнце)
        self.sun_radius = 60
        self.sun_x = SCREEN_WIDTH // 2
        self.sun_y = 150
        self.sun_color = (255, 204, 0)
        
        # Облака
        self.clouds = []
        self.create_clouds()

    def create_static_background(self):
        """Создаем статический фон (вызывается один раз)"""
        # Отрисовка градиентного закатного неба
        for i in range(6):
            color = self.colors[i]
            rect_height = SCREEN_HEIGHT // 6
            pygame.draw.rect(self.background_surface, color, 
                           (0, i * rect_height, SCREEN_WIDTH, rect_height))
        
        # Пиксельные горы на заднем плане
        self.draw_static_mountains()
        
        # Статичные звезды
        self.draw_static_stars()

    def draw_static_mountains(self):
        """Отрисовка статичных пиксельных гор"""
        # Создаем фиксированные горы с предопределенными позициями
        mountain_positions = [
            {'x': -50, 'y': 250, 'width': 400, 'height': 180, 'color': (80, 60, 40)},
            {'x': 300, 'y': 280, 'width': 500, 'height': 150, 'color': (70, 50, 30)},
            {'x': 700, 'y': 260, 'width': 450, 'height': 170, 'color': (90, 70, 50)},
            {'x': 1000, 'y': 270, 'width': 400, 'height': 160, 'color': (75, 55, 35)},
            {'x': 1400, 'y': 290, 'width': 350, 'height': 140, 'color': (85, 65, 45)},
        ]
        
        for mountain in mountain_positions:
            # Основная часть горы
            points = [
                (mountain['x'], mountain['y'] + mountain['height']),
                (mountain['x'] + mountain['width'] // 2, mountain['y']),
                (mountain['x'] + mountain['width'], mountain['y'] + mountain['height'])
            ]
            pygame.draw.polygon(self.background_surface, mountain['color'], points)
            
            # Создаем пиксельный эффект один раз
            mountain_surface = pygame.Surface((mountain['width'], mountain['height']), pygame.SRCALPHA)
            
            # Заполняем основным цветом
            mountain_points = [
                (0, mountain['height']),
                (mountain['width'] // 2, 0),
                (mountain['width'], mountain['height'])
            ]
            pygame.draw.polygon(mountain_surface, mountain['color'], mountain_points)
            
            # Добавляем пиксельный шум
            for _ in range(mountain['width'] * mountain['height'] // 100):
                x = random.randint(0, mountain['width'] - 1)
                y = random.randint(0, mountain['height'] - 1)
                
                # Проверяем, находится ли точка внутри треугольника
                if self.is_point_in_triangle(x, y, mountain_points):
                    shade = random.randint(-15, 15)
                    pixel_color = (
                        max(0, min(255, mountain['color'][0] + shade)),
                        max(0, min(255, mountain['color'][1] + shade)),
                        max(0, min(255, mountain['color'][2] + shade))
                    )
                    pygame.draw.rect(mountain_surface, pixel_color, (x, y, 2, 2))
            
            # Накладываем гору на фон
            self.background_surface.blit(mountain_surface, (mountain['x'], mountain['y']))

    def is_point_in_triangle(self, x, y, triangle_points):
        """Проверяет, находится ли точка внутри треугольника"""
        x1, y1 = triangle_points[0]
        x2, y2 = triangle_points[1]
        x3, y3 = triangle_points[2]
        
        # Вычисляем барицентрические координаты
        denominator = ((y2 - y3)*(x1 - x3) + (x3 - x2)*(y1 - y3))
        if denominator == 0:
            return False
            
        a = ((y2 - y3)*(x - x3) + (x3 - x2)*(y - y3)) / denominator
        b = ((y3 - y1)*(x - x3) + (x1 - x3)*(y - y3)) / denominator
        c = 1 - a - b
        
        return 0 <= a <= 1 and 0 <= b <= 1 and 0 <= c <= 1

    def draw_static_stars(self):
        """Отрисовка статичных звезд"""
        # Фиксированный набор звезд
        random.seed(42)  # Фиксируем seed для воспроизводимости
        for _ in range(80):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, 200)
            size = random.choice([1, 1, 1, 2])  # Большинство звезд маленькие
            brightness = random.randint(180, 255)
            color = (brightness, brightness, brightness)
            pygame.draw.circle(self.background_surface, color, (x, y), size)
        random.seed()  # Сбрасываем seed

    def create_clouds(self):
        """Создание ретро-облаков (только позиции, отрисовка каждый кадр)"""
        for _ in range(6):
            cloud = {
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(60, 160),
                'width': random.randint(80, 150),
                'height': random.randint(25, 40),
                'speed': random.uniform(0.5, 1.2),
                'color': (255, 255, 255)
            }
            self.clouds.append(cloud)

    def draw_sun(self, screen):
        """Отрисовка солнца с эффектом свечения"""
        # Эффект свечения (статичный)
        for i in range(5, 0, -1):
            glow_radius = self.sun_radius + i * 5
            alpha = 50 - i * 10
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*self.sun_color, alpha), 
                             (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surface, 
                       (self.sun_x - glow_radius, self.sun_y - glow_radius))
        
        # Основной круг солнца
        pygame.draw.circle(screen, self.sun_color, 
                         (self.sun_x, self.sun_y), self.sun_radius)
        
        # Простой эффект лучей
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            x1 = self.sun_x + (self.sun_radius + 5) * math.cos(rad)
            y1 = self.sun_y + (self.sun_radius + 5) * math.sin(rad)
            x2 = self.sun_x + (self.sun_radius + 15) * math.cos(rad)
            y2 = self.sun_y + (self.sun_radius + 15) * math.sin(rad)
            pygame.draw.line(screen, self.sun_color, (x1, y1), (x2, y2), 3)

    def draw_clouds_dynamic(self, screen):
        """Отрисовка и анимация облаков"""
        for cloud in self.clouds:
            # Перемещение облаков
            cloud['x'] -= cloud['speed']
            if cloud['x'] < -cloud['width']:
                cloud['x'] = SCREEN_WIDTH + random.randint(50, 100)
                cloud['y'] = random.randint(60, 160)
            
            # Рисуем облако как эллипс с мягкими краями
            cloud_surface = pygame.Surface((cloud['width'], cloud['height']), pygame.SRCALPHA)
            
            # Основная часть облака
            pygame.draw.ellipse(cloud_surface, (*cloud['color'], 200), 
                              (0, 0, cloud['width'], cloud['height']))
            
            # Мягкие края
            pygame.draw.ellipse(cloud_surface, (*cloud['color'], 150), 
                              (5, 5, cloud['width'] - 10, cloud['height'] - 10))
            
            screen.blit(cloud_surface, (cloud['x'], cloud['y']))

    def draw(self, screen):
        """Отрисовка всего фона"""
        # Статический фон
        screen.blit(self.background_surface, (0, 0))
        
        # Динамические элементы
        self.draw_sun(screen)
        self.draw_clouds_dynamic(screen)

class Dinosaur:
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def update(self, userInput):
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        if userInput[pygame.K_UP] and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif userInput[pygame.K_DOWN] and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or userInput[pygame.K_DOWN]):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < - self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))

class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))

class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)

class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325

class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 300

class Bird(Obstacle):
    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = 250
        self.index = 0

    def draw(self, SCREEN):
        if self.index >= 9:
            self.index = 0
        SCREEN.blit(self.image[self.index//5], self.rect)
        self.index += 1

def main():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles
    run = True
    clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud()
    background = RetroSunsetBackground()  # Используем новый фон
    game_speed = 20
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    font = pygame.font.Font('freesansbold.ttf', 20)
    obstacles = []
    death_count = 0

    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1

        text = font.render("Points: " + str(points), True, (255, 255, 255))
        textRect = text.get_rect()
        textRect.center = (1000, 40)
        SCREEN.blit(text, textRect)

    def draw_track():
        """Отрисовка беговой дорожки"""
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Отрисовка фона
        background.draw(SCREEN)
        
        userInput = pygame.key.get_pressed()

        player.draw(SCREEN)
        player.update(userInput)

        if len(obstacles) == 0:
            if random.randint(0, 2) == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif random.randint(0, 2) == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            elif random.randint(0, 2) == 2:
                obstacles.append(Bird(BIRD))

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            if player.dino_rect.colliderect(obstacle.rect):
                pygame.time.delay(2000)
                death_count += 1
                menu(death_count, background)

        draw_track()

        cloud.draw(SCREEN)
        cloud.update()

        score()

        clock.tick(30)
        pygame.display.update()

def menu(death_count, background=None):
    global points
    run = True
    
    # Создаем фон для меню, если не передан
    if background is None:
        background = RetroSunsetBackground()
    
    while run:
        # Отрисовываем фон
        background.draw(SCREEN)
        
        # Затемняем фон для меню
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        SCREEN.blit(overlay, (0, 0))
        
        font = pygame.font.Font('freesansbold.ttf', 30)
        title_font = pygame.font.Font('freesansbold.ttf', 40)

        # Заголовок
        title = title_font.render("DINO RUNNER", True, (255, 204, 0))
        titleRect = title.get_rect()
        titleRect.center = (SCREEN_WIDTH // 2, 100)
        SCREEN.blit(title, titleRect)

        if death_count == 0:
            text = font.render("Press any Key to Start", True, (255, 255, 255))
        elif death_count > 0:
            text = font.render("Press any Key to Restart", True, (255, 255, 255))
            score = font.render("Your Score: " + str(points), True, (255, 204, 0))
            scoreRect = score.get_rect()
            scoreRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            SCREEN.blit(score, scoreRect)
            
            deaths = font.render("Deaths: " + str(death_count), True, (255, 150, 100))
            deathsRect = deaths.get_rect()
            deathsRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
            SCREEN.blit(deaths, deathsRect)
            
        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        SCREEN.blit(text, textRect)
        SCREEN.blit(RUNNING[0], (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 140))
        
        controls_font = pygame.font.Font('freesansbold.ttf', 16)
        controls = controls_font.render("UP = Jump | DOWN = Duck", True, (200, 200, 200))
        controlsRect = controls.get_rect()
        controlsRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        SCREEN.blit(controls, controlsRect)
        
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.KEYDOWN:
                main()

menu(death_count=0)