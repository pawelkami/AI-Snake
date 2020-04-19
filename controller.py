import pygame
from pygame.locals import *
import enum

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
    
    def make_move(self):
        pass
    
    def update_state(self):
        pass

class KeyboardController(Controller):
    player = None
    game = None
    
    def make_move(self):
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        
        if keys[K_RIGHT]:
            self.player.turn_right()
        elif keys[K_LEFT]:
            self.player.turn_left()
            
    
    def update_state(self):
        pass
    