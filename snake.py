from constants import Constants as Cts

class Snake():

    def __init__(self, color, size, i, j, game_matrix):
        self.pixels = []
        self.live = True
        self.can_move = True
        self.speed = 0.5
        self.dj = 0
        self.di = -self.speed
        self.size = size
        self.grew = True # initially grew from nothing to something ;)
        self.receivedLeaderBoard = False # initially no one received leaderboard

        for c in range(i, i + size):
            self.pixels.append({
                    "i": c,
                    "j": j,
                    "c": color
                })
            game_matrix.pixel(c, j)["state"] = Cts.STATE_BUSY

    def clear(self, game_matrix):
        for pixel in self.pixels:
            game_matrix.pixel(int(pixel["i"]), int(pixel["j"]))["state"] = Cts.STATE_EMPTY

    def kill(self):
        self.live = False

    def getPixelsStr(self):
        pixels_str = ""
        for pixel in self.pixels:
            pixels_str = pixels_str + chr(int(pixel["i"])) + chr(int(pixel["j"])) + chr(int(pixel["c"]))

        return pixels_str

    def increaseSize(self):
        self.pixels.insert(0, self.pixels[0].copy())
        if (self.size < 127):
            self.size = self.size + 1
            self.grew = True

    def walk(self, previous_i, previous_j):
        self.pixels[0]["i"], previous_i = previous_i, int(self.pixels[0]["i"])
        self.pixels[0]["j"], previous_j = previous_j, int(self.pixels[0]["j"])
        
        for i in range(1, len(self.pixels)):
            self.pixels[i]["i"], previous_i = previous_i, self.pixels[i]["i"]
            self.pixels[i]["j"], previous_j = previous_j, self.pixels[i]["j"]

        return previous_i, previous_j
    
    def getHead(self):
        return self.pixels[0]
    
    def move(self, key):
        if not self.live or not self.can_move:
            return

        # KEY_UP
        if key == "0":
            if (self.di == 0):
                self.dj = 0
                self.pixels[0]["j"] = int(self.pixels[0]["j"])
                self.di = -self.speed
                self.can_move = False

        # KEY_DOWN
        elif key == "1":
            if (self.di == 0):
                self.dj = 0
                self.pixels[0]["j"] = int(self.pixels[0]["j"])
                self.di = self.speed
                self.can_move = False

        # KEY_LEFT
        elif key == "2":
            if (self.dj == 0):
                self.dj = -self.speed
                self.di = 0
                self.pixels[0]["i"] = int(self.pixels[0]["i"])
                self.can_move = False

        # KEY_RIGHT
        elif key == "3":
            if (self.dj == 0):
                self.dj = self.speed
                self.di = 0
                self.pixels[0]["i"] = int(self.pixels[0]["i"])
                self.can_move = False
