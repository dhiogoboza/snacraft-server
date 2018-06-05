class Client():
    """
    Wrapper client class of geventwebsocket.websocket.WebSocket to
    interface with Game class.
    """
    def __init__(self, ws, bot=False):
        self.ws = ws
        self.id = 0
        #self.address = self.ws.environ['HTTP_SEC_WEBSOCKET_KEY']
        self.nickname = ''
        self.snake = None
        self.bot = bot
        
    def setSnake(self, s):
        self.snake = s
        
    def setId(self, client_id):
        self.id = client_id
        # Msg nickname [ ID | SIZE | NICKNAME ]
        self.nickname = chr(self.id) + chr(len(self.nickname)) + self.nickname
    
    def setNickname(self, nickname):
        self.nickname = nickname

    def sendMessage(self, message, binary=False):
        if self.bot:
            return

        if not self.ws.closed:
            self.ws.send(message, binary=binary)

    def close(self):
        if self.bot:
            return

        if not self.ws.closed:
            self.ws.close()
