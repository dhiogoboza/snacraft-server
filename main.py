import os

from game import Game
from client import Client
from botmanager import BotManager
from constants import Constants as Cts

from flask import Flask, render_template
from flask_sockets import Sockets

game = Game(Cts.LINES, Cts.COLUMNS, Cts.SLEEP_TIME)
bot_manager = BotManager(game, Cts.MAX_BOTS, Cts.SLEEP_TIME * 5)

game.init(bot_manager)
bot_manager.addBots(0)

bot_manager.start()
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
    client.sendMessage("".join([Cts.MESSAGE_PLAYERS_SIZE, chr(len(game.clients))]), binary=True)

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
