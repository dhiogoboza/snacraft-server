from .snake import Snake

class SnakeBot(Snake):

    def __init__(self, color, client_id, size, i, j, game_matrix):
        Snake.__init__(self, color, client_id, size, i, j, game_matrix)
        self.keys_buffer = None

    def checkMovement(self):
        pass

    def move(self, key_to_add):
        if self.can_move:
            self.doMovement(key_to_add)
