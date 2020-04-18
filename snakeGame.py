from pygame.locals import *
import pygame
import enum
import random

INITIAL_LENGTH = 1

class Move(enum.Enum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4
    
    def __int__(self):
        return self.value
    
    
class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash(str(self.x) + ',' + str(self.y))
    

class Fruit:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.image = pygame.image.load('img/fruit.png')
        
    def get_rect(self):
        return self.image.get_rect().move((self.x, self.y))
    


class Player:
    def __init__(self):
        self.positions = [Position(100, 100)]
        self.last_move = Move.RIGHT
        self.image = pygame.image.load('img/body.png')
        self.step = self.get_first_block_rect().right - self.get_first_block_rect().left
        
        
    def make_bigger(self):
        self.positions.append(Position(0, 0))
        
    
    def get_first_block_rect(self):
        return self.image.get_rect().move((self.positions[0].x, self.positions[0].y))
    
    def get_snake_length(self):
        return len(self.positions)
    
    def get_score(self):
        return self.get_snake_length() - INITIAL_LENGTH
    
    def set_move(self, move):
        if abs(int(self.last_move) - int(move)) != 2:
            self.last_move = move
        
    def update(self):
        for i in range(len(self.positions) - 1, 0, -1):
            self.positions[i].x = self.positions[i-1].x
            self.positions[i].y = self.positions[i-1].y
            
        if self.last_move == Move.UP:
            self.positions[0].y -= self.step
        elif self.last_move == Move.DOWN:
            self.positions[0].y += self.step
        elif self.last_move == Move.LEFT:
            self.positions[0].x -= self.step
        elif self.last_move == Move.RIGHT:
            self.positions[0].x += self.step
        
        
class Game:
    window_width = 800
    window_height = 800
    border_width = 40
    player = None
    fruit = None
    
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.board_rect = None
        self.highscore = 0
        self.game_count = 1
        self.player = Player()
        self.fruit = Fruit()
        
    
    def init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode((self.window_width, self.window_height + 150), pygame.HWSURFACE)
        self.board_rect = pygame.Rect(self.border_width, self.border_width, self.window_width - 2 * self.border_width, self.window_height - 2 * self.border_width)
        
        pygame.display.set_caption('AI SNAKE')
        
        self._running = True
        
        self.generate_fruit()
        
    
    def is_player_inside_board(self):
        return self.board_rect.contains(self.player.get_first_block_rect())
        
    
    def draw_board(self):
        self._display_surf.fill((0, 0, 0))    # border
        pygame.draw.rect(self._display_surf, (255, 255, 255), self.board_rect) # board where snake moves
        
        
    def draw_ui(self):
        myfont = pygame.font.SysFont('Segoe UI', 32)
        myfont_bold = pygame.font.SysFont('Segoe UI', 32, True)
        text_game_count = myfont.render('GAME COUNT: ', True, (255, 255, 255))
        text_game_count_number = myfont.render(str(self.game_count), True, (255, 255, 255))
        text_score = myfont.render('SCORE: ', True, (255, 255, 255))
        text_score_number = myfont.render(str(self.player.get_score()), True, (255, 255, 255))
        text_highest = myfont.render('HIGHEST SCORE: ', True, (255, 255, 255))
        text_highest_number = myfont_bold.render(str(self.highscore), True, (255, 255, 255))
        self._display_surf.blit(text_game_count, (45, self.window_height + 50))
        self._display_surf.blit(text_game_count_number, (220, self.window_height + 50))
        
        self._display_surf.blit(text_score, (45, self.window_height + 100))
        self._display_surf.blit(text_score_number, (150, self.window_height + 100))
        self._display_surf.blit(text_highest, (220, self.window_height + 100))
        self._display_surf.blit(text_highest_number, (430, self.window_height + 100))


    def draw_snake(self):
        for p in self.player.positions:
            self._display_surf.blit(self.player.image, (p.x, p.y))
        
        
    def draw_fruit(self):
        self._display_surf.blit(self.fruit.image, (self.fruit.x, self.fruit.y))
        
        
    def generate_fruit(self):
        self.fruit.x = random.randint(self.board_rect.left, self.board_rect.right - 20)
        self.fruit.y = random.randint(self.board_rect.top, self.board_rect.bottom - 20)
        
        self.fruit.x -= self.fruit.x % 20
        self.fruit.y -= self.fruit.y % 20
        
        # todo check if fruit is generated on snake body?
        
    
    def render(self):
        self.draw_board()
        self.draw_ui()
        self.draw_snake()
        self.draw_fruit()

        pygame.display.flip()
        
        
    def cleanup(self):
        pygame.quit()
        
    def read_move(self):
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        
        if keys[K_RIGHT]:
            self.player.set_move(Move.RIGHT)
        elif keys[K_LEFT]:
            self.player.set_move(Move.LEFT)
        elif keys[K_UP]:
            self.player.set_move(Move.UP)
        elif keys[K_DOWN]:
            self.player.set_move(Move.DOWN)
            
        if keys[K_ESCAPE]:
            self._running = False
        
        
    def update_snake(self):
        self.player.update()
        
    
    def check_collisions(self):
        if not self.is_player_inside_board():
            self._running = False
            
        if len(self.player.positions) != len(set(self.player.positions)):
            # there are duplicates -> snake is colliding with itself
            self._running = False
        
        if self.fruit.get_rect().contains(self.player.get_first_block_rect()):
            self.player.make_bigger()
            self.generate_fruit()
            if self.player.get_score() > self.highscore:
                self.highscore = self.player.get_score()
        
        
    def run(self):
        self.init()
        self.generate_fruit()
        while self._running:
            self.read_move()
            self.update_snake()
            
            self.check_collisions()
                
            self.render()
            pygame.time.wait(100)
    
    
    
if __name__ == "__main__":
    game = Game()
    game.run()
    game.cleanup()