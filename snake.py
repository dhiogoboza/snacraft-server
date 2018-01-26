STATE_EMPTY = 0
STATE_BUSY = 1

class Snake():

    def __init__(self, size, i, j, game_matrix):
        self.pixels = []
        self.live = True
        self.can_move = True
        self.dj = 0
        self.di = -1
        self.size = size
        self.grew = True # initially grew from nothing to something ;)

        for c in range(i, i + size):
            self.pixels.append({
                    "i": c,
                    "j": j,
                    "c": 2
                })
            game_matrix[c][j]["state"] = STATE_BUSY

    def clear(self, game_matrix):
        for pixel in self.pixels:
            game_matrix[pixel["i"]][pixel["j"]]["state"] = STATE_EMPTY

    def kill(self):
        self.live = False

    def getPixelsStr(self):
        pixels_str = ""
        for pixel in self.pixels:
            pixels_str = pixels_str + chr(pixel["i"]) + chr(pixel["j"]) + chr(pixel["c"])

        return pixels_str

    def increaseSize(self):
        self.pixels.insert(0, self.pixels[0].copy())
        self.size = self.size + 1
        self.grew = True

    def walk(self, previous_i, previous_j):
        for pixel in self.pixels:
            pixel["i"], previous_i = previous_i, pixel["i"]
            pixel["j"], previous_j = previous_j, pixel["j"]

        return previous_i, previous_j

    def move(self, key):
        if not self.live or not self.can_move:
            return

        # KEY_UP
        if key == "0":
            if (self.di == 0):
                self.dj = 0
                self.di = -1
                self.can_move = False

        # KEY_DOWN
        elif key == "1":
            if (self.di == 0):
                self.dj = 0
                self.di = 1
                self.can_move = False

        # KEY_LEFT
        elif key == "2":
            if (self.dj == 0):
                self.dj = -1
                self.di = 0
                self.can_move = False

        # KEY_RIGHT
        elif key == "3":
            if (self.dj == 0):
                self.dj = 1
                self.di = 0
                self.can_move = False
