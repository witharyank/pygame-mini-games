import random
import pygame


pygame.init()

# =====================
# CONFIG / CONSTANTS
# =====================
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400

FPS = 60
PLAYER_SPEED = 5
OBJECT_SPEED = 5
MAX_OBJECTS = 5
WIN_SCORE = 20

PLAYER_WIDTH = 50
PLAYER_HEIGHT = 10

OBJECT_WIDTH = 20
OBJECT_HEIGHT = 20

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# =====================
# SETUP
# =====================
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Catch the Falling Objects")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)


# =====================
# TEXT RENDER
# =====================
def draw_text(text, font, color, surface, x, y):
    render = font.render(text, True, color)
    rect = render.get_rect(center=(x, y))
    surface.blit(render, rect)


# =====================
# MAIN GAME LOOP
# =====================
def game_loop():
    player_x = SCREEN_WIDTH // 2
    player_y = SCREEN_HEIGHT - 40

    falling_objects = [
        {"x": random.randint(0, SCREEN_WIDTH - OBJECT_WIDTH), "y": 0}
    ]

    score = 0
    paused = False
    running = True

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
                player_x -= PLAYER_SPEED

            if keys[pygame.K_RIGHT] and player_x < SCREEN_WIDTH - PLAYER_WIDTH:
                player_x += PLAYER_SPEED

            # Move falling objects
            for obj in falling_objects:
                obj["y"] += OBJECT_SPEED

                if obj["y"] > SCREEN_HEIGHT:
                    obj["y"] = 0
                    obj["x"] = random.randint(0, SCREEN_WIDTH - OBJECT_WIDTH)

                # Collision check
                if (
                    player_x < obj["x"] + OBJECT_WIDTH
                    and player_x + PLAYER_WIDTH > obj["x"]
                    and player_y < obj["y"] + OBJECT_HEIGHT
                    and player_y + PLAYER_HEIGHT > obj["y"]
                ):
                    score += 1
                    obj["y"] = 0
                    obj["x"] = random.randint(0, SCREEN_WIDTH - OBJECT_WIDTH)

            # Increase difficulty
            if score > 0 and score % 5 == 0 and len(falling_objects) < MAX_OBJECTS:
                falling_objects.append(
                    {"x": random.randint(0, SCREEN_WIDTH - OBJECT_WIDTH), "y": 0}
                )

        # Draw player
        pygame.draw.rect(
            screen,
            BLUE,
            (player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT)
        )

        # Draw objects
        for obj in falling_objects:
            pygame.draw.rect(
                screen,
                RED,
                (obj["x"], obj["y"], OBJECT_WIDTH, OBJECT_HEIGHT)
            )

        # UI
        draw_text(f"Score: {score}", font, BLACK, screen, 70, 20)

        if paused:
            draw_text("PAUSED", big_font, GREEN, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        pygame.display.update()
        clock.tick(FPS)

        if score >= WIN_SCORE:
            game_over_screen(score)
            return True


# =====================
# START SCREEN
# =====================
def start_screen():
    while True:
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
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False


# =====================
# GAME OVER SCREEN
# =====================
def game_over_screen(score):
    while True:
        screen.fill(WHITE)
        draw_text("GAME OVER", big_font, RED, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        draw_text(f"Your Score: {score}", font, BLACK, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text(
            "Press ENTER to Play Again or ESC to Quit",
            font,
            BLUE,
            screen,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 40,
        )

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_loop()
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False


# =====================
# ENTRY POINT
# =====================
running = start_screen()
while running:
    running = game_loop()

pygame.quit()
