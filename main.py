import os

from game import Game
from net import Client

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
     
    game.sendMap(client)

    # wait for snake's data
    data = ws.receive()
    data_split = data.split(",")
    
    client.nickname = data_split[0]
    
    if (len(client.nickname) > 15):
        client.nickname = client.nickname[0:15]
    
    print(client.nickname, "connected")

    game.addClient(client, int(data_split[1]))
    game.sendHead(client)

    while not ws.closed:
        # handle incoming messages
        data = ws.receive()

        if data and data[0] == '1':
            game.moveSnake(client, data[2])

    # terminate connection
    game.removeClient(client)
