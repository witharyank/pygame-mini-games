import random
import pygame


pygame.init()

# ==================================================
# SCREEN SETTINGS
# ==================================================
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
FPS = 60

# ==================================================
# PLAYER SETTINGS
# ==================================================
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 10
PLAYER_SPEED = 5

# ==================================================
# FALLING OBJECT SETTINGS
# ==================================================
OBJECT_WIDTH = 20
OBJECT_HEIGHT = 20
OBJECT_SPEED = 5
MAX_OBJECTS = 5

# ==================================================
# GAME RULES
# ==================================================
WIN_SCORE = 20

# ==================================================
# COLORS
# ==================================================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)
GREEN = (0, 255, 0)

# ==================================================
# PYGAME SETUP
# ==================================================
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Catch the Falling Objects")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)


# ==================================================
# HELPER FUNCTIONS
# ==================================================
def draw_text(text, font, color, surface, x, y):
    """Render and draw centered text on screen."""
    render = font.render(text, True, color)
    rect = render.get_rect(center=(x, y))
    surface.blit(render, rect)


# ==================================================
# MAIN GAME LOOP
# ==================================================
def game_loop():
    """Runs the main gameplay loop."""
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

        # ------------------
        # EVENT HANDLING
        # ------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused

        # ------------------
        # GAME LOGIC
        # ------------------
        if not paused:
            keys = pygame.key.get_pressed()

            if keys[pygame.K_LEFT] and player_x > 0:
                player_x -= PLAYER_SPEED

            if keys[pygame.K_RIGHT] and player_x < SCREEN_WIDTH - PLAYER_WIDTH:
                player_x += PLAYER_SPEED

            # Move falling objects
            for obj in falling_objects:
                obj["y"] += OBJECT_SPEED

                # Reset object if it goes off screen
                if obj["y"] > SCREEN_HEIGHT:
                    obj["y"] = 0
                    obj["x"] = random.randint(0, SCREEN_WIDTH - OBJECT_WIDTH)

                # Collision detection
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

        # ------------------
        # DRAWING
        # ------------------
        pygame.draw.rect(
            screen,
            BLUE,
            (player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT)
        )

        for obj in falling_objects:
            pygame.draw.rect(
                screen,
                RED,
                (obj["x"], obj["y"], OBJECT_WIDTH, OBJECT_HEIGHT)
            )

        # UI
        draw_text(f"Score: {score}", font, BLACK, screen, 70, 20)

        if paused:
            draw_text(
                "PAUSED",
                big_font,
                GREEN,
                screen,
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2
            )

        pygame.display.update()
        clock.tick(FPS)

        # Win condition
        if score >= WIN_SCORE:
            game_over_screen(score)
            return True


# ==================================================
# START SCREEN
# ==================================================
def start_screen():
    """Displays the start menu."""
    while True:
        screen.fill(WHITE)

        draw_text(
            "Catch the Falling Objects",
            big_font,
            BLACK,
            screen,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 3
        )

        draw_text(
            "Press ENTER to Start",
            font,
            BLUE,
            screen,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2
        )

        draw_text(
            "Press ESC to Quit",
            font,
            RED,
            screen,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 40
        )

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False


# ==================================================
# GAME OVER SCREEN
# ==================================================
def game_over_screen(score):
    """Displays the game over screen."""
    while True:
        screen.fill(WHITE)

        draw_text(
            "GAME OVER",
            big_font,
            RED,
            screen,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 3
        )

        draw_text(
            f"Your Score: {score}",
            font,
            BLACK,
            screen,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2
        )

        draw_text(
            "Press ENTER to Play Again or ESC to Quit",
            font,
            BLUE,
            screen,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 40
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


# ==================================================
# ENTRY POINT
# ==================================================
running = start_screen()
while running:
    running = game_loop()

pygame.quit()