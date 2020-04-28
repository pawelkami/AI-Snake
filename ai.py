from controller import *
import random

from keras.optimizers import Adam
from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from keras.utils.np_utils import to_categorical
import collections

from pygame import gfxdraw
import pygame

import numpy as np


class CellItemType(enum.Enum):
    WALL = -1
    EMPTY = 0
    BODY = 1
    HEAD = 2
    FRUIT = 4
    
    def __int__(self):
        return self.value
    
    
class MemoryItem:  
    def __init__(self, state, last_decision, reward, next_state, end):
        self.state = state
        self.last_decision = last_decision
        self.reward = reward
        self.next_state = next_state
        self.end = end
    
    
class AIController(Controller):
    player = None
    game = None
    neural_network = None
    learning_rate = 0.0005
    discount = 0.5 # 0.6 is the best 
    
    epsilon = 0.1
    epsilon_decay_linear = 1/200
    
    memory_size = 2000
    replay_size = 500
    memory = collections.deque(maxlen=memory_size)
    
    first_layer = 100
    second_layer = 36
    third_layer = 36
    train_flag = True
    
    def init(self, player, game):
        self.player = player
        self.game = game
        self.reward = 0
        self.score = 0
        if self.train_flag:
            #self.epsilon = 1 - (self.game.game_count * self.epsilon_decay_linear)
            self.player.positions[0].x = 240
            self.player.positions[0].y = 240
            self.game.fruit.position.x = 200
            self.game.fruit.position.y = 200       
            self.player._set_move(Move.RIGHT)
        else:
            self.epsilon = 0
            
        self.last_state = self.get_snake_vision()
        self.last_decision = None
        
        if not self.neural_network:
            self.create_network()
            
        self.replay()
        
    def display_controller_gui(self):
        self.render_network()
            
            
    def save_to_memory(self, state, decision, reward, next_state, end):
        self.memory.append(MemoryItem(state, decision, reward, next_state, end))
            
            
    def get_input_size(self):
        return len(self.last_state)
    
    
    def scan(self, board, start_pos, itemType, direction):
        i = 1
        while True:
            x = start_pos.x + i * self.player.step * direction[0]
            y = start_pos.y + i * self.player.step * direction[1]

            if x < self.get_min_x() or x >= self.get_max_x() or y < self.get_min_y() or y >= self.get_max_y():
                if itemType == CellItemType.WALL:
                    return 1 / (start_pos.distance(Position(x, y)) / self.player.step)
                break
            
            curr_idx = self.coordinates_to_board_index(x, y)
            if board[curr_idx] == int(itemType):
                return 1 / (start_pos.distance(Position(x, y)) / self.player.step)
            
            i += 1
            
        return 0
    
    
    def get_snake_vision(self):
        if self.game.is_end():
            return np.asarray([1, 1, 1, 1, 1, 1, 1,
                               1, 1, 1, 1, 1, 1, 1,
                               0, 0, 0, 0, 0, 0, 0])
            
        board = self.board_state_to_list()
        directions = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)] # up, up-right, right...
        
        directions_for_move = None
        if self.player.last_move == Move.UP:
            directions_for_move = directions[-3:] + directions[:4]
        elif self.player.last_move == Move.RIGHT:
            directions_for_move = directions[-1:] + directions[:6]
        elif self.player.last_move == Move.DOWN:
            directions_for_move = directions[1:]
        elif self.player.last_move == Move.LEFT:
            directions_for_move = directions[3:] + directions[:2]
        
        vision = []
        for cell in (CellItemType.WALL, CellItemType.BODY, CellItemType.FRUIT):
            for direction in directions_for_move:
                vision.append(self.scan(board, self.player.positions[0], cell, direction))
            
        return np.asarray(vision)
        
    
    
    def make_move(self):
        self.last_state = self.get_snake_vision()
        if random.random() < self.epsilon:
            self.last_decision = to_categorical(random.randint(0, 2), num_classes=3)
        else:
            prediction = self.neural_network.predict(self.last_state.reshape((1, self.get_input_size())))
            self.last_decision = to_categorical(np.argmax(prediction[0]), num_classes=3)
        
        if self.last_decision[0]:   # left
            self.player.turn_left()
        elif self.last_decision[1]: # right
            self.player.turn_right()
        elif self.last_decision[2]: # forward
            pass
        
        self.render_network()
        
            
    def set_reward(self):
        self.reward = 0
        if self.player.get_score() > self.score:
            self.score = self.player.get_score()
            self.reward = 100
        elif self.game.is_end():
            self.reward = -100
        
        
    def replay(self):
        if len(self.memory) > self.replay_size:
            curr_replay = random.sample(self.memory, self.replay_size)
        else:
            curr_replay = self.memory
            
        for item in curr_replay:
            reward = item.reward
            if not item.end:
                reward += self.discount * np.amax(self.neural_network.predict(item.next_state.reshape((1, self.get_input_size())))[0])
            
            target_f = self.neural_network.predict(item.state.reshape((1, self.get_input_size())))
            target_f[0][np.argmax(item.last_decision)] = reward
            self.neural_network.fit(item.state.reshape((1, self.get_input_size())), target_f, epochs=1, verbose=0)
            
    
    def update_state(self):
        if self.train_flag:
            self.set_reward()
            if not self.game.is_end():
                self.reward += self.discount * np.amax(self.neural_network.predict(self.get_snake_vision().reshape((1, self.get_input_size())))[0])
            
            target_f = self.neural_network.predict(self.last_state.reshape((1, self.get_input_size())))
            target_f[0][np.argmax(self.last_decision)] = self.reward
            self.neural_network.fit(self.last_state.reshape((1, self.get_input_size())), target_f, epochs=1, verbose=0)
            
            self.save_to_memory(self.last_state, self.last_decision, self.reward, self.get_snake_vision(), self.game.is_end())
    
    
    def get_board_width(self):
        return (self.game.board_rect.right - self.game.board_rect.left) / self.player.step
    
    def get_board_height(self):
        return (self.game.board_rect.bottom - self.game.board_rect.top) / self.player.step
    
    
    def get_min_x(self):
        return self.game.board_rect.left
    
    
    def get_min_y(self):
        return self.game.board_rect.top
    
    
    def get_max_x(self):
        return self.game.board_rect.right
    
    
    def get_max_y(self):
        return self.game.board_rect.bottom
    
    
    def coordinates_to_board_index(self, x, y):
        tmp_x = (x - self.get_min_x()) / self.player.step
        tmp_y = (y - self.get_min_y()) / self.player.step
        
        width = self.get_board_width()
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
        self.neural_network.add(Dense(units=self.get_input_size(), activation='relu', input_dim=self.get_input_size()))
        self.neural_network.add(Dense(units=self.second_layer, activation='relu'))
        self.neural_network.add(Dense(units=self.third_layer, activation='relu'))
        self.neural_network.add(Dense(units=self.third_layer, activation='relu'))
        self.neural_network.add(Dense(units=3, activation='softmax'))
        
        opt = Adam(self.learning_rate)
        self.neural_network.compile(loss='mse', optimizer=opt)
        self.neural_network.summary()
    
    def render_network(self):
        if self.last_decision is None or self.last_state is None:
            return           
        
        # compute distance between layers
        network_layers = self.neural_network.layers
        network_layers_count = len(network_layers)
        
        screen_division = self.game.window_width / network_layers_count
        STEP_SIZE = 1.5
        CIRCLE_SIZE = 5
        DISTANCE_LENGTH = 16
        step = 1
        for i in range(network_layers_count):
            for j in range(network_layers[i].units):
                y = int((self.game.window_height + 200) / 2 + (j * DISTANCE_LENGTH) - (network_layers[i].units - 1)/2 * DISTANCE_LENGTH)
                x = int(self.game.window_width + step * screen_division)
                
                fill_factor = 0
                if i == 0:
                    fill_factor = int(self.last_state[j] * 255)
                elif i == network_layers_count - 1:
                    fill_factor = int(self.last_decision[j] * 255)
                    
                # draw connections
                if i < network_layers_count - 1:
                    for k in range(network_layers[i + 1].units):
                        y2 = int((self.game.window_height + 200) / 2 + (k * DISTANCE_LENGTH) - (network_layers[i + 1].units - 1)/2 * DISTANCE_LENGTH)
                        x2 = int(self.game.window_width + (step + STEP_SIZE) * screen_division)
                        
                        fill_factor_line = 60
                        # input layer
                        if i == 0:
                            fill_factor_line = fill_factor / 2 + 40
                        pygame.gfxdraw.line(self.game._display_surf, x + 2, y, x2, y2, (fill_factor_line, fill_factor_line, fill_factor_line, fill_factor_line))
                
                pygame.gfxdraw.filled_circle(self.game._display_surf, x, y, CIRCLE_SIZE, (fill_factor, fill_factor, fill_factor))
                pygame.gfxdraw.aacircle(self.game._display_surf, x, y, CIRCLE_SIZE, (255, 255, 255))
            step += STEP_SIZE