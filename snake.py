from constants import Constants as Cts
from Queue import *

KEYS_MAX_BUFFER = 3

class Snake():

    def __init__(self, color, size, i, j, game_matrix):
        self.pixels = []
        self.live = True
        self.can_move = True
        self.speed = Cts.INITIAL_SPEED
        self.dj = 0
        self.di = -self.speed
        self.direction = Cts.DIRECTION_UP
        self.size = size
        self.grew = True # initially grew from nothing to something ;)
        self.color = color
        self.keys_buffer = Queue()
        self.last_key = -1
        self.moved = False

        for c in range(i, i + size):
            self.pixels.append({
                    "i": c,
                    "j": j,
                    "c": color
                })
            map_pixel = game_matrix.pixel(c, j)

            if map_pixel["state"] == Cts.STATE_EMPTY:
                game_matrix.pixel(c, j)["state"] = Cts.STATE_BUSY

    def clear(self, game_matrix):
        for pixel in self.pixels:
            game_matrix.pixel(int(pixel["i"]), int(pixel["j"]))["state"] = Cts.STATE_EMPTY

    def kill(self):
        self.live = False

    def getPixelsStr(self):
        pixels_str = ""
        for pixel in self.pixels:
            pixels_str = pixels_str + chr(int(pixel["i"])) + chr(int(pixel["j"]))

        return pixels_str

    def increaseSize(self):
        if (self.size < Cts.MAX_SNAKE_SIZE):
            self.pixels.insert(0, self.pixels[0].copy())
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

    def checkMovement(self):
        if not self.keys_buffer.empty():
            self.doMovement(self.keys_buffer.get())

    def move(self, key_to_add):
        if not self.live:
            return

        if self.keys_buffer.qsize() == 0 and self.can_move:
            self.doMovement(key_to_add)
        elif (self.keys_buffer.qsize() < KEYS_MAX_BUFFER):
            if key_to_add != self.last_key:
                self.last_key = key_to_add
                self.keys_buffer.put(key_to_add)
                if self.can_move:
                    self.doMovement(self.keys_buffer.get())

    def doMovement(self, key):
        # KEY_UP
        if key == Cts.KEY_UP:
            if (self.di == 0):
                self.dj = 0
                self.pixels[0]["j"] = int(self.pixels[0]["j"])
                self.di = -self.speed
                self.can_move = False
                self.direction = Cts.DIRECTION_UP

        # KEY_DOWN
        elif key == Cts.KEY_DOWN:
            if (self.di == 0):
                self.dj = 0
                self.pixels[0]["j"] = int(self.pixels[0]["j"])
                self.di = self.speed
                self.can_move = False
                self.direction = Cts.DIRECTION_DOWN

        # KEY_LEFT
        elif key == Cts.KEY_LEFT:
            if (self.dj == 0):
                self.dj = -self.speed
                self.di = 0
                self.pixels[0]["i"] = int(self.pixels[0]["i"])
                self.can_move = False
                self.direction = Cts.DIRECTION_LEFT

        # KEY_RIGHT
        elif key == Cts.KEY_RIGHT:
            if (self.dj == 0):
                self.dj = self.speed
                self.di = 0
                self.pixels[0]["i"] = int(self.pixels[0]["i"])
                self.can_move = False
                self.direction = Cts.DIRECTION_RIGHT
