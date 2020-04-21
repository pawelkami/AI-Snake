from pygame.locals import *
import pygame
import enum
import random
import argparse
from ai import *
from controller import *

INITIAL_LENGTH = 1
WINDOW_TO_STEP_MULTIPLIER = 20
    
class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash(str(self.x) + ',' + str(self.y))
    
    def distance(self, other):
        return abs(other.x - self.x) + abs(other.y - self.y)
    

class Fruit:
    def __init__(self):
        self.position = Position(0, 0)
        self.image = pygame.image.load('img/fruit.png')
        
    def get_rect(self):
        return self.image.get_rect().move((self.position.x, self.position.y))
    


class Player:
    def __init__(self):
        self.positions = []
        for i in range(0, INITIAL_LENGTH):
            self.positions.append(Position(0, 0))
        self.last_move = Move.LEFT
        self.image = pygame.image.load('img/body.png')
        self.step = self.get_first_block_rect().right - self.get_first_block_rect().left
        
        
    def make_bigger(self):
        self.positions.append(Position(self.positions[-1].x, self.positions[-1].y))
        
    
    def get_first_block_rect(self):
        return self.image.get_rect().move((self.positions[0].x, self.positions[0].y))
    
    def get_snake_length(self):
        return len(self.positions)
    
    def get_score(self):
        return self.get_snake_length() - INITIAL_LENGTH
    
    def turn_left(self):
        self.last_move = Move((self.last_move.value - 1) % 4)
    
    def turn_right(self):
        self.last_move = Move((self.last_move.value + 1) % 4)
    
    def _set_move(self, move):
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
    player = None
    fruit = None
    
    def __init__(self, controller, speed):
        pygame.init()
        self._running = True
        self._display_surf = None
        self.board_rect = None
        self.highscore = 0
        self.game_count = 0
        self.speed = speed
        self.controller = controller
        self.fruit = Fruit()
        
    def _generate_init_player_state(self):
        self.player.positions[0].x = random.randint(self.board_rect.left, self.board_rect.right - 1)
        self.player.positions[0].y = random.randint(self.board_rect.top, self.board_rect.bottom - 1)
        
        self.player.positions[0].x -= self.player.positions[0].x % self.player.step
        self.player.positions[0].y -= self.player.positions[0].y % self.player.step
        
        self.player._set_move(Move(random.randint(0, 3)))
    
    
    def init(self):
        pygame.display.set_caption('AI SNAKE')
        self.player = Player()
        self.border_width = 2 * self.player.step
        self.window_width = WINDOW_TO_STEP_MULTIPLIER * self.player.step
        self.window_height = WINDOW_TO_STEP_MULTIPLIER * self.player.step
        
        self._display_surf = pygame.display.set_mode((self.window_width, self.window_height + 150), pygame.HWSURFACE)
        self.board_rect = pygame.Rect(self.border_width, self.border_width, self.window_width - 2 * self.border_width, self.window_height - 2 * self.border_width)
        
        self._generate_init_player_state()
        self.generate_fruit()
        self.controller.init(self.player, self)
        self.moves_left = 200
        self._running = True
        
    
    def is_player_inside_board(self):
        return self.board_rect.contains(self.player.get_first_block_rect())
    
    def get_score(self):
        return self.player.get_score()
    
    def is_end(self):
        return not self._running
        
    
    def draw_board(self):
        self._display_surf.fill((0, 0, 0))    # border
        pygame.draw.rect(self._display_surf, (255, 255, 255), self.board_rect) # board where snake moves
        
        
    def draw_ui(self):
        myfont = pygame.font.SysFont('Segoe UI', 23)
        myfont_bold = pygame.font.SysFont('Segoe UI', 23, True)
        
        text_game_count = myfont.render('GAME COUNT: ', True, (255, 255, 255))
        text_game_count_number = myfont.render(str(self.game_count), True, (255, 255, 255))  
        text_moves_left = myfont.render('MOVES LEFT: ', True, (255, 255, 255))
        text_moves_left_number = myfont.render(str(self.moves_left), True, (255, 255, 255))
        
        text_score = myfont.render('SCORE: ', True, (255, 255, 255))
        text_score_number = myfont.render(str(self.get_score()), True, (255, 255, 255))
        text_highest = myfont.render('HIGHEST SCORE: ', True, (255, 255, 255))
        text_highest_number = myfont_bold.render(str(self.highscore), True, (255, 255, 255))
        
        self._display_surf.blit(text_game_count, (45, self.window_height + 50))
        self._display_surf.blit(text_game_count_number, (180, self.window_height + 50))
        self._display_surf.blit(text_moves_left, (220, self.window_height + 50))
        self._display_surf.blit(text_moves_left_number, (360, self.window_height + 50))
        
        self._display_surf.blit(text_score, (45, self.window_height + 100))
        self._display_surf.blit(text_score_number, (180, self.window_height + 100))
        self._display_surf.blit(text_highest, (220, self.window_height + 100))
        self._display_surf.blit(text_highest_number, (360, self.window_height + 100))


    def draw_snake(self):
        for p in self.player.positions:
            self._display_surf.blit(self.player.image, (p.x, p.y))
        
        
    def draw_fruit(self):
        self._display_surf.blit(self.fruit.image, (self.fruit.position.x, self.fruit.position.y))
        
        
    def generate_fruit(self):
        self.fruit.position.x = random.randint(self.board_rect.left, self.board_rect.right - 1)
        self.fruit.position.y = random.randint(self.board_rect.top, self.board_rect.bottom - 1)
        
        self.fruit.position.x -= self.fruit.position.x % self.player.step
        self.fruit.position.y -= self.fruit.position.y % self.player.step
        
        # check if fruit is generated on snake body by mistake
        if self.fruit.position in self.player.positions:
            self.generate_fruit()
        
    
    def render(self):
        self.draw_board()
        self.draw_ui()
        self.draw_snake()
        self.draw_fruit()

        pygame.display.flip()
        
        
    def cleanup(self):
        pygame.quit()
        
    def read_move(self):
        last_move = self.player.last_move
        self.controller.make_move()
        if last_move != self.player.last_move:
            self.moves_left -= 1
        
        
    def update_snake(self):
        self.player.update()
        
    
    def check_collisions(self):
        if not self.is_player_inside_board():
            self._running = False
            
        if self.moves_left <= 0:
            self._running = False         
            
        if len(self.player.positions) != len(set(self.player.positions)):
            # there are duplicates -> snake is colliding with itself
            self._running = False
        
        if self.fruit.get_rect().contains(self.player.get_first_block_rect()):
            self.player.make_bigger()
            self.moves_left += 500
            self.generate_fruit()
            if self.player.get_score() > self.highscore:
                self.highscore = self.player.get_score()
        
        
    def run(self):
        self.init()
        self.game_count += 1
        while not self.is_end():
            self.render()
            self.read_move()
            
            self.update_snake()
            self.check_collisions()
                
            self.controller.update_state()
            pygame.time.wait(self.speed)
    
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ai', action='store_true', help="AI controlls snake")
    parser.add_argument('--speed', type=int, default=100, help='Speed of game. 0 is the fastest. Default: 100')
    parser.add_argument('--count', type=int, default=100, help='Game count to play. Default: 100')
    args = parser.parse_args()
    
    controller = KeyboardController()
    if args.ai:
        controller = AIController()
        
    score_in_game = []
    highscore_in_game = [] 
    
    game = Game(controller, args.speed)
    while game.game_count < args.count or args.count == 0:
        game.run()
        score_in_game.append(game.get_score())
        highscore_in_game.append(game.highscore)
        print("Game count: {} Highscore: {}".format(game.game_count, game.highscore))
        
    game.cleanup()