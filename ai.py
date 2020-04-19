from controller import *
import random


class CellItemType(enum.Enum):
    EMPTY = 0
    BODY = 1
    HEAD = 2
    FRUIT = 4
    
    
class AIController(Controller):
    player = None
    game = None
    
    def make_move(self):
        self.player.set_move(Move(random.randint(1,4)))
    
    def update_state(self):
        if not self.game.is_end():
            board = self.board_state_to_list()
            # TODO
    
    def coordinates_to_board_index(self, x, y):
        tmp_x = (x - self.game.board_rect.top) / self.player.step
        tmp_y = (y - self.game.board_rect.left) / self.player.step
        
        width = (self.game.board_rect.right - self.game.board_rect.left) / self.player.step
        return int(tmp_y * width + tmp_x)
    
    def board_state_to_list(self):
        board = []
        for row in range(self.game.board_rect.top, self.game.board_rect.bottom, self.player.step):
            for col in range(self.game.board_rect.left, self.game.board_rect.right, self.player.step):
                board.append(CellItemType.EMPTY.value)
                
        board[self.coordinates_to_board_index(self.game.fruit.position.x, self.game.fruit.position.y)] = CellItemType.FRUIT.value
        
        for pos in self.player.positions:
            board[self.coordinates_to_board_index(pos.x, pos.y)] = CellItemType.BODY.value
        
        snake_head = self.player.positions[0]
        board[self.coordinates_to_board_index(snake_head.x, snake_head.y)] = CellItemType.HEAD.value
        
        return board
    