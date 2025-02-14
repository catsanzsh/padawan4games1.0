import pygame
import numpy as np

# Initialize pygame and fonts
pygame.init()
pygame.font.init()

# Game Constants
WIDTH, HEIGHT = 800, 600
BALL_SPEED = 4
PADDLE_SPEED = 6
BRICK_ROWS, BRICK_COLS = 5, 8
BRICK_WIDTH = WIDTH // BRICK_COLS
BRICK_HEIGHT = 30

# Colors
WHITE = (255, 255, 255)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLACK = (0, 0, 0)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout - Synthwave Atari Style")

# Fonts
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 48)

# Sound Synthesizer
def generate_sine_wave(frequency=440, duration=0.1, sample_rate=44100):
    samples = np.sin(2 * np.pi * np.arange(int(sample_rate * duration)) * frequency / sample_rate).astype(np.float32)
    samples_stereo = np.column_stack((samples, samples))
    return pygame.sndarray.make_sound(np.int16(samples_stereo * 32767))

bounce_sound = generate_sine_wave(440, 0.05)
break_sound = generate_sine_wave(220, 0.05)

def draw_text(text, font_obj, color, surface, x, y):
    textobj = font_obj.render(text, True, color)
    textrect = textobj.get_rect(center=(x, y))
    surface.blit(textobj, textrect)

def show_main_menu():
    waiting = True
    while waiting:
        screen.fill(BLACK)
        draw_text("Breakout - Synthwave Atari Style", big_font, WHITE, screen, WIDTH // 2, HEIGHT // 2 - 50)
        draw_text("Press SPACE to start", font, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 20)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

def show_game_over(score, win=False):
    waiting = True
    while waiting:
        screen.fill(BLACK)
        if win:
            draw_text("YOU WIN!", big_font, GREEN, screen, WIDTH // 2, HEIGHT // 2 - 50)
        else:
            draw_text("GAME OVER", big_font, RED, screen, WIDTH // 2, HEIGHT // 2 - 50)
        draw_text(f"Score: {score}", font, WHITE, screen, WIDTH // 2, HEIGHT // 2)
        draw_text("Press SPACE to return to main menu", font, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 50)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

def run_game():
    # Initialize game objects
    paddle = pygame.Rect(WIDTH // 2 - 60, HEIGHT - 40, 120, 10)
    ball = pygame.Rect(WIDTH // 2, HEIGHT // 2, 10, 10)
    ball_dx, ball_dy = BALL_SPEED, -BALL_SPEED
    bricks = [pygame.Rect(c * BRICK_WIDTH, r * BRICK_HEIGHT, BRICK_WIDTH - 2, BRICK_HEIGHT - 2)
              for r in range(BRICK_ROWS) for c in range(BRICK_COLS)]
    
    score = 0
    lives = 3

    clock = pygame.time.Clock()
    running = True
    while running:
        clock.tick(60)
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                
        # Paddle Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle.left > 0:
            paddle.move_ip(-PADDLE_SPEED, 0)
        if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
            paddle.move_ip(PADDLE_SPEED, 0)
        
        # Ball Movement
        ball.move_ip(ball_dx, ball_dy)
        
        # Ball Collision with Walls
        if ball.left <= 0 or ball.right >= WIDTH:
            ball_dx = -ball_dx
            bounce_sound.play()
        if ball.top <= 0:
            ball_dy = -ball_dy
            bounce_sound.play()
        
        # Ball Collision with Paddle
        if ball.colliderect(paddle) and ball_dy > 0:
            ball_dy = -BALL_SPEED
            bounce_sound.play()
        
        # Ball Collision with Bricks
        for brick in bricks[:]:
            if ball.colliderect(brick):
                bricks.remove(brick)
                ball_dy = -ball_dy
                score += 10
                break_sound.play()
                break
        
        # Ball falls below the screen (life lost)
        if ball.bottom >= HEIGHT:
            lives -= 1
            if lives > 0:
                # Reset positions for next life
                ball.topleft = (WIDTH // 2, HEIGHT // 2)
                ball_dx, ball_dy = BALL_SPEED, -BALL_SPEED
                paddle.centerx = WIDTH // 2
                pygame.time.delay(1000)
            else:
                running = False
        
        # Win condition: All bricks cleared
        if not bricks:
            running = False
        
        # Drawing
        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, paddle)
        pygame.draw.ellipse(screen, WHITE, ball)
        for brick in bricks:
            pygame.draw.rect(screen, RED, brick)
        
        # Display Score and Lives
        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(score_text, (10, HEIGHT - 30))
        screen.blit(lives_text, (WIDTH - 100, HEIGHT - 30))
        
        pygame.display.flip()
    
    # End-of-game: Determine if player won or lost
    win = True if not bricks else False
    show_game_over(score, win)

def main():
    while True:
        show_main_menu()
        run_game()

if __name__ == "__main__":
    main()
