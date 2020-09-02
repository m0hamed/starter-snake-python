#!/usr/bin/env python3
import time

DEBUG = True

SNAKE = 1 << 1
HEAD = 1 << 2
MY_SNAKE = 1 << 3

POSSIBLE_MOVES = {
    'up': (0, 1),
    'down': (0, -1),
    'left': (-1, 0),
    'right': (1, 0),
}

STAY_ALIVE = 0
STARVING = 1

original_print = print
def print(*args, **kwargs):
    if DEBUG:
        original_print(*args, **kwargs)


def get_empty_board(board_size, fill=0):
    board = []
    for _ in range(board_size):
        board.append([fill] * board_size)
    return board


def clone_board(old_board):
    new_board = get_empty_board(len(old_board))
    for i in range(len(old_board)):
        for j in range(len(old_board[i])):
            new_board[i][j] = old_board[i][j]
    return new_board


def flood_count(real_board, x, y):
    s = time.time()
    R = C = len(real_board)
    fake_board = clone_board(real_board)
    if fake_board[x][y] > 0: return 0

    def dfs(r, c):
        count = 0
        if fake_board[r][c] == 0:
            fake_board[r][c] = 1
            count += 1
            if r >= 1: count += dfs(r - 1, c)
            if r + 1 < R: count += dfs(r + 1, c)
            if c >= 1: count += dfs(r, c - 1)
            if c + 1 < C: count += dfs(r, c + 1)
        return count

    ret = dfs(x, y)
    print(f'flood_count elapsted time: {time.time()-s}')
    return ret


class Game:
    def __init__(self, game_state):
        self.my_head_x = None
        self.my_head_y = None
        self.my_snake = None
        self.my_health = None
        self.food_board = None

        self.board_size = game_state['board']['height']
        self.board = get_empty_board(self.board_size)
        self._add_food(game_state['board']['food'])
        self._add_snakes(game_state['board']['snakes'])
        self._set_my_snake(game_state['you'])

    def _add_food(self, food_pos):
        self.food_board = get_empty_board(self.board_size)
        self.flood_fill(self.food_board, food_pos)

    def flood_fill(self, board, food_pos):
        s = time.time()
        queue = []
        visited = get_empty_board(len(board))
        for pos in food_pos:
            x, y = (pos['x'], pos['y'])
            queue.append((x, y, 0))
            self.set_at(x, y, 0, board=board)
            self.set_at(x, y, 1, board=visited)

        def bfs(q):
            while q:
                x, y, distance = q.pop(0)
                for move, delta in POSSIBLE_MOVES.items():
                    new_x = x + delta[0]
                    new_y = y + delta[1]
                    if self.is_out_of_bounds(new_x, new_y):
                        continue
                    if not self.get_at(new_x, new_y, board=visited):
                        self.set_at(x, y, distance+1, board=board)
                        self.set_at(x, y, 1, board=visited)
                        q.append((new_x, new_y, distance+1))
        bfs(queue)
        print(f'flood_fill elapsted time: {time.time()-s}')

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
        board_y = self.board_size - y - 1
        board_x = x
        return board_y, board_x

    def set_at(self, x, y, value, append=False, board=None):
        if board is None:
            board = self.board
        i, j = self.to_board_idx(x, y)
        if append:
            board[i][j] |= value
        else:
            board[i][j] = value

    def get_at(self, x, y, board=None):
        if board is None:
            board = self.board
        i, j = self.to_board_idx(x, y)
        return board[i][j]

    def get_safe_move(self):
        for move, delta in POSSIBLE_MOVES.items():
            new_x = self.my_head_x + delta[0]
            new_y = self.my_head_y + delta[1]
            if self.is_out_of_bounds(new_x, new_y):
                continue
            if self.is_empty(new_x, new_y):
                return move

    def is_out_of_bounds(self, x, y):
        if x < 0 or x >= self.board_size:
            return True
        if y < 0 or y >= self.board_size:
            return True
        return False

    def is_empty(self, x, y):
        return self.get_at(x, y) == 0

    def has_snake(self, x, y):
        return bool(self.get_at(x, y) & SNAKE)

    def is_close_to_other_head(self, x, y):
        count = 0
        for move, delta in POSSIBLE_MOVES.items():
            new_x = x + delta[0]
            new_y = y + delta[1]
            if self.is_out_of_bounds(new_x, new_y):
                continue
            value = self.get_at(new_x, new_y)
            if value & HEAD and not (value & MY_SNAKE):
                count += 1
        return count

    def is_close_to_wall(self, x, y):
        count = 0
        for move, delta in POSSIBLE_MOVES.items():
            new_x = x + delta[0]
            new_y = y + delta[1]
            if self.is_out_of_bounds(new_x, new_y):
                count +=1
        return count

    def get_possible_moves(self):
        possible_moves = {}
        for move, delta in POSSIBLE_MOVES.items():
            new_x = self.my_head_x + delta[0]
            new_y = self.my_head_y + delta[1]
            if self.is_out_of_bounds(new_x, new_y):
                print(f'{move}=({new_x}, {new_y}) is out of bounds')
                continue
            if self.has_snake(new_x, new_y):
                print(f'{move}=({new_x}, {new_y}) has snake')
                continue
            possible_moves[move] = (new_x, new_y)
        return possible_moves

    def rank_moves(self, goal=STAY_ALIVE):
        s = time.time()
        move_rank = {}
        for move, (new_x, new_y) in self.get_possible_moves().items():
            print(f'possible move {move}=({new_x}, {new_y})')
            food_distance = self.get_at(new_x, new_y, board=self.food_board)
            print(f'{move}=({new_x}, {new_y}) is {food_distance} away from food')
            close_to_other_head = self.is_close_to_other_head(new_x, new_y)
            if close_to_other_head:
                print(f'{move}=({new_x}, {new_y}) is close to other head')
            close_to_wall = self.is_close_to_wall(new_x, new_y)
            print(f'{move}=({new_x}, {new_y}) is close to {close_to_wall} walls')
            count_open_squares = self.count_open_squares(new_x, new_y)
            print(
                f'{move}=({new_x}, {new_y}) has {count_open_squares} open squares'
            )
            if goal==STARVING:
                ranking_tuple = (food_distance, -count_open_squares, close_to_wall, close_to_other_head)
            else:
                ranking_tuple = (-count_open_squares, close_to_wall + food_distance, 0, close_to_other_head)
            move_rank[move] = ranking_tuple
        print(f'rank_moves elapsted time: {time.time()-s}')
        return move_rank

    def count_open_squares(self, x, y):
        return flood_count(self.board, x, y)

    def print_board(self, show_head=True, board=None):
        if board is None:
            board = self.board
        for i in range(len(board)):
            for j in range(len(board[i])):
                if show_head and board[i][j] & (MY_SNAKE | HEAD) == (MY_SNAKE | HEAD):
                    pos = '  X,'
                else:
                    pos = '{:3d},'.format(board[i][j])
                print(pos, end='')
            print()

    def get_best_move(self):
        print('Food Board:')
        self.print_board(show_head = False, board = self.food_board)
        print('Game Board:')
        print(f'I am at ({self.my_head_x}, {self.my_head_y})')
        self.print_board(board = self.board)
        goal = STAY_ALIVE
        if self.my_health < 20:
            goal = STARVING
        # lower is better
        moves = self.rank_moves(goal=goal)
        best_moves = sorted(moves.items(), key=lambda m: m[1])
        print(best_moves)
        return best_moves[0][0]