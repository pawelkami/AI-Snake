from controller import *
import random

from keras.optimizers import Adam
from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from keras.utils.np_utils import to_categorical

import numpy as np


class CellItemType(enum.Enum):
    EMPTY = 0
    BODY = 1
    HEAD = 2
    FRUIT = 4
    
    
class AIController(Controller):
    player = None
    game = None
    neural_network = None
    learning_rate = 0.0005
    first_layer = 1000
    second_layer = 1000
    third_layer = 1000
    train_flag = True
    
    def init(self, player, game):
        self.player = player
        self.game = game
        self.reward = 0
        self.score = 0
        self.last_state = self.board_state_to_list()
        self.last_decision = None
        
        if not self.neural_network:
            self.create_network()
            
            
    def get_input_size(self):
        return len(self.last_state)
    
    
    def make_move(self):
        self.last_state = self.board_state_to_list()
        prediction = self.neural_network.predict(self.last_state.reshape((1, self.get_input_size())))
        self.last_decision = to_categorical(np.argmax(prediction[0]), num_classes=3)
        
        if self.last_decision[0]:   # left
            self.player.turn_left()
        elif self.last_decision[1]: # forward
            pass
        elif self.last_decision[2]: # right
            self.player.turn_right()
        
            
    def set_reward(self):
        self.reward = 0
        if self.player.get_score() > self.score:
            self.score = self.player.get_score()
            self.reward = 500
        elif self.game.is_end():
            self.reward = -500
        # else:
        #     self.reward = - self.player.positions[0].distance(self.game.fruit.position) / self.player.step
        
    
    
    def update_state(self):
        if self.train_flag:
            self.set_reward()
            #print(self.reward)
            target_f = self.neural_network.predict(self.last_state.reshape((1, self.get_input_size())))
            target_f[0][np.argmax(self.last_decision)] = self.reward
            self.neural_network.fit(self.last_state.reshape((1, self.get_input_size())), target_f, epochs=1, verbose=0)
    
    
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
        
        return np.asarray(board)
    
    
    def create_network(self):
        self.neural_network = Sequential()
        self.neural_network.add(Dense(output_dim=self.first_layer, activation='relu', input_dim=self.get_input_size()))
        self.neural_network.add(Dense(output_dim=self.second_layer, activation='relu'))
        self.neural_network.add(Dense(output_dim=self.third_layer, activation='relu'))
        self.neural_network.add(Dense(output_dim=3, activation='softmax'))
        
        opt = Adam(self.learning_rate)
        self.neural_network.compile(loss='mse', optimizer=opt)
    
    