import pygame
import random

pygame.init()

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Catch the Falling Objects")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

player_width = 50
player_height = 10
player_speed = 5

object_width = 20
object_height = 20
object_speed = 5

def draw_text(text, font, color, surface, x, y):
    render = font.render(text, True, color)
    rect = render.get_rect(center=(x, y))
    surface.blit(render, rect)

def game_loop():
    player_x = SCREEN_WIDTH // 2
    player_y = SCREEN_HEIGHT - 40
    objects = [{'x': random.randint(0, SCREEN_WIDTH - object_width), 'y': 0}]
    score = 0
    running = True
    paused = False

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused

        if not paused:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player_x > 0:
                player_x -= player_speed
            if keys[pygame.K_RIGHT] and player_x < SCREEN_WIDTH - player_width:
                player_x += player_speed

            for obj in objects:
                obj['y'] += object_speed
                if obj['y'] > SCREEN_HEIGHT:
                    obj['y'] = 0
                    obj['x'] = random.randint(0, SCREEN_WIDTH - object_width)

                if (player_x < obj['x'] + object_width and
                    player_x + player_width > obj['x'] and
                    player_y < obj['y'] + object_height and
                    player_y + player_height > obj['y']):
                    score += 1
                    obj['y'] = 0
                    obj['x'] = random.randint(0, SCREEN_WIDTH - object_width)

            if score > 0 and score % 5 == 0 and len(objects) < 5:
                objects.append({'x': random.randint(0, SCREEN_WIDTH - object_width), 'y': 0})

        pygame.draw.rect(screen, BLUE, (player_x, player_y, player_width, player_height))
        for obj in objects:
            pygame.draw.rect(screen, RED, (obj['x'], obj['y'], object_width, object_height))

        draw_text(f"Score: {score}", font, BLACK, screen, 70, 20)
        if paused:
            draw_text("PAUSED", big_font, GREEN, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        pygame.display.update()
        clock.tick(60)

        if score >= 20:
            game_over_screen(score)
            return True

def start_screen():
    waiting = True
    while waiting:
        screen.fill(WHITE)
        draw_text("Catch the Falling Objects", big_font, BLACK, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        draw_text("Press ENTER to Start", font, BLUE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text("Press ESC to Quit", font, RED, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False

def game_over_screen(score):
    waiting = True
    while waiting:
        screen.fill(WHITE)
        draw_text("GAME OVER", big_font, RED, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        draw_text(f"Your Score: {score}", font, BLACK, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text("Press ENTER to Play Again or ESC to Quit", font, BLUE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False
                    game_loop()
                    return True
                if event.key == pygame.K_ESCAPE:
                    waiting = False
                    return False

running = start_screen()
while running:
    running = game_loop()

pygame.quit()
