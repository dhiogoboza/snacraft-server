class Client():
    """
    Wrapper client class of geventwebsocket.websocket.WebSocket to
    interface with Game class.
    """
    def __init__(self, ws):
        self.ws = ws
        self.id = 0
        self.address = self.ws.environ['HTTP_SEC_WEBSOCKET_KEY']
        self.nickname = ''
        self.snake = None
        self.ranking = 1
        self.rankingChanged = True # initially no ranking is set
        
    def setSnake(self, s):
        self.snake = s
        
    def setId(self, client_id):
        self.id = client_id
        
    def setRanking(self, ranking):
        self.rankingChanged = (self.ranking != ranking)
        self.ranking = ranking

    def sendMessage(self, message, binary=False):
        if not self.ws.closed:
            self.ws.send(message, binary=binary)

    def close(self):
        if not self.ws.closed:
            self.ws.close()
