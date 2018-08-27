import utils

from constants import Constants as Cts
from pixel import Pixel
from Queue import *

class Snake():

    def __init__(self, color, client_id, size, i, j, game_matrix):
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
        self.last_key = Cts.KEY_UP
        self.moved = False
        self.client_id = client_id

        for c in range(i, i + size):
            self.pixels.append(Pixel(i, j, color))

        map_pixel = game_matrix.pixel(i, j)
        map_pixel.client = client_id
        map_pixel.state = Cts.STATE_BUSY

    def clear(self, game_matrix):
        for pixel in self.pixels:
            pix = game_matrix.pixel(utils.toint(pixel.i), utils.toint(pixel.j))
            pix.state = pix.client = Cts.STATE_EMPTY

    def kill(self):
        self.live = False

    def getPixelsStr(self):
        pixels_str = [chr(self.client_id), chr(self.color), chr(self.size >> 8), chr(self.size & 0xFF)]
        for pixel in self.pixels:
            pixels_str.append(pixel.getIChar())
            pixels_str.append(pixel.getJChar())

        return "".join(pixels_str)

    def increaseSize(self, game_map):
        if (self.size < Cts.MAX_SNAKE_SIZE):
            new_pixel = self.pixels[self.size - 1].copy()
            self.pixels.append(new_pixel)
            self.size = self.size + 1
            self.grew = True
            # TODO: enable this?
            #game_map.pixel(new_pixel["i"], new_pixel["j"])["state"] += Cts.STATE_BUSY

    def incrementSpeed(self):
        aux = self.speed
        self.speed = self.speed + Cts.SPEED_INCREMENT
        # FIXME: not sending speed message when max speed is reached
        if self.speed > 1:
            self.speed = 1

        return self.speed != aux

    def walk(self, previous_i, previous_j):
        self.pixels[0].i, previous_i = previous_i, self.pixels[0].i
        self.pixels[0].j, previous_j = previous_j, self.pixels[0].j

        for i in range(1, len(self.pixels)):
            self.pixels[i].i, previous_i = previous_i, self.pixels[i].i
            self.pixels[i].j, previous_j = previous_j, self.pixels[i].j

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
            self.last_key = key_to_add
            self.doMovement(key_to_add)
        elif (self.keys_buffer.qsize() < Cts.KEYS_MAX_BUFFER):
            if key_to_add != self.last_key and Cts.POSSIBLE_MOVEMENTS[self.last_key][key_to_add]:
                self.last_key = key_to_add
                if self.can_move:
                    self.doMovement(key_to_add)
                else:
                    self.keys_buffer.put(key_to_add)

    def doMovement(self, key):
        # KEY_UP
        if key == Cts.KEY_UP:
            if (self.di == 0):
                self.dj = 0
                self.pixels[0].j = utils.toint(self.pixels[0].j)
                self.di = -self.speed
                self.can_move = False
                self.direction = Cts.DIRECTION_UP

        # KEY_DOWN
        elif key == Cts.KEY_DOWN:
            if (self.di == 0):
                self.dj = 0
                self.pixels[0].j = utils.toint(self.pixels[0].j)
                self.di = self.speed
                self.can_move = False
                self.direction = Cts.DIRECTION_DOWN

        # KEY_LEFT
        elif key == Cts.KEY_LEFT:
            if (self.dj == 0):
                self.dj = -self.speed
                self.di = 0
                self.pixels[0].i = utils.toint(self.pixels[0].i)
                self.can_move = False
                self.direction = Cts.DIRECTION_LEFT

        # KEY_RIGHT
        elif key == Cts.KEY_RIGHT:
            if (self.dj == 0):
                self.dj = self.speed
                self.di = 0
                self.pixels[0].i = utils.toint(self.pixels[0].i)
                self.can_move = False
                self.direction = Cts.DIRECTION_RIGHT
