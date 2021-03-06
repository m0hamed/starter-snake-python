import os
import time

import cherrypy

from game import Game

class Battlesnake(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return {
            "apiversion": "1",
            "author": "mheikal",
            "color": "#00eeff", 
            "head": "silly",
            "tail": "bwc-ice-skate",
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        #data = cherrypy.request.json

        print("START")
        return "ok"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        start = time.time()
        data = cherrypy.request.json

        move = Game(data).get_best_move()
        end = time.time()
        print(f'elapsed time: {end-start}')

        print(f"MOVE: {move}")
        return {"move": move}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        #data = cherrypy.request.json

        print("END")
        return "ok"


if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
