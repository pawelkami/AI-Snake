from pygame.locals import *
import pygame
import enum


class Move(enum.Enum):
    UP = 1
    DOWN = 2
    RIGHT = 3
    LEFT = 4


class Player:
    def __init__(self):
        position = []
        self.x = 10
        self.y = 10
        self.speed = 5
        self.score = 0
        self.last_move = Move.RIGHT
        self.image = pygame.image.load('img/body.png')
        
    
    def get_first_block_rect(self):
        return pygame.Rect(self.x, self.y, 20, 20)
    
    def set_move(self, move):
        self.last_move = move
        
        
    def make_move(self):
        if self.last_move == Move.UP:
            self.move_up()
        elif self.last_move == Move.DOWN:
            self.move_down()
        elif self.last_move == Move.LEFT:
            self.move_left()
        elif self.last_move == Move.RIGHT:
            self.move_right()
            
    
    def move_right(self):
        self.x += self.speed
    
    def move_left(self):
        self.x -= self.speed
    
    def move_up(self):
        self.y -= self.speed
    
    def move_down(self):
        self.y += self.speed
        
        
class Game:
    window_width = 800
    window_height = 800
    border_width = 50
    player = None
    
    def __init__(self):
        self._running = True
        self._display_surf = None
        self._image_surf = None
        self.board_rect = None
        self.highscore = 0
        self.game_count = 1
        self.player = Player()
        
    
    def init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode((self.window_width, self.window_height + 150), pygame.HWSURFACE)
        self.board_rect = pygame.Rect(self.border_width, self.border_width, self.window_width - 2 * self.border_width, self.window_height - 2 * self.border_width)
        
        pygame.display.set_caption('AI SNAKE')
        
        self._running = True
        self._image_surf = self.player.image
        
    
    def is_player_inside_board(self):
        return self.board_rect.contains(self.player.get_first_block_rect())
        
        
    def on_event(self, event):
        if event.type == QUIT:
            self._running = False


    def on_loop(self):
        pass
    
    def draw_board(self):
        self._display_surf.fill((0, 0, 0))    # border
        print("Player in rect: " + str(self.is_player_inside_board()))
        pygame.draw.rect(self._display_surf, (255, 255, 255), self.board_rect) # board where snake moves
        
        
    def draw_ui(self):
        myfont = pygame.font.SysFont('Segoe UI', 32)
        myfont_bold = pygame.font.SysFont('Segoe UI', 32, True)
        text_game_count = myfont.render('GAME COUNT: ', True, (255, 255, 255))
        text_game_count_number = myfont.render(str(self.game_count), True, (255, 255, 255))
        text_score = myfont.render('SCORE: ', True, (255, 255, 255))
        text_score_number = myfont.render(str(self.player.score), True, (255, 255, 255))
        text_highest = myfont.render('HIGHEST SCORE: ', True, (255, 255, 255))
        text_highest_number = myfont_bold.render(str(self.highscore), True, (255, 255, 255))
        self._display_surf.blit(text_game_count, (45, self.window_height + 50))
        self._display_surf.blit(text_game_count_number, (220, self.window_height + 50))
        
        self._display_surf.blit(text_score, (45, self.window_height + 100))
        self._display_surf.blit(text_score_number, (150, self.window_height + 100))
        self._display_surf.blit(text_highest, (220, self.window_height + 100))
        self._display_surf.blit(text_highest_number, (430, self.window_height + 100))
        #self._display_surf.blit(game.bg, (10, 10))
        pass
    
    def draw_snake(self):
        self._display_surf.blit(self._image_surf, (self.player.x, self.player.y))
        
        
    def draw_fruit(self):
        pass
        
    
    def on_render(self):
        self.draw_board()
        self.draw_ui()
        self.draw_snake()
        self.draw_fruit()

        pygame.display.flip()
        
        
    def on_cleanup(self):
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
        
        
    def make_move(self):
        self.player.make_move()
        
        
    def run(self):
        self.init()
        
        while self._running:
            self.read_move()
            self.make_move()
                
            self.on_loop()
            self.on_render()
        self.on_cleanup()
    
    
    
if __name__ == "__main__":
    game = Game()
    game.run()