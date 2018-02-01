import random
import time

from snake import Snake
from threading import Thread

SNAKE_INITIAL_SIZE = 5

STATE_EMPTY = 0
STATE_BUSY = 1
# SNAKE_COLOR = 2 TODO: change snakes colors
MOB_INCREASE = 3
MOB_CORPSE = 4
MOB_MOVE_SPEED = 5

SPEED_INCREMENT = 0.1

# Messages types
MESSAGE_MAP = chr(0)
MESSAGE_HEAD = chr(1)
MESSAGE_MOBS = chr(2)
MESSAGE_SNAKE_SIZE = chr(3)
MESSAGE_DEATH = chr(4)
MESSAGE_RANKING = chr(5)
MESSAGE_LEADERBOARD = chr(6)

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
        self.ranking = []
        self.leaderBoard = ""

    def init(self):
        self.clients = []

        lines_1 = self.lines - 1
        columns_1 = self.columns - 1

        for i in range(0, self.lines):
            line = []
            for j in range(0, self.columns):
                it = STATE_BUSY if (i == 0) or (i == lines_1) or (j == 0) or (j == columns_1) else STATE_EMPTY
                line.append({
                        "it": it,
                        "state": it,
                        "mob": STATE_EMPTY
                    })
            self.matrix.append(line)

        minor = int((self.lines if self.lines < self.columns else self.columns) * 0.5)

        for c in range(0, minor):
            self.generateRandomPowerUp(MOB_INCREASE)

        for c in range(0, int(minor * 0.2)):
            self.generateRandomPowerUp(MOB_MOVE_SPEED)

    def sendMap(self, client):
        client.sendMessage(",".join([MESSAGE_MAP, self.getMapStr()]))

    def getKey(self, i, j):
        return i * self.columns + j

    def generateRandomPowerUp(self, power_up_type):
        power_up = {}

        while True:
            i = random.randrange(1, self.lines - 1)
            j = random.randrange(1, self.columns - 1)

            if self.matrix[i][j]["mob"] == STATE_EMPTY and self.matrix[i][j]["state"] == STATE_EMPTY:
                break;

        power_up["i"] = i
        power_up["j"] = j
        power_up["type"] = power_up_type

        key = self.getKey(i, j)

        self.power_ups[key] = power_up
        self.matrix[i][j]["mob"] = power_up_type

    def addClient(self, client):
        self.clients.append(client)
        return self.createSnake(client.address, client.nickname)

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

    def createSnake(self, address, nickname):
        i = int(self.lines / 2)
        j = int(self.columns / 2) + len(self.snakes)

        for k, snake in self.snakes.items():
            snake.rankingChanged = True

        snake = Snake(SNAKE_INITIAL_SIZE, i, j, self.matrix, nickname)
        self.snakes[address] = snake
        self.ranking.append(address)

        return snake

    def killSnake(self, snake):
        pixels = snake.pixels
        snake.kill()

        power_up_type = MOB_CORPSE

        for pixel in snake.pixels:
            i, j = int(pixel['i']), int(pixel['j'])

            power_up = {}
            power_up["i"] = i
            power_up["j"] = j
            power_up["type"] = power_up_type

            key = self.getKey(i, j)

            self.power_ups[key] = power_up
            self.matrix[i][j]["mob"] = power_up_type

    def removeSnake(self, address):
        snake = self.snakes[address]
        snake.clear(self.matrix)
        self.snakes.pop(address)
        self.ranking.remove(address)

        for k, snake in self.snakes.items():
            snake.rankingChanged = True

    def getSnakes(self):
        snakes = ""
        for k, snake in self.snakes.items():
            snakes = snakes + snake.getPixelsStr()

        return snakes

    def getPowerUps(self):
        power_ups = ""
        for k, power_up in self.power_ups.items():
            power_ups = power_ups + chr(power_up["i"]) + chr(power_up["j"]) + chr(power_up["type"])

        return power_ups

    def moveSnake(self, address, key):
        self.snakes[address].move(key)

    def processMob(self, snake, pixel, i, j):
        pixel["mob"] = STATE_EMPTY

        key = self.getKey(i, j)
        power_up = self.power_ups[key]
        ptype = power_up["type"]

        if ptype == MOB_INCREASE:
            snake.increaseSize()
            self.generateRandomPowerUp(ptype)
        elif ptype == MOB_CORPSE:
            snake.increaseSize()
            # do not generate another
        elif ptype == MOB_MOVE_SPEED:
            snake.speed = snake.speed + SPEED_INCREMENT
            
            if snake.speed > 1:
                snake.speed = 1
        
            self.generateRandomPowerUp(ptype)
            
        self.power_ups.pop(key)            

    def recalculateRanking(self):
        for i in range(1, len(self.ranking)):
            if self.snakes[self.ranking[i]].size > self.snakes[self.ranking[i - 1]].size:
                # swap
                self.ranking[i], self.ranking[i - 1] = self.ranking[i - 1], self.ranking[i]
                # update ranking
                self.snakes[self.ranking[i]].setRanking(i + 1)
                self.snakes[self.ranking[i - 1]].setRanking(i)

    def close(self):
        self.running = False

        while not self.thread_exit:
            pass

        for client in self.clients:
            client.close()

        del self.matrix[:]
        self.snakes.clear()
        self.power_ups.clear()

    def sendHead(self, client, snake):
        head = snake.getHead()
        client.sendMessage("".join([MESSAGE_HEAD, chr(head["i"]), chr(head["j"])]))

    def run(self):
        previous_time = 0
        cur_time = 0

        while self.running:
            recalculateRanking = False
            for k, snake in self.snakes.items():
                if not snake.live:
                    continue

                head = snake.pixels[0]

                new_i = head["i"] + snake.di
                new_j = head["j"] + snake.dj
                
                int_new_i = int(new_i)
                int_new_j = int(new_j)
                
                if int_new_i == int(head["i"]) and int_new_j == int(head["j"]):
                    # snake do not moved
                    
                    head["i"] = new_i
                    head["j"] = new_j
                    
                    continue
                    
                pixel = self.matrix[int_new_i][int_new_j]
                
                if (pixel["state"] == STATE_BUSY):
                    self.killSnake(snake)
                    continue

                if not (pixel["mob"] == 0):
                    self.processMob(snake, pixel, int_new_i, int_new_j)

                previous_i = new_i
                previous_j = new_j

                pixel["state"] = STATE_BUSY

                previous_i, previous_j = snake.walk(previous_i, previous_j)

                self.matrix[int(previous_i)][int(previous_j)]["state"] = STATE_EMPTY
                snake.can_move = True

                if snake.grew:
                    recalculateRanking = True

                # snakes iteration end

            if recalculateRanking:
                self.recalculateRanking()

            messageMobs = self.getSnakes() + self.getPowerUps()

            leaderBoard = ""
            for address in self.ranking[:10]:
                leaderBoard = leaderBoard + str(self.snakes[address].nickname) + ','
            leaderBoard = leaderBoard[:(len(leaderBoard) - 1)]

            leaderBoardChanged = False

            if self.leaderBoard != leaderBoard:
                self.leaderBoard = leaderBoard
                leaderBoardChanged = True
                leaderBoardMessage = "".join([MESSAGE_LEADERBOARD, self.leaderBoard])

            rankingLength = chr(len(self.ranking))

            for client in self.clients:
                snake = self.snakes[client.address]

                # mobs
                head = snake.getHead()
                client.sendMessage("".join([MESSAGE_MOBS, chr(int(head["i"])),
                        chr(int(head["j"])), messageMobs]))

                if snake.live:
                    # ranking
                    if snake.rankingChanged:
                        snake.rankingChanged = False
                        client.sendMessage("".join([MESSAGE_RANKING,
                                chr(snake.ranking),
                                rankingLength]))

                    # leader board
                    if leaderBoardChanged or not snake.receivedLeaderBoard:
                        snake.receivedLeaderBoard = True
                        client.sendMessage(leaderBoardMessage)

                    # growth
                    if snake.grew:
                        snake.grew = False
                        client.sendMessage("".join([MESSAGE_SNAKE_SIZE, chr(snake.size)]))
                else:
                    # death
                    client.sendMessage(MESSAGE_DEATH)

            cur_time = time.time()
            elapsed_time = cur_time - previous_time

            # check if must sleep
            if elapsed_time < self.sleep_time:
                # sleep some time
                time.sleep(self.sleep_time - elapsed_time)

            previous_time = time.time()

        self.thread_exit = True
