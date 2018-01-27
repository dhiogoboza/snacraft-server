class Client():
    """
    Wrapper client class of geventwebsocket.websocket.WebSocket to
    interface with Game class.
    """
    def __init__(self, ws):
        self.ws = ws
        self.address = self.ws.environ['HTTP_SEC_WEBSOCKET_KEY']
        self.data = None
        self.nickname = ''

    def sendMessage(self, message):
        if not self.ws.closed:
            self.ws.send(message)

    def close(self):
        if not self.ws.closed:
            self.ws.close()
