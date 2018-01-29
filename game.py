import random
import time

from snake import Snake
from threading import Thread

SNAKE_INITIAL_SIZE = 5

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
                        "mob": 0
                    })
            self.matrix.append(line)

        minor = int((self.lines if self.lines < self.columns else self.columns) * 0.8)
        t = ""
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
        self.createSnake(client.address, client.nickname)

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

        self.snakes[address] = Snake(SNAKE_INITIAL_SIZE, i, j, self.matrix, nickname)
        self.ranking.append(address)

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

        if power_up["type"] == MOB_INCREASE:
            snake.increaseSize()

        self.power_ups.pop(key)
        self.generateRandomPowerUp(power_up["type"])

    def recalculateRanking(self):
        self.ranking = self.merge_sort(self.ranking)

        ranking = 1
        for address in self.ranking:
            self.snakes[address].setRanking(ranking)
            ranking += 1

    def merge(self, left, right):
        result = []
        left_idx, right_idx = 0, 0
        while left_idx < len(left) and right_idx < len(right):
            if self.snakes[left[left_idx]].size > self.snakes[right[right_idx]].size:
                result.append(left[left_idx])
                left_idx += 1
            else:
                result.append(right[right_idx])
                right_idx += 1

        if left:
            result.extend(left[left_idx:])
        if right:
            result.extend(right[right_idx:])

        return result

    def merge_sort(self, array):
        if len(array) <= 1:
            return array

        middle = len(array) // 2
        left = array[:middle]
        right = array[middle:]

        left = self.merge_sort(left)
        right = self.merge_sort(right)

        return list(self.merge(left, right))

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
            recalculateRanking = False
            for k, snake in self.snakes.items():
                if not snake.live:
                    continue

                head = snake.pixels[0]

                new_i = head["i"] + snake.di
                new_j = head["j"] + snake.dj

                pixel = self.matrix[new_i][new_j]

                if (pixel["state"] == STATE_BUSY):
                    snake.kill()

                    continue

                if not (pixel["mob"] == 0):
                    self.processMob(snake, pixel, new_i, new_j)

                previous_i = new_i
                previous_j = new_j

                pixel["state"] = STATE_BUSY

                previous_i, previous_j = snake.walk(previous_i, previous_j)

                self.matrix[previous_i][previous_j]["state"] = STATE_EMPTY
                snake.can_move = True

                if snake.grew:
                    recalculateRanking = True

                # snakes iteration end

            if recalculateRanking:
                self.recalculateRanking()

            message0 = chr(2)
            message2 = self.getSnakes() + self.getPowerUps()

            rankingLength = str(len(self.ranking))

            leaderBoard = ""
            for address in self.ranking[:10]:
                leaderBoard = leaderBoard + str(self.snakes[address].nickname) + ','
            leaderBoard = leaderBoard[:(len(leaderBoard) - 1)]

            leaderBoardChanged = False

            if self.leaderBoard != leaderBoard:
                self.leaderBoard = leaderBoard
                leaderBoardChanged = True

            for client in self.clients:
                snake = self.snakes[client.address]

                # mobs
                head = snake.pixels[0]
                client.sendMessage("".join([message0, chr(head["i"]),
                        chr(head["j"]), message2]))

                # ranking
                if snake.rankingChanged:
                    snake.rankingChanged = False
                    client.sendMessage("".join([chr(5),
                            str(snake.ranking),
                            str('/'),
                            rankingLength]))

                # leader board
                if leaderBoardChanged or not snake.receivedLeaderBoard:
                    snake.receivedLeaderBoard = True
                    client.sendMessage("".join([chr(6), leaderBoard]))

                # growth
                if snake.grew:
                    snake.grew = False
                    client.sendMessage("".join([chr(3), str(snake.size)]))

                # death
                if not snake.live:
                    client.sendMessage("".join([chr(4)]))

            cur_time = time.time()
            elapsed_time = cur_time - previous_time

            # check if must sleep
            if elapsed_time < self.sleep_time:
                # sleep some time
                time.sleep(self.sleep_time - elapsed_time)

            previous_time = time.time()

        self.thread_exit = True
