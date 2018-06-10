import os

from game import Game
from client import Client
from constants import Constants as Cts

from flask import Flask, render_template
from flask_sockets import Sockets

# game config
LINES = 150
COLUMNS = 150
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

    ws.send(
        message=",".join([Cts.MESSAGE_PLAYERS_SIZE, chr(len(game.clients))]),
        binary=True)

    # FIXME: find a way to check here if client is still present

    game.sendMap(client)

    # wait for snake's data
    data = ws.receive()

    if data == None:
        ws.close()
        return

    data_split = data.split(",")

    data = data_split[0]
    if (len(data) > 10):
        data = data[0:10]

    client.setNickname(data)

    nickname = client.nickname

    print(nickname, "connected")

    game.addClient(client, int(data_split[1]))
    game.sendClientData(client)

    data_split = None

    while not ws.closed:
        # handle incoming messages
        data = ws.receive()

        if data and data[0] == '1':
            game.moveSnake(client, data[2])

    # terminate connection
    game.removeClient(client)

    print(nickname, "disconnected")
