# =========================
# IMPORTS & INITIALIZATION
# =========================
import os
import sys
import random
import pygame

pygame.init()

# =========================
# GAME WINDOW SETTINGS
# =========================
WIDTH, HEIGHT = 500, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Racer Turbo - Powerup Boosted")

clock = pygame.time.Clock()

# =========================
# COLORS (RGB)
# =========================
WHITE  = (255, 255, 255)
GRAY   = (50, 50, 50)
RED    = (200, 0, 0)
GREEN  = (0, 200, 0)
YELLOW = (255, 200, 0)
BLUE   = (0, 150, 255)
ORANGE = (255, 140, 0)

# =========================
# FILE PATH BASE
# =========================
base = os.path.dirname(__file__)

# =========================
# IMAGE LOADER (SAFE)
# =========================
def load_image(name, size):
    """
    Loads image if exists, else returns placeholder surface
    """
    path = os.path.join(base, name)
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)

    # fallback placeholder
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill((180, 180, 180))
    return surface

# =========================
# GAME ASSETS
# =========================
player_img = load_image("player_car.png.webp", (60, 120))
enemy_img  = load_image("enemy.png.webp", (60, 120))
fuel_img   = load_image("fuel.jpg", (40, 40))
boost_img  = load_image("boost.png", (40, 40))

# =========================
# ROAD BACKGROUND
# =========================
road_img = pygame.Surface((WIDTH, HEIGHT))
road_img.fill((30, 30, 30))

# draw lane divider
for y in range(-1000, 1000, 100):
    pygame.draw.rect(road_img, (200, 200, 200), (WIDTH//2 - 5, y, 10, 60))

# =========================
# HIGH SCORE HANDLING
# =========================
SCORE_FILE = os.path.join(base, "highscore.txt")

if not os.path.exists(SCORE_FILE):
    with open(SCORE_FILE, "w") as f:
        f.write("0")

def get_high_score():
    try:
        with open(SCORE_FILE, "r") as f:
            return int(f.read())
    except:
        return 0

def save_high_score(score):
    if score > get_high_score():
        with open(SCORE_FILE, "w") as f:
            f.write(str(score))

# =========================
# PLAYER CLASS
# =========================
class Player:
    def __init__(self):
        self.image = player_img
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT-140))

        # speed settings
        self.base_speed  = 7
        self.boost_speed = 12
        self.power_speed = 16

        self.speed = self.base_speed
        self.boost = False
        self.powered = False
        self.invincible = False

        self.power_time = 0
        self.power_duration = 5000  # milliseconds

    def move(self, keys):
        """
        Handle movement and speed logic
        """
        if self.powered:
            self.speed = self.power_speed
        elif keys[pygame.K_SPACE]:
            self.boost = True
            self.speed = self.boost_speed
        else:
            self.boost = False
            self.speed = self.base_speed

        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def update(self):
        """
        Handle power-up timeout Its lagging last second have to fix
        """
        if self.powered:
            if pygame.time.get_ticks() - self.power_time >= self.power_duration:
                self.powered = False
                self.invincible = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)

        # power-up visual effect
        if self.powered:
            glow = pygame.Surface((self.rect.width+12, self.rect.height+12), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (255,180,50,90), glow.get_rect())
            surface.blit(glow, (self.rect.x-6, self.rect.y-6))

            flame = [
                (self.rect.centerx, self.rect.bottom),
                (self.rect.centerx - 10, self.rect.bottom + 30),
                (self.rect.centerx + 10, self.rect.bottom + 30),
            ]
            pygame.draw.polygon(surface, ORANGE, flame)

# =========================
# ENEMY CLASS
# =========================
class Enemy:
    def __init__(self):
        self.image = enemy_img
        self.rect = self.image.get_rect(
            center=(random.randint(60, WIDTH-60), -random.randint(120, 800))
        )
        self.speed = random.randint(5, 8)

    def move(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.center = (random.randint(60, WIDTH-60), -random.randint(200, 400))
            self.speed = random.randint(5, 8)
            return True
        return False

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# =========================
# FUEL CLASS
# =========================
class Fuel:
    def __init__(self):
        self.image = fuel_img
        self.rect = self.image.get_rect(
            center=(random.randint(60, WIDTH-60), -random.randint(120, 800))
        )
        self.speed = 6

    def move(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.center = (random.randint(60, WIDTH-60), -random.randint(200, 800))

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# =========================
# POWER-UP CLASS
# =========================
class PowerUp:
    def __init__(self):
        self.image = boost_img
        self.rect = self.image.get_rect(
            center=(random.randint(60, WIDTH-60), -random.randint(600, 1200))
        )
        self.speed = 5
        self.active = True
        self.respawn_delay = 7000
        self.collected_time = 0

    def move(self):
        if not self.active:
            if pygame.time.get_ticks() - self.collected_time >= self.respawn_delay:
                self.active = True
            return

        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.center = (random.randint(60, WIDTH-60), -random.randint(200, 800))

    def draw(self, surface):
        if self.active:
            surface.blit(self.image, self.rect)

    def collect(self):
        self.active = False
        self.collected_time = pygame.time.get_ticks()
        self.rect.center = (-100, -100)

# =========================
# UI HELPERS
# =========================
def draw_text(surface, text, size, color, x, y, center=True):
    font = pygame.font.SysFont("Arial", size, bold=True)
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect(center=(x,y)) if center else text_surface.get_rect(topleft=(x,y))
    surface.blit(text_surface, rect)

def draw_fuel_bar(surface, fuel):
    x, y = 20, 60
    width, height = 200, 20
    pygame.draw.rect(surface, WHITE, (x-2, y-2, width+4, height+4))
    inner = int(width * fuel / 100)
    color = GREEN if fuel > 40 else YELLOW if fuel > 20 else RED
    pygame.draw.rect(surface, color, (x, y, inner, height))

def draw_background(surface, offset):
    y = offset % HEIGHT
    surface.blit(road_img, (0, y-HEIGHT))
    surface.blit(road_img, (0, y))

# =========================
# MAIN GAME LOOP
# =========================
def main_game():
    player = Player()
    enemies = [Enemy() for _ in range(3)]
    fuel_can = Fuel()
    powerup = PowerUp()

    score = 0
    fuel = 100
    bg_offset = 0

    while True:
        clock.tick(60)
        bg_offset += 8

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        player.move(keys)
        player.update()

        draw_background(win, bg_offset)

        for enemy in enemies:
            if enemy.move():
                score += 1
            enemy.draw(win)
            if player.rect.colliderect(enemy.rect) and not player.invincible:
                save_high_score(score)
                return

        fuel_can.move()
        fuel_can.draw(win)
        if player.rect.colliderect(fuel_can.rect):
            fuel = min(100, fuel + 25)

        powerup.move()
        powerup.draw(win)
        if powerup.active and player.rect.colliderect(powerup.rect):
            player.powered = True
            player.invincible = True
            player.power_time = pygame.time.get_ticks()
            powerup.collect()

        fuel -= 0.1 if not player.boost else 0.3
        if fuel <= 0:
            save_high_score(score)
            return

        player.draw(win)

        draw_text(win, f"Score: {score}", 30, WHITE, 80, 30)
        draw_text(win, "Fuel:", 30, WHITE, 20, 60, center=False)
        draw_fuel_bar(win, fuel)

        pygame.display.update()

# =========================
# START GAME
# =========================
if __name__ == "__main__":
    main_game()
