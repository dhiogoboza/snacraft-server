import os
import sys

from game import Game
from net import Client

from flask import Flask, render_template
from flask_sockets import Sockets

# game config
LINES = 64
COLUMNS = 64
SLEEP_TIME = 0.200

game = None

# init game
columns = COLUMNS
lines = LINES
sleep_time = SLEEP_TIME

game = Game(lines, columns, sleep_time)
game.init()
game.start()

# init app
app = Flask(__name__)
app.debug = 'DEBUG' in os.environ

# init websocket
sockets = Sockets(app)

@sockets.route('/')
def echo(ws):
    # new client connected
    client = Client(ws)
    client.sendMessage(chr(0) + "," + str(game.getMapStr()))

    game.addClient(client)

    while not ws.closed:
        # handle incoming messages
        client.data = ws.receive()

        if client.data and client.data[0] == '1':
            game.moveSnake(client.address, client.data[2])

    # terminate connection
    game.removeClient(client)
