#https://github.com/dpallot/simple-websocket-server
from SimpleWebSocketServer import WebSocket
from game import Game
import sys, traceback

class Connector():
    
    def __init__(self, game):
        self.game = game
    
    def onConnection(self, client):
        print(client.address, 'connected')
        
        client.sendMessage(chr(0) + "," + str(self.game.getMapStr()))
        
        self.game.addClient(client)
        print(client.address, 'snake created connected')
    
    def onMessage(self, client):
        #print(client.data, "-", 'received')
        
        if (client.data[0] == '1'):
            self.game.moveSnake(client.address, client.data[2])
            
        #elif (client.data[0] == '2'):
            # Request snakes
            #client.sendMessage("2," + str(self.game.getSnakes()))
            
    def onClose(self, client):
        print(client.address, 'closed')
        self.game.removeClient(client)


class Client(WebSocket):

    listener = None
    methods = {"0": "onConnection", "1": "onMessage", "2": "onClose"}
    
    def callListener(self, option):
        try:
            if option == 0:
                Client.listener.onConnection(self)
            elif option == 1:
                Client.listener.onMessage(self)
            elif option == 2:
                Client.listener.onClose(self)
        except:
            print("Unexpected error:", sys.exc_info(), "method =", Client.methods[str(option)])
            traceback.print_exc(file=sys.stdout)

    def handleConnected(self):
        Client.callListener(self, 0)
        
    def handleMessage(self):
        Client.callListener(self, 1)

    def handleClose(self):
        Client.callListener(self, 2)
