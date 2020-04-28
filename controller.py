import pygame
from pygame.locals import *
import enum
import math

class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash(str(self.x) + ',' + str(self.y))
    
    def distance(self, other):
        return math.sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)

class Move(enum.Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3
    
    def __int__(self):
        return self.value

class Controller:
    player = None
    game = None
    
    def init(self, player, game):
        self.player = player
        self.game = game
    
    def make_move(self):
        pass
    
    def update_state(self):
        pass
    
    def display_controller_gui(self):
        pass

class KeyboardController(Controller):
    player = None
    game = None
    
    def init(self, player, game):
        self.player = player
        self.game = game
    
    def make_move(self):
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        
        if keys[K_RIGHT]:
            self.player.turn_right()
        elif keys[K_LEFT]:
            self.player.turn_left()
            
    
    def update_state(self):
        pass
    
    def display_controller_gui(self):
        pass
    