import pygame
import random
import numpy as np
from collections import deque

# Initialize Pygame and its mixer for sound
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2)

# Set up the game window
width = 800
height = 600
size = (width, height)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Snake Game")

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# Snake and food settings
snake_block = 20
snake_speed = 15

# Initialize fonts
score_font = pygame.font.SysFont('arial', 35)
game_over_font = pygame.font.SysFont('arial', 65)

class Snake:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.body = deque()
        self.direction = 'right'
        self.next_direction = 'right'  # Buffer for next direction change
        self.body.append((width/2 - snake_block*3.5, height/2))
        self.body.append((width/2 - snake_block*2.5, height/2))
        self.body.append((width/2 - snake_block*1.5, height/2))
        self.score = 0
        self.growth_pending = 0
    
    def move(self):
        # Update direction from buffered input
        self.direction = self.next_direction
        
        x, y = self.body[-1]
        if self.direction == 'right':
            x += snake_block
        elif self.direction == 'left':
            x -= snake_block
        elif self.direction == 'up':
            y -= snake_block
        elif self.direction == 'down':
            y += snake_block
        return (x, y)
    
    def change_direction(self, new_direction):
        # Prevent 180-degree turns
        opposite_directions = {
            'left': 'right',
            'right': 'left',
            'up': 'down',
            'down': 'up'
        }
        if new_direction != opposite_directions.get(self.direction):
            self.next_direction = new_direction

    def grow(self):
        self.growth_pending += 1
        self.score += 10

def play_beep(frequency=440, duration=0.2, volume=0.5):
    """Generate and play a beep using a sine wave."""
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    tone = np.sin(frequency * 2 * np.pi * t)
    audio = tone * (2**15 - 1) * volume
    audio = audio.astype(np.int16)
    audio_stereo = np.column_stack((audio, audio))
    sound = pygame.sndarray.make_sound(audio_stereo)
    sound.play()

def show_score(snake):
    score_surface = score_font.render(f'Score: {snake.score}', True, WHITE)
    screen.blit(score_surface, (10, 10))

def show_game_over(score):
    game_over_surface = game_over_font.render('GAME OVER', True, RED)
    score_surface = score_font.render(f'Final Score: {score}', True, WHITE)
    restart_surface = score_font.render('Press SPACE to restart', True, YELLOW)
    
    screen.blit(game_over_surface, (width//2 - 160, height//2 - 50))
    screen.blit(score_surface, (width//2 - 100, height//2 + 20))
    screen.blit(restart_surface, (width//2 - 150, height//2 + 80))

def main():
    clock = pygame.time.Clock()
    snake = Snake()
    game_over = False
    game_active = True

    # Initialize food position
    food_x = round(random.randrange(0, width - snake_block) / snake_block) * snake_block
    food_y = round(random.randrange(0, height - snake_block) / snake_block) * snake_block

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.KEYDOWN:
                if game_active:
                    if event.key in [pygame.K_LEFT, pygame.K_a]:
                        snake.change_direction('left')
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        snake.change_direction('right')
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        snake.change_direction('up')
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        snake.change_direction('down')
                elif event.key == pygame.K_SPACE:  # Restart game
                    snake = Snake()
                    food_x = round(random.randrange(0, width - snake_block) / snake_block) * snake_block
                    food_y = round(random.randrange(0, height - snake_block) / snake_block) * snake_block
                    game_active = True

        if game_active:
            # Move snake
            new_head = snake.move()
            
            # Check wall collision
            if (new_head[0] < 0 or new_head[0] >= width or 
                new_head[1] < 0 or new_head[1] >= height):
                game_active = False
                play_beep(220, 0.5, 0.8)  # Low pitch for game over
                continue

            # Check self collision
            if new_head in snake.body:
                game_active = False
                play_beep(220, 0.5, 0.8)  # Low pitch for game over
                continue

            snake.body.append(new_head)

            # Simplified food collision check
            head_x, head_y = new_head
            food_collision = (abs(head_x - food_x) < snake_block and 
                            abs(head_y - food_y) < snake_block)

            if food_collision:
                snake.grow()
                play_beep(660, 0.1, 0.5)  # High pitch for food
                # Generate new food position
                while True:
                    food_x = round(random.randrange(0, width - snake_block) / snake_block) * snake_block
                    food_y = round(random.randrange(0, height - snake_block) / snake_block) * snake_block
                    # Make sure food doesn't spawn on snake
                    if not any(abs(pos[0] - food_x) < snake_block and 
                             abs(pos[1] - food_y) < snake_block for pos in snake.body):
                        break

            # Only remove the tail if we're not growing
            if snake.growth_pending > 0:
                snake.growth_pending -= 1
            else:
                snake.body.popleft()

            # Draw everything
            screen.fill(BLACK)
            
            # Draw food with collision box
            pygame.draw.rect(screen, RED, (food_x, food_y, snake_block, snake_block))
            
            # Draw snake
            for pos in snake.body:
                pygame.draw.rect(screen, GREEN, (pos[0], pos[1], snake_block, snake_block))
                
            show_score(snake)
        else:
            show_game_over(snake.score)

        pygame.display.update()
        clock.tick(snake_speed)

    pygame.quit()
    quit()

if __name__ == "__main__":
    main()
