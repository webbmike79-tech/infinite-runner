import pygame
import random
import sys

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
obstacles = []

# Game variables
score = 0
font = pygame.font.SysFont("Arial", 24)
game_over = False

# Timer event for spawning obstacles
SPAWN_OBSTACLE = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_OBSTACLE, 1300)  # Spawns every 1.3 seconds

def reset_game():
    """Resets all variables to start a new game."""
    global player_y, player_velocity_y, is_jumping, obstacles, score, game_over, obstacle_speed
    player_y = HEIGHT - player_height - 20
    player_velocity_y = 0
    is_jumping = False
    obstacles.clear()
    score = 0
    obstacle_speed = base_obstacle_speed
    game_over = False

running = True
while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_over:
                    reset_game()
                elif not is_jumping:
                    player_velocity_y = jump_power
                    is_jumping = True

        if event.type == SPAWN_OBSTACLE and not game_over:
            # Randomize obstacle height to make it less predictable
            obs_height = random.randint(30, 80)
            obs_y = HEIGHT - obs_height - 20
            obstacles.append(pygame.Rect(WIDTH, obs_y, obstacle_width, obs_height))

    if not game_over:
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

                # Increase game speed every 5 points
                if score % 5 == 0:
                    obstacle_speed += 0.5

            # Check for collision
            if player_rect.colliderect(obs):
                game_over = True

    # 4. Rendering
    screen.fill(WHITE)

    # Draw Ground
    pygame.draw.rect(screen, GREEN, (0, HEIGHT - 20, WIDTH, 20))

    if not game_over:
        # Draw Player
        pygame.draw.rect(screen, BLUE, (player_x, player_y, player_width, player_height))

        # Draw Obstacles
        for obs in obstacles:
            pygame.draw.rect(screen, RED, obs)

        # Draw Score
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))
    else:
        # Game Over Screen
        game_over_text = font.render("GAME OVER - Press SPACE to Restart", True, RED)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 20))
        final_score_text = font.render(f"Final Score: {score}", True, BLACK)
        screen.blit(final_score_text, (WIDTH//2 - final_score_text.get_width()//2, HEIGHT//2 + 20))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
