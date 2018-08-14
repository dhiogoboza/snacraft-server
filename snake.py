from constants import Constants as Cts
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
        self.pixels_str = ""
        self.snake_data_str = ""
        self.snake_body_str = ""
        self.snake_data_array = [chr(client_id), chr(self.color), 0, 0]
        self.snake_body_arr = []

        for c in range(i, i + size):
            self.pixels.append({
                    "i": i,
                    "j": j,
                    "c": color
                })

        map_pixel = game_matrix.pixel(i, j)
        #if map_pixel["state"] == Cts.STATE_EMPTY:
        map_pixel["client"] = client_id
        map_pixel["state"] = Cts.STATE_BUSY

        self.updateSnakeDataStr()
        self.updateSnakeBodyStr()

    def clear(self, game_matrix):
        for pixel in self.pixels:
            pix = game_matrix.pixel(int(pixel["i"]), int(pixel["j"]))
            pix["state"] = pix["client"] = Cts.STATE_EMPTY

    def kill(self):
        self.live = False

    def updateSnakeDataStr(self):
        self.snake_data_array[2] = chr(self.size >> 8)
        self.snake_data_array[3] = chr(self.size & 0xFF)

        self.snake_data_str = "".join(self.snake_data_array)

        self.updateSnakeStr()

    def updateSnakeBodyStr(self, np=None):
        if np:
            # only append new item in array
            self.snake_body_arr.append(chr(int(np["i"])))
            self.snake_body_arr.append(chr(int(np["j"])))
        else:
            # init all array
            self.snake_body_arr = []

            # append body pixels
            for pixel in self.pixels:
                self.snake_body_arr.append(chr(int(pixel["i"])))
                self.snake_body_arr.append(chr(int(pixel["j"])))

        self.snake_body_str = "".join(self.snake_body_arr)
        self.updateSnakeStr()

    def updateSnakeStr(self):
        # join snake data and body
        self.pixels_str = self.snake_data_str + self.snake_body_str

    def getPixelsStr(self):
        """
        self.snake_data_array[2] = chr(0)
        self.snake_data_array[3] = chr(1)
        str_temp = "".join(self.snake_data_array)
        return "".join([str_temp, chr(int(self.pixels[0]["i"])), chr(int(self.pixels[0]["j"]))])
        """
        
        return self.pixels_str

    def increaseSize(self):
        if (self.size < Cts.MAX_SNAKE_SIZE):
            new_pixel = self.pixels[0].copy()
            self.pixels.insert(0, new_pixel)
            self.size = self.size + 1
            self.grew = True

            self.updateSnakeBodyStr(np=new_pixel)
            self.updateSnakeDataStr()

    def walk(self, previous_i, previous_j):
        curr_pixel = self.pixels[0]
        curr_pixel["i"], previous_i = previous_i, int(curr_pixel["i"])
        curr_pixel["j"], previous_j = previous_j, int(curr_pixel["j"])

        c = 0
        self.snake_body_arr[c] = chr(int(curr_pixel["i"]))
        c+=1
        self.snake_body_arr[c] = chr(int(curr_pixel["j"]))
        c+=1

        for i in range(1, len(self.pixels)):
            curr_pixel = self.pixels[i]

            curr_pixel["i"], previous_i = previous_i, curr_pixel["i"]
            curr_pixel["j"], previous_j = previous_j, curr_pixel["j"]

            self.snake_body_arr[c] = chr(int(curr_pixel["i"]))
            c+=1
            self.snake_body_arr[c] = chr(int(curr_pixel["j"]))
            c+=1

        # update snake str
        self.snake_body_str = "".join(self.snake_body_arr)
        self.updateSnakeStr()

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
