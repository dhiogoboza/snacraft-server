import os

from game import Game
from net import Client

from flask import Flask, render_template
from flask_sockets import Sockets

# game config
LINES = 128
COLUMNS = 128
SLEEP_TIME = 0.100

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
def handle(ws):
    # new client connected
    client = Client(ws)
     
    game.sendMap(client)

    # wait for snake's nickname
    client.nickname = ws.receive()

    game.addClient(client)
    game.sendHead(client)

    while not ws.closed:
        # handle incoming messages
        client.data = ws.receive()

        if client.data and client.data[0] == '1':
            game.moveSnake(client, client.data[2])

    # terminate connection
    game.removeClient(client)
