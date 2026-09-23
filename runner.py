import pygame
import random
import sys
import os
import math
from array import array

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH = 800
HEIGHT = 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Infinite Runner")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
RED = (220, 50, 50)
BLUE = (50, 150, 255)
GRAY = (120, 120, 120)

# Clock to control frame rate
clock = pygame.time.Clock()
FPS = 60

# Player settings
player_width = 40
player_height = 60
player_x = 50
player_y = HEIGHT - player_height - 20  # 20 is the ground height
player_velocity_y = 0
gravity = 0.6
jump_power = -12
is_jumping = False

# Obstacle settings
obstacle_width = 30
base_obstacle_speed = 7
obstacle_speed = base_obstacle_speed
base_spawn_ms = 1300
spawn_interval_ms = base_spawn_ms
obstacles = []

# Game variables
score = 0
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 40)
game_over = False
started = False   # start screen shown until first SPACE
paused = False

# --- High score persistence ---
HIGHSCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscore.txt")

def load_highscore():
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return int(f.read().strip())
    except (OSError, ValueError):
        return 0

def save_highscore(value):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(value))
    except OSError:
        pass  # read-only dir etc: high score just won't persist

highscore = load_highscore()

# --- Synthesized sound effects (no asset files needed) ---
def _tone(freq_start, freq_end, duration_ms, volume=0.4, noise=False):
    """Build a mono 16-bit sound buffer: a frequency sweep, or noise burst."""
    sample_rate = 22050
    n = int(sample_rate * duration_ms / 1000)
    buf = array("h")
    for i in range(n):
        t = i / n
        if noise:
            s = random.uniform(-1, 1) * (1 - t)  # decaying noise
        else:
            freq = freq_start + (freq_end - freq_start) * t
            s = math.sin(2 * math.pi * freq * i / sample_rate) * (1 - t)
        buf.append(int(s * volume * 32767))
    return buf

try:
    pygame.mixer.init(frequency=22050, size=-16, channels=1)  # mono, matches _tone buffer
    jump_sound = pygame.mixer.Sound(buffer=_tone(300, 700, 150))
    crash_sound = pygame.mixer.Sound(buffer=_tone(0, 0, 300, volume=0.5, noise=True))
    sounds_on = True
except pygame.error:
    sounds_on = False  # headless / no audio device: play silently

# Timer event for spawning obstacles
SPAWN_OBSTACLE = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_OBSTACLE, spawn_interval_ms)

def reset_game():
    """Resets all variables to start a new game."""
    global player_y, player_velocity_y, is_jumping, obstacles, score
    global game_over, obstacle_speed, spawn_interval_ms
    player_y = HEIGHT - player_height - 20
    player_velocity_y = 0
    is_jumping = False
    obstacles.clear()
    score = 0
    obstacle_speed = base_obstacle_speed
    spawn_interval_ms = base_spawn_ms
    pygame.time.set_timer(SPAWN_OBSTACLE, spawn_interval_ms)
    game_over = False

def draw_centered(text, font_obj, color, y):
    surf = font_obj.render(text, True, color)
    screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))

running = True
while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not started:
                    started = True
                elif game_over:
                    reset_game()
                elif not paused and not is_jumping:
                    player_velocity_y = jump_power
                    is_jumping = True
                    if sounds_on:
                        jump_sound.play()
            if event.key == pygame.K_p and started and not game_over:
                paused = not paused

        if event.type == SPAWN_OBSTACLE and started and not game_over and not paused:
            # Randomize obstacle height to make it less predictable
            obs_height = random.randint(30, 80)
            obs_y = HEIGHT - obs_height - 20
            obstacles.append(pygame.Rect(WIDTH, obs_y, obstacle_width, obs_height))

    if started and not game_over and not paused:
        # 2. Physics & Movement
        player_velocity_y += gravity
        player_y += player_velocity_y

        # Prevent player from falling through the ground
        if player_y >= HEIGHT - player_height - 20:
            player_y = HEIGHT - player_height - 20
            is_jumping = False
            player_velocity_y = 0

        # Create a Rect for the player to handle collisions
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

        # 3. Obstacle Management
        for obs in obstacles[:]:
            obs.x -= obstacle_speed

            # Remove obstacles that go off-screen and add to score
            if obs.x + obstacle_width < 0:
                obstacles.remove(obs)
                score += 1

                # Ramp difficulty every 5 points: faster + more frequent
                if score % 5 == 0:
                    obstacle_speed += 0.5
                    spawn_interval_ms = max(500, int(spawn_interval_ms * 0.9))
                    pygame.time.set_timer(SPAWN_OBSTACLE, spawn_interval_ms)

            # Check for collision (slightly forgiving hitbox)
            if player_rect.inflate(-8, -4).colliderect(obs):
                game_over = True
                if sounds_on:
                    crash_sound.play()
                if score > highscore:
                    highscore = score
                    save_highscore(highscore)

    # 4. Rendering
    screen.fill(WHITE)

    # Draw Ground
    pygame.draw.rect(screen, GREEN, (0, HEIGHT - 20, WIDTH, 20))

    if not started:
        # Start screen
        draw_centered("PYTHON INFINITE RUNNER", big_font, BLACK, HEIGHT // 2 - 70)
        draw_centered("Press SPACE to jump over the red blocks", font, GRAY, HEIGHT // 2)
        draw_centered("Press SPACE to start - P to pause", font, GRAY, HEIGHT // 2 + 35)
        if highscore:
            draw_centered(f"High score: {highscore}", font, BLUE, HEIGHT // 2 + 70)
    elif not game_over:
        # Draw Player
        pygame.draw.rect(screen, BLUE, (player_x, player_y, player_width, player_height))

        # Draw Obstacles
        for obs in obstacles:
            pygame.draw.rect(screen, RED, obs)

        # Draw Score
        score_text = font.render(f"Score: {score}   Best: {highscore}", True, BLACK)
        screen.blit(score_text, (10, 10))
        if paused:
            draw_centered("PAUSED - press P to resume", big_font, GRAY, HEIGHT // 2 - 20)
    else:
        # Game Over Screen
        draw_centered("GAME OVER - Press SPACE to Restart", big_font, RED, HEIGHT // 2 - 40)
        draw_centered(f"Final Score: {score}   Best: {highscore}", font, BLACK, HEIGHT // 2 + 20)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
