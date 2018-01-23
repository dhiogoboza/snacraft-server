import sys
import signal

from game import Game
from net import Client, Connector
from SimpleWebSocketServer import SimpleWebSocketServer

LINES = 24
COLUMNS = 24
PORT = 8888
SLEEP_TIME = 0.200

game = None
server = None

def signal_handler(signal, frame):
    global game
    global server
    
    print('\rShutting down')
    
    if not game == None:
        print('Closing game')
        
        game.close()

    sys.exit(0)

def main():
    global game
    global server
    
    columns = COLUMNS
    lines = LINES
    port = PORT
    sleep_time = SLEEP_TIME
    
    if len(sys.argv) > 1:
        for i in range(1, len(sys.argv)):
            if sys.argv[i] == '-p':
                port = int(sys.argv[i + 1])
            elif sys.argv[i] == '-s':
                split = sys.argv[i + 1].split('x')
                
                columns = int(split[0])
                lines = int(split[1])
            elif sys.argv[i] == '-t':
                sleep_time = float(sys.argv[i + 1])
                
    game = Game(lines, columns, sleep_time)
    game.init()
    
    listener = Connector(game)
    Client.listener = listener
    
    server = SimpleWebSocketServer('', port, Client)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    game.start()
    server.serveforever()

if __name__ == "__main__":
    main()


