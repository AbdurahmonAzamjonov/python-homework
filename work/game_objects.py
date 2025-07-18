import pygame
import random
import math

pygame.font.init()
POWERUP_FONT = pygame.font.Font(None, 20)

class Paddle:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.width = 100
        self.height = 10
        self.speed = 7
        self.color = (200, 200, 200)
        self.original_width = self.width
        self.rect = pygame.Rect(self.screen_width // 2 - self.width // 2, self.screen_height - 30, self.width, self.height)
        self.reset()

    def reset(self):
        self.rect.x = self.screen_width // 2 - self.width // 2
        self.width = self.original_width
        self.rect.width = self.width
        self.power_up_timers = {
            'grow': 0,
            'laser': 0,
            'glue': 0,
            'shrink': 0
        }
        self.has_laser = False
        self.has_glue = False

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.screen_width:
            self.rect.right = self.screen_width

        self._update_powerups()

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def activate_powerup(self, type):
        DURATION = 600
        if type == 'grow':
            self.width = 150
            self.rect.width = self.width
            self.power_up_timers['grow'] = DURATION
        elif type == 'shrink':
            self.width = 60
            self.rect.width = self.width
            self.power_up_timers['shrink'] = DURATION
        elif type == 'laser':
            self.has_laser = True
            self.power_up_timers['laser'] = DURATION
        elif type == 'glue':
            self.has_glue = True
            self.power_up_timers['glue'] = DURATION

    def _update_powerups(self):
        if self.power_up_timers['grow'] > 0:
            self.power_up_timers['grow'] -= 1
            if self.power_up_timers['grow'] <= 0:
                self.width = self.original_width
                self.rect.width = self.width

        if self.power_up_timers['shrink'] > 0:
            self.power_up_timers['shrink'] -= 1
            if self.power_up_timers['shrink'] <= 0:
                self.width = self.original_width
                self.rect.width = self.width

        if self.power_up_timers['laser'] > 0:
            self.power_up_timers['laser'] -= 1
            if self.power_up_timers['laser'] <= 0:
                self.has_laser = False

        if self.power_up_timers['glue'] > 0:
            self.power_up_timers['glue'] -= 1
            if self.power_up_timers['glue'] <= 0:
                self.has_glue = False

class Ball:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.radius = 10
        self.color = (200, 200, 200)
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.is_glued = False
        self.is_slowed = False
        self.base_speed = 6
        self.slow_timer = 0
        self.fast_timer = 0
        self.reset()

    def reset(self):
        self.rect.center = (self.screen_width // 2, self.screen_height // 2)
        self.speed_x = self.base_speed * random.choice((1, -1))
        self.speed_y = -self.base_speed
        self.is_glued = False
        self.is_slowed = False
        self.slow_timer = 0
        self.fast_timer = 0

    def update(self, paddle, launch_ball=False):
        collision_object = 'air'

        if self.is_glued:
            self.rect.centerx = paddle.rect.centerx
            self.rect.bottom = paddle.rect.top
            if launch_ball:
                self.is_glued = False
                self.speed_x = self.base_speed * random.choice((1, -1))
                self.speed_y = -self.base_speed

        if self.is_slowed:
            self.slow_timer -= 1
            if self.slow_timer <= 0:
                self.speed_x *= 2
                self.speed_y *= 2
                self.is_slowed = False

        if self.fast_timer > 0:
            self.fast_timer -= 1
            if self.fast_timer <= 0:
                self.speed_x /= 2
                self.speed_y /= 2

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.top <= 0:
            self.speed_y *= -1
            collision_object = 'wall'
        if self.rect.left <= 0 or self.rect.right >= self.screen_width:
            self.speed_x *= -1
            collision_object = 'wall'

        if self.rect.colliderect(paddle.rect):
            if self.speed_y > 0:
                self.speed_y *= -1
                if paddle.has_glue:
                    self.is_glued = True
                collision_object = 'paddle'

        if self.rect.top > self.screen_height:
            return "Lost", collision_object

        return 'playing', collision_object

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)

    def activate_powerup(self, type):
        if type == 'slow' and not self.is_slowed:
            self.speed_x /= 2
            self.speed_y /= 2
            self.is_slowed = True
            self.slow_timer = 600
        elif type == 'speed' and self.fast_timer == 0:
            self.speed_x *= 2
            self.speed_y *= 2
            self.fast_timer = 600

class Brick:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class PowerUp:
    PROPERTIES = {
        'grow': {'color': (60, 60, 255), 'char': 'G'},
        'laser': {'color': (255, 60, 60), 'char': 'L'},
        'glue': {'color': (60, 255, 60), 'char': 'C'},
        'slow': {'color': (255, 165, 0), 'char': 'S'},
        'shrink': {'color': (128, 0, 128), 'char': 'K'},
        'speed': {'color': (255, 255, 0), 'char': 'F'},
    }

    def __init__(self, x, y, type):
        self.width = 30
        self.height = 15
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.speed_y = 3
        self.type = type
        self.color = self.PROPERTIES[type]['color']
        self.char = self.PROPERTIES[type]['char']

    def update(self):
        self.rect.y += self.speed_y

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surf = POWERUP_FONT.render(self.char, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

class Laser:
    def __init__(self, x, y):
        self.width = 5
        self.height = 15
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.color = (255, 255, 0)
        self.speed_y = -8

    def update(self):
        self.rect.y += self.speed_y

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class Particle:
    def __init__(self, x, y, color, min_size, max_size, min_speed, max_speed, gravity):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(min_size, max_size)
        self.gravity = gravity
        angle = random.uniform(0, 360)
        self.speed = random.uniform(min_speed, max_speed)
        self.vx = self.speed * math.cos(math.radians(angle))
        self.vy = self.speed * math.sin(math.radians(angle))

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.size -= .1

    def draw(self, screen):
        if self.size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

class Firework:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = random.randint(0, screen_width)
        self.y = screen_height
        self.vy = -random.uniform(8, 12)
        self.color = (255, 255, 255)
        self.exploded = False
        self.particles = []
        self.explosion_y = random.uniform(screen_height * .2, screen_height * .5)

    def update(self):
        if not self.exploded:
            self.y += self.vy
            if self.y <= self.explosion_y:
                self.exploded = True
                explosion_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                for _ in range(50):
                    particle = Particle(self.x, self.y, explosion_color, 2, 4, 1, 4, .1)
                    self.particles.append(particle)
        else:
            for particle in self.particles[:]:
                particle.update()
                if particle.size <= 0:
                    self.particles.remove(particle)

    def draw(self, screen):
        if not self.exploded:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 3)
        else:
            for particle in self.particles:
                particle.draw(screen)

    def is_dead(self):
        return self.exploded and not self.particles
