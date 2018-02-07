import random

from constants import Constants as Cts

class Map():

    def __init__(self, lines, columns):
        self.matrix = []
        self.power_ups = {}
        self.lines = lines
        self.columns = columns
        
    def init(self):
        # fill empty matrix
        for i in range(0, self.lines):
            line = []
            for j in range(0, self.columns):
                line.append({"it": Cts.STATE_EMPTY, "state": Cts.STATE_EMPTY, "mob": Cts.STATE_EMPTY})
            self.matrix.append(line)
        
        for i in range(0, 10):
            self.drawIsland()
            
        self.drawWalls()

        minor = int((self.lines if self.lines < self.columns else self.columns) * 0.5)
        
        for c in range(0, minor):
            self.generateRandomPowerUp(Cts.MOB_INCREASE)

        for c in range(0, int(minor * 0.2)):
            self.generateRandomPowerUp(Cts.MOB_MOVE_SPEED)
            
    def generateRandomPowerUp(self, power_up_type):
        power_up = {}

        while True:
            i = random.randrange(1, self.lines - 1)
            j = random.randrange(1, self.columns - 1)

            if self.matrix[i][j]["mob"] == Cts.STATE_EMPTY and self.matrix[i][j]["state"] == Cts.STATE_EMPTY:
                break;

        power_up["i"] = i
        power_up["j"] = j
        power_up["type"] = power_up_type

        key = self.getKey(i, j)

        self.power_ups[key] = power_up
        self.matrix[i][j]["mob"] = power_up_type
            
    def drawIsland(self):
        start_i = random.randrange(20, self.lines - 20)
        start_j = random.randrange(20, self.columns - 20)
        size = random.randrange(5, 8)
        
        end_i = start_i + size
        end_j = start_j + size
        
        for i in range(start_i, end_i):
            for j in range(start_j, end_j):
                current = self.matrix[i][j]
                
                if i == start_i or i == end_i - 1 or j == start_j or j == end_j - 1:
                    it = random.randrange(Cts.GRASS[0], Cts.GRASS[1])
                else:
                    it = random.randrange(Cts.CLAY[0], Cts.CLAY[1])
                    
                current["it"] = it
                current["state"] = Cts.STATE_BUSY
            
    
    def drawWalls(self):
        walls_width = 5
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
            power_ups = power_ups + chr(power_up["i"]) + chr(power_up["j"]) + chr(power_up["type"])

        return power_ups
    
    def getKey(self, i, j):
        return i * self.columns + j
    
    def __getitem__(self, index):
        return self.matrix[index]

