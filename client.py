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
        # Msg nickname [ ID | SIZE | NICKNAME ]
        self.nickname = chr(self.id) + chr(len(self.nickname)) + self.nickname
    
    def setNickname(self, nickname):
        self.nickname = nickname
            
    def setRanking(self, ranking):
        self.rankingChanged = True
        self.ranking = ranking

    def sendMessage(self, message, binary=False):
        if not self.ws.closed:
            self.ws.send(message, binary=binary)

    def close(self):
        if not self.ws.closed:
            self.ws.close()
