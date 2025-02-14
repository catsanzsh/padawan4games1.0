import pygame
import random
import numpy as np

# Initialize pygame
pygame.init()

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
BLUE = (50, 50, 200)
GREEN = (50, 200, 50)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout - Synthwave Atari Style")

# Paddle
paddle = pygame.Rect(WIDTH // 2 - 60, HEIGHT - 40, 120, 10)

# Ball
ball = pygame.Rect(WIDTH // 2, HEIGHT // 2, 10, 10)
ball_dx, ball_dy = BALL_SPEED, -BALL_SPEED

# Bricks
bricks = [pygame.Rect(c * BRICK_WIDTH, r * BRICK_HEIGHT, BRICK_WIDTH - 2, BRICK_HEIGHT - 2)
          for r in range(BRICK_ROWS) for c in range(BRICK_COLS)]

# Sound Synthesizer
def generate_sine_wave(frequency=440, duration=0.1, sample_rate=44100):
    # Generate a mono sine wave
    samples = np.sin(2 * np.pi * np.arange(sample_rate * duration) * frequency / sample_rate).astype(np.float32)
    # Convert to stereo by duplicating the mono channel
    samples_stereo = np.column_stack((samples, samples))
    # Scale to int16 range and create a sound object
    return pygame.sndarray.make_sound(np.int16(samples_stereo * 32767))

# Pre-generate synth sounds
bounce_sound = generate_sine_wave(440, 0.05)
break_sound = generate_sine_wave(220, 0.05)

# Game loop
running = True
clock = pygame.time.Clock()
while running:
    screen.fill((0, 0, 0))
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Paddle Movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle.left > 0:
        paddle.move_ip(-PADDLE_SPEED, 0)
    if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
        paddle.move_ip(PADDLE_SPEED, 0)
    
    # Ball Movement
    ball.move_ip(ball_dx, ball_dy)
    
    # Ball Collision (Walls)
    if ball.left <= 0 or ball.right >= WIDTH:
        ball_dx = -ball_dx
        bounce_sound.play()
    if ball.top <= 0:
        ball_dy = -ball_dy
        bounce_sound.play()
    
    # Ball Collision (Paddle)
    if ball.colliderect(paddle):
        ball_dy = -BALL_SPEED
        bounce_sound.play()
    
    # Ball Collision (Bricks)
    for brick in bricks[:]:
        if ball.colliderect(brick):
            bricks.remove(brick)
            ball_dy = -ball_dy
            break_sound.play()
            break
    
    # Game Over Condition
    if ball.bottom >= HEIGHT:
        ball.topleft = (WIDTH // 2, HEIGHT // 2)
        ball_dy = -BALL_SPEED
    
    # Draw everything
    pygame.draw.rect(screen, WHITE, paddle)
    pygame.draw.ellipse(screen, WHITE, ball)
    for brick in bricks:
        pygame.draw.rect(screen, RED, brick)
    
    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()
