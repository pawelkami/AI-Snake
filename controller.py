import pygame
from pygame.locals import *
import enum

class Move(enum.Enum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4
    
    NONE = 255
    
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
        move = Move.NONE
        
        if keys[K_RIGHT]:
            move = Move.RIGHT
        elif keys[K_LEFT]:
            move = Move.LEFT
        elif keys[K_UP]:
            move = Move.UP
        elif keys[K_DOWN]:
            move = Move.DOWN
            
        self.player.set_move(move)
    
    def update_state(self):
        pass
    