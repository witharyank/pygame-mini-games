import os
import sys
import random
import pygame


pygame.init()
WIDTH, HEIGHT = 500, 700
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Racer Turbo - Powerup Boosted")

clock = pygame.time.Clock()

WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
YELLOW = (255, 200, 0)
BLUE = (0, 150, 255)
ORANGE = (255, 140, 0)

base = os.path.dirname(__file__)

def load_image(name, size):
    path = os.path.join(base, name)
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    s = pygame.Surface(size, pygame.SRCALPHA)
    s.fill((180, 180, 180))
    return s

player_img = load_image("player_car.png.webp", (60, 120))
enemy_img = load_image("enemy.png.webp", (60, 120)) 
fuel_img = load_image("fuel.jpg", (40, 40))
boost_img = load_image("boost.png", (40, 40))  # optional

# Simple road background (you can replace with an image)
road_img = pygame.Surface((WIDTH, HEIGHT))
road_img.fill((30, 30, 30))
# draw lane marks
for y in range(-1000, 1000, 100):
    pygame.draw.rect(road_img, (200, 200, 200), (WIDTH//2 - 5, y, 10, 60))

# High score file
SCORE_FILE = os.path.join(base, "highscore.txt")
if not os.path.exists(SCORE_FILE):
    with open(SCORE_FILE, "w") as f:
        f.write("0")

def get_high_score():
    try:
        with open(SCORE_FILE, "r") as f:
            return int(f.read().strip())
    except Exception:
        return 0

def save_high_score(score):
    current = get_high_score()
    if score > current:
        with open(SCORE_FILE, "w") as f:
            f.write(str(score))

# --- Game classes ---
class Player:
    def __init__(self):
        self.image = player_img
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT-140))
        self.base_speed = 7
        self.boost_speed = 12    # when holding SPACE
        self.power_speed = 16    # when power-up active
        self.speed = self.base_speed
        self.boost = False
        self.powered = False
        self.power_time = 0
        self.power_duration = 5000  # ms
        self.invincible = False

    def move(self, keys):
        # determine current speed
        if self.powered:
            # while powered, override SPACE boost and use power_speed
            self.speed = self.power_speed
        else:
            if keys[pygame.K_SPACE]:
                self.boost = True
                self.speed = self.boost_speed
            else:
                self.boost = False
                self.speed = self.base_speed

        # horizontal movement
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def update(self):
        # check power-up timeout
        if self.powered:
            now = pygame.time.get_ticks()
            if now - self.power_time >= self.power_duration:
                self.powered = False
                self.invincible = False
#future update
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # draw visual effect when powered: a glow + flame
        if self.powered:
            # glow
            glow_rect = pygame.Rect(self.rect.left-6, self.rect.top-6, self.rect.width+12, self.rect.height+12)
            s = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            s.fill((0,0,0,0))
            pygame.draw.ellipse(s, (255,180,50,90), (0, glow_rect.height//2, glow_rect.width, glow_rect.height//2))
            surface.blit(s, (glow_rect.left, glow_rect.top))
            # flame behind car
            flame_points = [
                (self.rect.centerx, self.rect.bottom),
                (self.rect.centerx - 10, self.rect.bottom + 30),
                (self.rect.centerx + 10, self.rect.bottom + 30),
            ]
            pygame.draw.polygon(surface, ORANGE, flame_points)

class Enemy:
    def __init__(self):
        self.image = enemy_img
        self.rect = self.image.get_rect(center=(random.randint(60, WIDTH-60), -random.randint(120, 800)))
        self.base_speed = random.randint(5, 8)
        self.speed = self.base_speed
    def move(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            # respawn above
            self.rect.center = (random.randint(60, WIDTH-60), -random.randint(120, 400))
            self.base_speed = random.randint(5, 8)
            self.speed = self.base_speed
            return True
        return False
    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Fuel:
    def __init__(self):
        self.image = fuel_img
        self.rect = self.image.get_rect(center=(random.randint(60, WIDTH-60), -random.randint(120, 800)))
        self.speed = 6
    def move(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.center = (random.randint(60, WIDTH-60), -random.randint(120, 800))
    def draw(self, surface):
        surface.blit(self.image, self.rect)

class PowerUp:
    def __init__(self):
        self.image = boost_img
        self.rect = self.image.get_rect(center=(random.randint(60, WIDTH-60), -random.randint(600, 1200)))
        self.speed = 5
        self.active = True
        self.collected_time = None
        self.respawn_delay = 7000  # ms before it appears again after collect

    def move(self):
        if not self.active:
            # waiting to respawn
            if pygame.time.get_ticks() - self.collected_time >= self.respawn_delay:
                self.active = True
                self.rect.center = (random.randint(60, WIDTH-60), -random.randint(200, 800))
            return
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            # move it back up
            self.rect.center = (random.randint(60, WIDTH-60), -random.randint(200, 800))

    def draw(self, surface):
        if self.active:
            surface.blit(self.image, self.rect)
            # small pulse (circle)
            r = 6 + int((pygame.time.get_ticks() // 200) % 6)
            pygame.draw.circle(surface, BLUE, (self.rect.centerx, self.rect.top + 10), r, 1)

    def collect(self):
        self.active = False
        self.collected_time = pygame.time.get_ticks()
        # move off-screen
        self.rect.center = (-100, -100)

# --- UI helpers ---
def draw_text(surface, text, size, color, x, y, center=True):
    f = pygame.font.SysFont("Arial", size, bold=True)
    t = f.render(text, True, color)
    if center:
        r = t.get_rect(center=(x, y))
    else:
        r = t.get_rect(topleft=(x, y))
    surface.blit(t, r)

def pause_game():
    paused = True
    while paused:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_p:
                paused = False
        draw_text(win, "PAUSED", 60, RED, WIDTH//2, HEIGHT//2 - 20)
        draw_text(win, "Press P to Resume", 30, WHITE, WIDTH//2, HEIGHT//2 + 40)
        pygame.display.update()
        clock.tick(10)

def game_over_screen(score):
    save_high_score(score)
    high = get_high_score()
    win.fill(GRAY)
    draw_text(win, "GAME OVER", 70, RED, WIDTH//2, HEIGHT//2 - 70)
    draw_text(win, f"Score: {score}", 40, WHITE, WIDTH//2, HEIGHT//2)
    draw_text(win, f"High Score: {high}", 35, YELLOW, WIDTH//2, HEIGHT//2 + 50)
    draw_text(win, "Press R to Restart or Q to Quit", 25, WHITE, WIDTH//2, HEIGHT//2 + 110)
    pygame.display.update()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    main_game()
                elif e.key == pygame.K_q:
                    pygame.quit(); sys.exit()

def draw_fuel_bar(surface, fuel):
    bar_width = 200
    bar_height = 20
    x, y = 20, 60
    pygame.draw.rect(surface, WHITE, (x-2, y-2, bar_width+4, bar_height+4))
    inner_width = max(0, int(bar_width * (fuel / 100)))
    color = GREEN if fuel > 40 else YELLOW if fuel > 20 else RED
    pygame.draw.rect(surface, color, (x, y, inner_width, bar_height))

def draw_background(surface, offset):
    y = offset % HEIGHT
    surface.blit(road_img, (0, y - HEIGHT))
    surface.blit(road_img, (0, y))

# --- Main game ---
def main_game():
    player = Player()
    enemies = [Enemy() for _ in range(3)]
    fuel_can = Fuel()
    powerup = PowerUp()
    score = 0
    fuel = 100.0
    bg_offset = 0
    running = True
    high = get_high_score()

    while running:
        dt = clock.tick(60)
        bg_offset += 8

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_p:
                pause_game()

        keys = pygame.key.get_pressed()
        player.move(keys)
        player.update()

        # background
        draw_background(win, bg_offset)

        # enemies
        for enemy in enemies:
            if enemy.move():
                score += 1
            enemy.draw(win)
            # collision: only matters if player not invincible
            if player.rect.colliderect(enemy.rect) and not player.invincible:
                # if player is powered, invincible is True -> no crash
                game_over_screen(score)

        # fuel
        fuel_can.move()
        fuel_can.draw(win)
        if player.rect.colliderect(fuel_can.rect):
            fuel = min(100.0, fuel + 25.0)
            # respawn fuel
            fuel_can.rect.center = (random.randint(60, WIDTH-60), -random.randint(200, 800))

        # powerup
        powerup.move()
        powerup.draw(win)
        if powerup.active and player.rect.colliderect(powerup.rect):
            # grant power: speed boost + invincibility for duration
            player.powered = True
            player.invincible = True
            player.power_time = pygame.time.get_ticks()
            powerup.collect()

        # fuel drain (considers whether player is using SPACE boost)
        fuel -= (0.1 if not player.boost else 0.3)
        # small additional drain if powered (optional)
        if player.powered:
            fuel -= 0.05

        # clamp
        if fuel <= 0:
            game_over_screen(score)

        # draw player (with effects if powered)
        player.draw(win)

        # UI
        draw_text(win, f"Score: {score}", 30, WHITE, 80, 30)
        draw_text(win, "Fuel:", 30, WHITE, 50, 60, center=False)
        draw_fuel_bar(win, fuel)
        draw_text(win, f"High: {high}", 25, YELLOW, WIDTH - 80, 30)

        # show power-up timer bar when active
        if player.powered:
            elapsed = pygame.time.get_ticks() - player.power_time
            remaining = max(0, player.power_duration - elapsed)
            # small timer bar under center
            bar_w = 160
            bar_h = 12
            bx = WIDTH//2 - bar_w//2
            by = 100
            pygame.draw.rect(win, WHITE, (bx-2, by-2, bar_w+4, bar_h+4))
            inner = int(bar_w * (remaining / player.power_duration))
            pygame.draw.rect(win, BLUE, (bx, by, inner, bar_h))
            draw_text(win, "POWER-UP ACTIVE", 18, WHITE, WIDTH//2, by - 12)

        pygame.display.update()

if __name__ == "__main__":
    main_game()
