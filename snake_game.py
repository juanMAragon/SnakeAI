

import pygame
import random
from enum import Enum
from collections import namedtuple
import time
import numpy as np

pygame.init()  # required to initialize all the modules correctly


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


Point = namedtuple('Point', 'x, y')  # light weight class

# RGB colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN1 = (51, 102, 0)
GREEN2 = (77, 153, 0)
BLACK = (0, 0, 0)
GRAY = (77, 77, 77)

# game constants
BLOCK_SIZE = 20
SPEED = 10  # the higher the number the faster the game is
font = pygame.font.Font('./Our-Arcade-Games.ttf', 25)

# agent control game
class SnakeGameAI:

    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h


        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()

        self.reset()

        

    def reset(self):
        # init game state
        self.direction = Direction.RIGHT  # initial direction

        self.head = Point(self.w/2, self.h/2)  # position of the snake
        self.snake = [self.head, Point(
            self.head.x - BLOCK_SIZE, self.head.y), Point(self.head.x - (2*BLOCK_SIZE), self.head.y)]
        self.score = 0
        self.food = None
        self._place_food()
        self.start_time = time.time()

        self.frame_iteration = 0 

    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        y = random.randint(30//BLOCK_SIZE, (self.h-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def play_step(self, action):
        # collect the user input
        self.frame_iteration += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            
        # move the snake
        self._move(action)
        self.snake.insert(0, self.head) #update the head

        # check if game over and quit
        reward = 0
        game_over = False
        if self._is_collision() or self.frame_iteration > 100*len(self.snake):
            reward = -10
            game_over = True
            return reward, game_over, self.score
        
        # place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()

        # update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)

        # return game over and score
        game_over = False
        return reward, game_over, self.score

    def _is_collision(self, pt=None):

        if pt is None:
            pt = self.head

        # check if it hits the boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y < 0 or pt.y > self.h - BLOCK_SIZE:
            return True

        # check if it hits itself
        if pt in self.snake[1:]:
            return True

        return False



    def _update_ui(self):
        self.display.fill(BLACK)

        for point in self.snake:
            pygame.draw.rect(self.display, GREEN1, pygame.Rect(
                point.x, point.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, GREEN2, pygame.Rect(point.x + int(BLOCK_SIZE*1/5),
                        point.y + int(BLOCK_SIZE*1/5), int(BLOCK_SIZE*3/5), int(BLOCK_SIZE*3/5)))
            pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
            

            text = font.render("score {0:<10} speed {1:<10} time {2:<10}".format(str(self.score).zfill(4), str(SPEED).zfill(2), str(int(time.time() - self.start_time)).zfill(4)), True, WHITE)
            text_rect = text.get_rect(center=(self.w/2, 15))
            self.display.blit(text, text_rect)
            pygame.display.flip()
    
    def _move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1,0,0]):
            new_dir = clock_wise[idx] # no change 
        elif np.array_equal(action, [0,1,0]):
            next_idx = (idx + 1)%4
            new_dir = clock_wise[next_idx]
        else: 
            next_idx = (idx - 1)%4
            new_dir = clock_wise[next_idx]

        self.direction = new_dir

        x = self.head.x 
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE 
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE 
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE

        self.head = Point(x,y)  
