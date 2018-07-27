import random

from constants import Constants as Cts

class Map():

    def __init__(self, lines, columns):
        self.matrix = []
        self.power_ups = {}
        self.animated_power_ups = {}
        self.lines = lines
        self.columns = columns

    def init(self):
        # fill empty matrix
        for i in range(0, self.lines):
            line = []
            for j in range(0, self.columns):
                line.append({"it": Cts.STATE_EMPTY, "state": Cts.STATE_EMPTY, "mob": Cts.STATE_EMPTY, "client": 0})
            self.matrix.append(line)

        for i in range(0, 20):
            self.drawIsland()

        self.drawWalls()

        minor = int((self.lines if self.lines < self.columns else self.columns) * 0.2)

        for c in range(0, minor):
            for item in range(Cts.MOB_FOOD_ITEMS[0], Cts.MOB_FOOD_ITEMS[1]):
                self.generateRandomPowerUp(Cts.MOB_INCREASE, item)

        minor = int((self.lines if self.lines < self.columns else self.columns) * 0.5)
        for c in range(0, int(minor * 0.2)):
            self.generateRandomPowerUp(Cts.MOB_MOVE_SPEED, Cts.MOB_MOVE_SPEED)

    def generateRandomPowerUp(self, power_up_type, item):
        power_up = {}

        while True:
            i = random.randrange(1, self.lines - 1)
            j = random.randrange(1, self.columns - 1)

            if self.matrix[i][j]["mob"] == Cts.STATE_EMPTY and self.matrix[i][j]["state"] == Cts.STATE_EMPTY:
                break;

        power_up["i"] = i
        power_up["j"] = j
        power_up["item"] = item
        power_up["type"] = power_up_type

        key = self.getKey(i, j)

        self.power_ups[key] = power_up
        self.matrix[i][j]["mob"] = power_up_type

        return chr(power_up["i"]) + chr(power_up["j"]) + chr(power_up["item"])
            
    def drawIsland(self):
        start_i = random.randrange(5, (self.lines / 2) - 5)
        start_j = random.randrange(5, (self.columns / 2) - 5)

        q = random.randrange(0, 4)

        if (q == 1):
            start_j = start_j + (self.columns / 2)
        elif (q == 2):
            start_i = start_i + (self.lines / 2)
            start_j = start_j + (self.columns / 2)
        elif (q == 3):
            start_i = start_i + (self.lines / 2)

        size = random.randrange(5, 15)

        end_i = start_i + size
        end_j = start_j + size

        for i in range(start_i, end_i):
            for j in range(start_j, end_j):
                if (len(self.matrix) <= i or len(self.matrix[i]) <= j):
                    continue;
                current = self.matrix[i][j]

                if i == start_i or i == end_i - 1 or j == start_j or j == end_j - 1:
                    it = random.randrange(Cts.GRASS[0], Cts.GRASS[1])
                else:
                    it = random.randrange(Cts.CLAY[0], Cts.CLAY[1])

                current["it"] = it
                current["state"] = Cts.STATE_BUSY

    def drawWalls(self):
        walls_width = Cts.WALLS_WIDTH
        lines_l = self.lines - walls_width
        columns_l = self.columns - walls_width
        for i in range(0, self.lines):
            line = []
            for j in range(0, self.columns):
                state = Cts.STATE_BUSY

                if i <= walls_width or j <= walls_width or i >= lines_l or j >= columns_l:
                    it = random.randrange(Cts.STONES[0], Cts.STONES[1])
                else:
                    state = Cts.STATE_EMPTY
                    it = Cts.STATE_EMPTY

                current = self.matrix[i][j]
                current["it"] = it if it != Cts.STATE_EMPTY else current["it"]
                current["state"] = state if state != Cts.STATE_EMPTY else current["state"]

    def getMapStr(self):
        to_return = str(self.lines) + "," + str(self.columns)

        for i in range(0, self.lines):
            for j in range(0, self.columns):
                to_return = to_return + "," + str(self.matrix[i][j]["it"])

        return to_return

    def getPowerUps(self):
        power_ups = ""

        for k, power_up in self.power_ups.items():
            power_ups = power_ups + chr(power_up["i"]) + chr(power_up["j"]) + chr(power_up["item"])

        for k, power_up in self.animated_power_ups.items():
            power_ups = power_ups + chr(power_up["i"]) + chr(power_up["j"]) + chr(power_up["item"])

        return power_ups

    def getKey(self, i, j):
        return i * self.columns + j

    def pixel(self, i, j):
        if (i >= self.lines or j >= self.columns or i < 0 or j < 0):
            pix = {}
            pix["state"] = Cts.STATE_BUSY
            pix["mob"] = Cts.STATE_EMPTY
            pix["client"] = Cts.STATE_EMPTY
            pix["it"] = Cts.STATE_EMPTY
            return pix

        return self.matrix[i][j]
