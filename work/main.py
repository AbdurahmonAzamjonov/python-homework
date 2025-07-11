import pygame
import sys
import random
from game_objects import Paddle, Ball, Brick, PowerUp, Laser, Particle, Firework

# -- General Setup --
pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()

# -- Screen Setup --
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
game_font = pygame.font.Font(None, 40)

POWERUP_CHANCE = .9
is_muted = False
level = 1

# We can set a caption for the window to give our game a title.
pygame.display.set_caption("PyGame Arkanoid")

# -- Load Sound --
try:
    bounce_sound = pygame.mixer.Sound('work/bounce.wav')
    brick_break_sound = pygame.mixer.Sound('work/brick_break.wav')
    game_over_sound = pygame.mixer.Sound('work/game_over.wav')
    laser_sound = pygame.mixer.Sound('phase_9/laser.wav')
except pygame.error as e:
    print(f"Sound file not found: {e}")

# -- Game Objects --
paddle = Paddle(screen_width, screen_height)
ball = Ball(screen_width, screen_height)

# -- Game Vars -- 
game_state = 'title'  # 'title', 'playing', 'game_over', 'you_win'
score = 0
lives = 3
firework_timer = 0

# -- Bricks --
def create_brick_wall(level=1):
    bricks = []
    brick_rows = 4 + level
    brick_cols = 10
    brick_width = 75
    brick_height = 20
    brick_padding = 5
    wall_start_y = 50
    BRICK_COLORS = [(178, 34, 34), (255, 165, 0), (255, 215, 0), (50, 205, 50), (100, 149, 237)]

    # Fill the bricks wall
    for row in range(brick_rows):
        for col in range(brick_cols):
            x = col * (brick_width + brick_padding) + brick_padding
            y = row * (brick_height + brick_padding) + wall_start_y
            color = BRICK_COLORS[row % len(BRICK_COLORS)]
            brick = Brick(x, y, brick_width, brick_height, color)
            bricks.append(brick)

    return bricks

bricks = create_brick_wall(level)

# -- Game objects --
power_ups = []
lasers = []
particles = []
fireworks = []

# -- Main Game Loop --
while True:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # -- Restarts and Controls --
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                is_muted = not is_muted

            if event.key == pygame.K_SPACE:
                if game_state in ['title', 'game_over', 'you_win']:
                    ball.reset()
                    paddle.reset()
                    bricks = create_brick_wall(level)
                    score = 0
                    lives = 3
                    game_state = 'playing'
                    power_ups.clear()
                    lasers.clear()
                    particles.clear()
                    fireworks.clear()

                if ball.is_glued:
                    ball.is_glued = False

                if paddle.has_laser:
                    laser_left = Laser(paddle.rect.centerx - 30, paddle.rect.top)
                    laser_right = Laser(paddle.rect.centerx + 30, paddle.rect.top)
                    lasers.append(laser_left)
                    lasers.append(laser_right)
                    if not is_muted:
                        laser_sound.play()

    # -- Game Objects Update --
    if game_state == 'playing':
        paddle.update()
        keys = pygame.key.get_pressed()
        ball_status, collision_object = ball.update(paddle, keys[pygame.K_SPACE])

        if collision_object in ['wall', 'paddle']:
            for _ in range(5):
                particle = Particle(ball.rect.centerx, ball.rect.centery, (255, 255, 0), 1, 3, 1, 3, 0)
                particles.append(particle)

        if ball_status == 'Lost':
            lives -= 1
            if lives <= 0:
                game_state = 'game_over'
                if not is_muted:
                    game_over_sound.play()
            else:
                ball.reset()

        # Check brick collision
        for brick in bricks[:]:
            if ball.rect.colliderect(brick.rect):
                ball.speed_y *= -1
                bricks.remove(brick)
                score += 10
                if not is_muted:
                    brick_break_sound.play()
                for _ in range(5):
                    particle = Particle(brick.rect.centerx, brick.rect.centery, (255, 255, 0), 1, 4, 1, 4, 0.05)
                    particles.append(particle)
                if random.random() < POWERUP_CHANCE:
                    powerup_type = random.choice(['grow', 'laser', 'glue', 'slow', 'shrink', 'speed'])
                    powerup = PowerUp(brick.rect.centerx, brick.rect.centery, powerup_type)
                    power_ups.append(powerup)
                break

        # Check if all bricks are gone
        if not bricks:
            level += 1
            bricks = create_brick_wall(level)
            ball.reset()
            paddle.reset()
            power_ups.clear()
            lasers.clear()
            particles.clear()

        # Update PowerUps
        for powerup in power_ups[:]:
            powerup.update()
            if paddle.rect.colliderect(powerup.rect):
                paddle.activate_powerup(powerup.type)
                ball.activate_powerup(powerup.type)
                power_ups.remove(powerup)
            elif powerup.rect.top > screen_height:
                power_ups.remove(powerup)

        # Update lasers
        for laser in lasers[:]:
            laser.update()
            if laser.rect.bottom < 0:
                lasers.remove(laser)
            else:
                for brick in bricks[:]:
                    if laser.rect.colliderect(brick.rect):
                        lasers.remove(laser)
                        bricks.remove(brick)
                        score += 10
                        if not is_muted:
                            brick_break_sound.play()
                        for _ in range(5):
                            particle = Particle(brick.rect.centerx, brick.rect.centery, (255, 255, 0), 1, 4, 1, 4, 0.05)
                            particles.append(particle)
                        break

    # Update particles
    for particle in particles[:]:
        particle.update()
        if particle.size <= 0:
            particles.remove(particle)

    # --- Drawing ---
    screen.fill((0, 0, 0))
    paddle.draw(screen)
    ball.draw(screen)

    for brick in bricks:
        brick.draw(screen)

    for powerup in power_ups:
        powerup.draw(screen)

    for laser in lasers:
        laser.draw(screen)

    for particle in particles:
        particle.draw(screen)

    # -- Game Screen --
    score_text = game_font.render(f"Score: {score}", True, (255, 255, 255))
    lives_text = game_font.render(f"Lives: {lives}", True, (255, 255, 255))
    level_text = game_font.render(f"Level: {level}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (screen_width - lives_text.get_width() - 10, 10))
    screen.blit(level_text, (screen_width // 2 - level_text.get_width() // 2, 10))

    # -- Game States -- 
    if game_state == 'title':
        title_surface = game_font.render("PYGAME ARKANOID", True, (255, 255, 255))
        screen.blit(title_surface, title_surface.get_rect(center=(screen_width // 2, screen_height // 2 - 50)))
        prompt_surface = game_font.render("Press SPACE to Start", True, (255, 255, 255))
        screen.blit(prompt_surface, prompt_surface.get_rect(center=(screen_width // 2, screen_height // 2)))

    elif game_state == 'game_over':
        text_surface = game_font.render('Game Over :(', True, (255, 255, 255))
        screen.blit(text_surface, text_surface.get_rect(center=(screen_width // 2, screen_height // 2 - 30)))
        if (pygame.time.get_ticks() // 500) % 2:
            text_surface = game_font.render('Press SPACE to Restart', True, (255, 255, 255))
            screen.blit(text_surface, text_surface.get_rect(center=(screen_width // 2, screen_height // 2 + 20)))

    elif game_state == 'you_win':
        text_surface = game_font.render('You Win :)', True, (255, 255, 255))
        screen.blit(text_surface, text_surface.get_rect(center=(screen_width // 2, screen_height // 2 - 30)))
        text_surface = game_font.render('Press SPACE to Restart', True, (255, 255, 255))
        screen.blit(text_surface, text_surface.get_rect(center=(screen_width // 2, screen_height // 2 + 20)))
        firework_timer -= 1
        if firework_timer <= 0:
            fireworks.append(Firework(screen_width, screen_height))
            firework_timer = random.randint(20, 50)
        for firework in fireworks[:]:
            firework.update()
            if firework.is_dead():
                fireworks.remove(firework)
            else:
                firework.draw(screen)

    # --- Updating the Display ---
    pygame.display.flip()

    # --- Frame Rate Control ---
    clock.tick(60)


