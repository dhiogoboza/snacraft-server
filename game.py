import random
import time

from threading import Thread

STATE_EMPTY = 0
STATE_BUSY = 1
MOB_MOVE_SPEED = 2
MOB_INCREASE = 3

class Game(Thread):

    def __init__(self, lines, columns, sleep_time):
        Thread.__init__(self)

        self.thread_exit = False
        self.lines = lines
        self.columns = columns
        self.sleep_time = sleep_time
        self.running = True
        self.matrix = []
        self.snakes = {}
        self.power_ups = {}

    def init(self):
        self.clients = []

        lines_1 = self.lines - 1
        columns_1 = self.columns - 1

        for i in range(0, self.lines):
            line = []
            for j in range(0, self.columns):
                it = STATE_BUSY if (i == 0) or (i == lines_1) or (j == 0) or (j == columns_1) else STATE_EMPTY
                line.append({
                        "i": i,
                        "j": j,
                        "it": it,
                        "state": it,
                        "mob": 0
                    })
            self.matrix.append(line)

        minor = int((self.lines if self.lines < self.columns else self.columns) * 0.8)

        for c in range(0, minor):
            self.generateRandomPowerUp(MOB_INCREASE)

    def getKey(self, i, j):
        return i * self.columns + j

    def generateRandomPowerUp(self, power_up_type):
        power_up = {}

        while True:
            i = random.randrange(1, self.lines - 1)
            j = random.randrange(1, self.columns - 1)

            if self.matrix[i][j]["mob"] == 0:
                break;

        power_up["i"] = i
        power_up["j"] = j
        power_up["type"] = power_up_type

        key = self.getKey(i, j)

        self.power_ups[key] = power_up
        self.matrix[i][j]["mob"] = power_up_type

    def addClient(self, client):
        self.clients.append(client)
        self.createSnake(client.address)

    def removeClient(self, client):
        if (client in self.clients):
            self.clients.remove(client)
            self.removeSnake(client.address)

    def getMapStr(self):
        to_return = str(self.lines) + "," + str(self.columns)

        for i in range(0, self.lines):
            for j in range(0, self.columns):
                to_return = to_return + "," + str(self.matrix[i][j]["it"])

        return to_return

    def createSnake(self, address):
        snake = {}
        snake["pixels"] = []
        snake["live"] = True
        snake["can_move"] = True
        snake["dj"] = 0
        snake["di"] = -1

        i = int(self.lines / 2)
        j = int(self.columns / 2) + len(self.snakes)

        for c in range(i, i + 5):
            snake["pixels"].append({
                    "i": c,
                    "j": j,
                    "c": 2
                })

            self.matrix[c][j]["state"] = STATE_BUSY

        self.snakes[address] = snake

    def removeSnake(self, address):
        snake = self.snakes[address]
        for i in range(0, len(snake["pixels"])):
            pixel = snake["pixels"][i]
            self.matrix[pixel["i"]][pixel["j"]]["state"] = STATE_EMPTY

        self.snakes.pop(address)

    def getSnakes(self):
        snakes = ""
        for k, snake in self.snakes.items():
            for pixel in snake["pixels"]:
                snakes = snakes + chr(pixel["i"]) + chr(pixel["j"]) + chr(pixel["c"])

        return snakes

    def getPowerUps(self):
        power_ups = ""
        for k, power_up in self.power_ups.items():
            power_ups = power_ups + chr(power_up["i"]) + chr(power_up["j"]) + chr(power_up["type"])

        return power_ups

    def moveSnake(self, address, key):
        snake = self.snakes[address]

        if not snake["live"] or not snake["can_move"]:
            return

        if key == "0":
            if (snake["di"] == 0):
                snake["dj"] = 0
                snake["di"] = -1
                snake["can_move"] = False
        elif key == "1":
            if (snake["di"] == 0):
                snake["dj"] = 0
                snake["di"] = 1
                snake["can_move"] = False
        elif key == "2":
            if (snake["dj"] == 0):
                snake["dj"] = -1
                snake["di"] = 0
                snake["can_move"] = False
        elif key == "3":
            if (snake["dj"] == 0):
                snake["dj"] = 1
                snake["di"] = 0
                snake["can_move"] = False

    def processMob(self, snake, pixel, i, j):
        pixel["mob"] = STATE_EMPTY

        key = self.getKey(i, j)
        power_up = self.power_ups[key]

        if power_up["type"] == MOB_INCREASE:
            pixels = snake["pixels"]
            pixels.append(pixels[len(pixels) - 1].copy())

        self.power_ups.pop(key)
        self.generateRandomPowerUp(power_up["type"])

    def close(self):
        self.running = False

        while not self.thread_exit:
            pass

        for client in self.clients:
            client.close()

        del self.matrix[:]
        self.snakes.clear()
        self.power_ups.clear()


    def run(self):
        previous_time = 0
        cur_time = 0

        while self.running:
            for k, snake in self.snakes.items():
                if not snake["live"]:
                    continue

                head = snake["pixels"][0]

                new_i = head["i"] + snake["di"]
                new_j = head["j"] + snake["dj"]

                pixel = self.matrix[new_i][new_j]

                if (pixel["state"] == STATE_BUSY):

                    snake["live"] = False

                    for i in range(0, self.lines):
                        line = ""
                        for j in range(0, self.columns):
                            line = line + ("0 " if self.matrix[i][j]["state"] == 1 else "  ")

                    continue

                if not (pixel["mob"] == 0):
                    self.processMob(snake, pixel, new_i, new_j)

                previous_i = new_i
                previous_j = new_j

                pixel["state"] = STATE_BUSY

                for i in range(0, len(snake["pixels"])):
                    pixel = snake["pixels"][i]

                    pixel["i"], previous_i = previous_i, pixel["i"]
                    pixel["j"], previous_j = previous_j, pixel["j"]

                self.matrix[previous_i][previous_j]["state"] = STATE_EMPTY
                snake["can_move"] = True

                # snakes iteration end

            message0 = chr(2)
            message2 = self.getSnakes() + self.getPowerUps()

            for client in self.clients:
                head = self.snakes[client.address]["pixels"][0]
                client.sendMessage("".join([message0, chr(head["i"]), chr(head["j"]), message2]))

            cur_time = time.time()
            elapsed_time = cur_time - previous_time

            # check if must sleep
            if elapsed_time < self.sleep_time:
                # sleep some time
                time.sleep(self.sleep_time - elapsed_time)

            previous_time = time.time()

        self.thread_exit = True
