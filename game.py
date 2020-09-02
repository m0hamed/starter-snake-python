#!/usr/bin/env python3

DEFAULT_BOARD_SIZE = 11
FOOD = 1 << 0
SNAKE = 1 << 1
HEAD = 1 << 2
MY_SNAKE = 1 << 3

POSSIBLE_MOVES = {
    'up': (0,1),
    'down': (0,-1),
    'left': (-1,0),
    'right': (1,0),
}

STAY_ALIVE = 0
GET_FOOD = 1

class Game:
    def __init__(self, game_state):
        self.my_head_x = None
        self.my_head_y = None
        self.my_snake = None
        self.my_health = None
        self.board_size = game_state['board']['height']
        self.board = [[0]*self.board_size]*self.board_size
        self._add_food(game_state['board']['food'])
        self._add_snakes(game_state['board']['snakes'])
        self._set_my_snake(game_state['you'])

    def _add_food(self, food_pos):
        for pos in food_pos:
            self.set_at(pos['x'], pos['y'], FOOD)
    
    def _add_snakes(self, snakes):
        for snake in snakes:
            for pos in snake['body']:
                self.set_at(pos['x'], pos['y'], SNAKE)
            head = snake['head']
            self.set_at(head['x'], head['y'], HEAD, append=True)

    def _set_my_snake(self, snake):
        for pos in snake['body']:
            self.set_at(pos['x'], pos['y'], MY_SNAKE, append=True)
        self.my_health = snake['health']
        self.my_head_x = snake['head']['x']
        self.my_head_y = snake['head']['y']
        self.my_snake = snake
    
    def to_board_idx(self, x, y):
        board_y = self.board_size-y-1
        board_x = x - 1
        return board_y, board_x
    
    def set_at(self, x, y, value, append=False):
        i, j = self.to_board_idx(x, y)
        if append:
            self.board[i][j] |= value
        else:
            self.board[i][j] = value

    def get_at(self, x, y):
        i, j = self.to_board_idx(x, y)
        return self.board[i][j]
    
    def get_safe_move(self):
        for move, delta in POSSIBLE_MOVES.items():
            new_x = self.my_head_x + delta[0]
            new_y = self.my_head_y + delta[1]
            if self.is_out_of_bounds(new_x, new_y):
                continue
            if self.is_empty(new_x, new_y):
                return move
    
    def is_out_of_bounds(self, x, y):
        if x < 0 or x > self.board_size:
            return True
        if y < 0 or y > self.board_size:
            return True
        return False
    
    def is_empty(self, x, y):
        return self.get_at(x, y) == 0

    def has_snake(self, x, y):
        return bool(self.get_at(x, y) & SNAKE)
    
    def is_close_to_other_head(self, x, y):
        for move, delta in POSSIBLE_MOVES.items():
            new_x = x + delta[0]
            new_y = y + delta[1]
            if self.is_out_of_bounds(new_x, new_y):
                continue
            value = self.get_at(new_x, new_y)
            if value & HEAD and not (value & MY_SNAKE):
                return True

    def rank_moves(self, goal=STAY_ALIVE):
        move_rank = {}
        for move, delta in POSSIBLE_MOVES.items():
            new_x = self.my_head_x + delta[0]
            new_y = self.my_head_y + delta[1]
            move_rank[move] = 0
            if self.is_out_of_bounds(new_x, new_y):
                print(f'{move}=({new_x}, {new_y}) is out of bounds')
                move_rank[move] += -100
                continue
            if self.has_snake(new_x, new_y):
                print(f'{move}=({new_x}, {new_y}) has snake')
                move_rank[move] = -100
                continue
            if self.get_at(new_x, new_y) & FOOD:
                print(f'{move}=({new_x}, {new_y}) has food')
                if goal == GET_FOOD:
                    move_rank[move] = 10
                else:
                    move_rank[move] = -5
            #if self.is_empty(new_x, new_y):
            #    print(f'{move}=({new_x}, {new_y}) is empty')
            #    move_rank[move] = 0
            if self.is_close_to_other_head(new_x, new_y):
                print(f'{move}=({new_x}, {new_y}) is close to other head')
                move_rank[move] -= 5
        return move_rank

    def print_board(self):
        for i in range(len(board)):
            for j in range(len(board[i])):
                print('{:2d},'.format(board[i][j]), end='')
        print()
        
    def get_best_move(self):
        self.print_board()
        moves = self.rank_moves()
        best_moves = sorted(moves.items(), key=lambda m: -m[1])
        print(best_moves)
        return 'right'
        return best_moves[0][0]