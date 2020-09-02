import time
from game import Game

def main(request):
    print(request)
    if request.path == '/':
        return index(request)
    if request.path == '/start':
        return noop(request)
    if request.path == '/end':
        return noop(request)
    if request.path == '/move':
        return move(request)
    return request.path

def index(request):
        return {
            "apiversion": "1",
            "author": "mheikal",
            "color": "#00ffff", 
            "head": "silly",
            "tail": "bwc-ice-skate",
        }

def noop(request):
    return 'OK'

def move(request):
    start = time.time()
    data = request.get_json(silent=True)

    move = Game(data).get_best_move()
    end = time.time()
    print(f'elapsed time: {end-start}')

    print(f"MOVE: {move}")
    return {"move": move}