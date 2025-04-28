import pygame
import time
import random
import os

# Initialize pygame
pygame.init()
pygame.font.init()
pygame.mixer.init()  # For sound effects

# Game window
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h

# Game design resolution (base resolution)
DESIGN_WIDTH, DESIGN_HEIGHT = 1000, 800

# Create fullscreen window
WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("GALAXY RIDER")


# Calculate scaling factors
scale_x = SCREEN_WIDTH / DESIGN_WIDTH
scale_y = SCREEN_HEIGHT / DESIGN_HEIGHT
scale_factor = min(scale_x, scale_y)  # Maintain aspect ratio


def load_background():
    try:
        original_bg = pygame.image.load('bgp.png').convert()
        bg_width, bg_height = original_bg.get_size()

        # Scale to cover screen while maintaining aspect ratio
        scale = max(SCREEN_WIDTH / bg_width, SCREEN_HEIGHT / bg_height)
        scaled_width = int(bg_width * scale)
        scaled_height = int(bg_height * scale)
        scaled_bg = pygame.transform.scale(original_bg, (scaled_width, scaled_height))

        # Center and crop
        crop_x = (scaled_width - SCREEN_WIDTH) // 2
        crop_y = (scaled_height - SCREEN_HEIGHT) // 2
        return scaled_bg.subsurface((crop_x, crop_y, SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        # Fallback solid color background
        bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        bg.fill((0, 0, 50))  # Dark blue
        return bg


BG = load_background()


# Load images with scaling
def load_image(name, original_size):
    scaled_size = (int(original_size[0] * scale_factor),
                   int(original_size[1] * scale_factor))
    try:
        img = pygame.image.load(os.path.join('assets', name)).convert_alpha()
        return pygame.transform.scale(img, scaled_size)
    except:
        surf = pygame.Surface(scaled_size)
        surf.fill("red" if "enemy" in name else "blue")
        return surf



player_img = pygame.image.load('spaceship.png')
# Game settings
player_width, player_height = int(120 * scale_factor), int(100 * scale_factor)
player_vel = 8
enemy_vel_min = int(3 * scale_factor)
enemy_vel_max = int(7 * scale_factor)
font = pygame.font.SysFont("comicsans", 30)
score = 0
lives = 1
#player image
player_img= pygame.transform.scale(player_img,(player_width,player_height))
enemy_img =  pygame.image.load('enemy_spaceship2.png')
explosion_img =  pygame.image.load('explosion.png')# Optional explosion effect



# Sound effects
try:
    explosion_sound = pygame.mixer.Sound('explosion.wav')
    engine_sound = pygame.mixer.Sound('engine.wav')
    engine_sound.play(-1)  # Loop engine sound
except:
    pass  # Continue without sound if files missing


class Enemy:
    def __init__(self):
        self.width = random.randint(int(50 * scale_factor), int(100 * scale_factor))
        self.height = random.randint(int(40 * scale_factor), int(80 * scale_factor))
        self.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.y = -self.height
        self.vel = random.randint(enemy_vel_min, enemy_vel_max)
        self.img = pygame.transform.scale(enemy_img, (self.width, self.height))
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.y += self.vel
        self.rect.y = self.y

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))


def draw(player, elapsed_time, enemies, explosions):
    WIN.blit(BG, (0, 0))

    # Draw UI
    time_text = font.render(f"TIME: {round(elapsed_time)}s", 1, "white")
    score_text = font.render(f"SCORE: {score}", 1, "white")
    lives_text = font.render(f"LIVES: {lives}", 1, "white")

    WIN.blit(time_text, (10, 10))
    WIN.blit(score_text, (10, 50))
    WIN.blit(lives_text, (10, 90))

    # Draw player
    WIN.blit(player_img, (player.x, player.y))

    # Draw enemies
    for enemy in enemies:
        enemy.draw(WIN)

    # Draw explosions
    for explosion in explosions:
        WIN.blit(explosion_img, (explosion[0], explosion[1]))

    pygame.display.update()


def main():
    global score, lives

    run = True
    player = pygame.Rect(SCREEN_WIDTH // 2 - player_width // 2, SCREEN_HEIGHT - player_height - 20,
                         player_width, player_height)

    clock = pygame.time.Clock()
    start_time = time.time()
    elapsed_time = 0

    # Game objects
    enemies = []
    explosions = []
    enemy_spawn_timer = 0
    enemy_spawn_delay = 60  # frames

    while run:
        clock.tick(60)
        elapsed_time = time.time() - start_time
        enemy_spawn_timer += 1

        # Spawn enemies
        if enemy_spawn_timer >= enemy_spawn_delay:
            enemies.append(Enemy())
            enemy_spawn_timer = 0
            # Increase difficulty over time
            enemy_spawn_delay = max(10, 40 - int(elapsed_time))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel >= 0:
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_width <= SCREEN_WIDTH:
            player.x += player_vel

        # Update enemies and check collisions
        for enemy in enemies[:]:
            enemy.update()

            if enemy.y > SCREEN_HEIGHT:
                enemies.remove(enemy)
                score += 1
            elif enemy.rect.colliderect(player):
                try:
                    explosion_sound.play()
                except:
                    pass
                explosions.append((enemy.x, enemy.y))
                enemies.remove(enemy)
                lives -= 1
                if lives <= 0:
                    run = False

        # Update explosions (remove after 5 frames)
        if len(explosions) > 0 and pygame.time.get_ticks() % 5 == 0:
            explosions.pop(0)

        draw(player, elapsed_time, enemies, explosions)

    # Game over screen
    game_over_text = font.render(f"GAME OVER! Final Score: {score}", 1, "white")
    WIN.blit(game_over_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2))
    pygame.display.update()
    pygame.time.delay(3000)  # Show for 3 seconds

    pygame.quit()


if __name__ == "__main__":
    main()