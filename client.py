class Client():
    """
    Wrapper client class of geventwebsocket.websocket.WebSocket to
    interface with Game class.
    """
    def __init__(self, ws, bot=False, manager=None):
        self.ws = ws
        self.id = 0
        self.nickname = ''
        self.snake = None
        self.bot = bot
        self.manager = manager
        
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
            self.manager.removeBot(self)
            return

        if not self.ws.closed:
            self.ws.close()
