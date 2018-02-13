import random
import time

from map import Map
from snake import Snake
from threading import Thread
from constants import Constants as Cts

class Game(Thread):

    def __init__(self, lines, columns, sleep_time):
        Thread.__init__(self)

        self.thread_exit = False
        self.lines = lines
        self.columns = columns
        self.sleep_time = sleep_time
        self.running = True
        self.map = Map(lines, columns)
        self.clients = []
        self.ranking = []
        self.leaderBoard = ""

    def init(self):
        self.map.init()        
    
    def sendMap(self, client):
        client.sendMessage(",".join([Cts.MESSAGE_MAP, self.map.getMapStr()]))

    def addClient(self, client):
        self.createSnake(client)
        self.clients.append(client)

    def removeClient(self, client):
        if (client in self.clients):
            self.clients.remove(client)
            client.snake.clear(self.map)
            self.ranking.remove(client)

            for c in self.clients:
                c.rankingChanged = True

    def getMapStr(self):
        to_return = str(self.lines) + "," + str(self.columns)

        for i in range(0, self.lines):
            for j in range(0, self.columns):
                to_return = to_return + "," + str(self.map[i][j]["it"])

        return to_return

    def createSnake(self, client):
        i = int(self.lines / 2)
        j = int(self.columns / 2) + len(self.clients)

        for c in self.clients:
            c.rankingChanged = True

        snake = Snake(Cts.SNAKE_COLOR, Cts.SNAKE_INITIAL_SIZE, i, j, self.map)
        self.ranking.append(client)
        client.setSnake(snake)

    def killSnake(self, snake):
        pixels = snake.pixels
        snake.kill()

        power_up_type = Cts.MOB_CORPSE[0]

        for pixel in snake.pixels:
            i, j = int(pixel['i']), int(pixel['j'])

            power_up = {}
            power_up["i"] = i
            power_up["j"] = j
            power_up["item"] = random.randrange(Cts.MOB_CORPSE[0], Cts.MOB_CORPSE[1])
            power_up["type"] = power_up_type

            key = self.map.getKey(i, j)

            self.map.power_ups[key] = power_up
            self.map[i][j]["mob"] = power_up_type
            self.map[i][j]["state"] = Cts.STATE_EMPTY

    def getSnakes(self):
        snakes = ""
        for client in self.clients:
            snakes = snakes + client.snake.getPixelsStr()

        return snakes

    def moveSnake(self, client, key):
        client.snake.move(key)

    def processMob(self, snake, pixel, i, j):
        pixel["mob"] = Cts.STATE_EMPTY

        key = self.map.getKey(i, j)
        power_up = self.map.power_ups[key]
        ptype = power_up["type"]

        if ptype == Cts.MOB_INCREASE:
            snake.increaseSize()
            self.map.generateRandomPowerUp(ptype, power_up["item"])
        elif ptype == Cts.MOB_CORPSE[0]:
            snake.increaseSize()
            # do not generate another
        elif ptype == Cts.MOB_MOVE_SPEED:
            snake.speed = snake.speed + Cts.SPEED_INCREMENT
            
            if snake.speed > 1:
                snake.speed = 1
        
            self.map.generateRandomPowerUp(ptype, power_up["item"])
            
        self.map.power_ups.pop(key)            

    def recalculateRanking(self):
        for i in range(1, len(self.ranking)):
            if self.ranking[i].snake.size > self.ranking[i - 1].snake.size:
                # swap
                self.ranking[i], self.ranking[i - 1] = self.ranking[i - 1], self.ranking[i]
                # update ranking
                self.ranking[i].snake.setRanking(i + 1)
                self.ranking[i - 1].snake.setRanking(i)

    def close(self):
        self.running = False

        while not self.thread_exit:
            pass

        for client in self.clients:
            client.close()

        del self.map[:]
        self.clients.clear()
        self.map.power_ups.clear()

    def sendHead(self, client):
        head = client.snake.getHead()
        client.sendMessage("".join([Cts.MESSAGE_HEAD, chr(head["i"]), chr(head["j"])]))

    def run(self):
        previous_time = 0
        cur_time = 0

        while self.running:
            recalculateRanking = False
            for client in self.clients:
                snake = client.snake
                
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
                    
                pixel = self.map[int_new_i][int_new_j]
                
                if (pixel["state"] == Cts.STATE_BUSY):
                    self.killSnake(snake)
                    continue

                if not (pixel["mob"] == 0):
                    self.processMob(snake, pixel, int_new_i, int_new_j)

                previous_i = new_i
                previous_j = new_j

                pixel["state"] = Cts.STATE_BUSY

                previous_i, previous_j = snake.walk(previous_i, previous_j)

                self.map[int(previous_i)][int(previous_j)]["state"] = Cts.STATE_EMPTY
                snake.can_move = True

                if snake.grew:
                    recalculateRanking = True

                # snakes iteration end

            if recalculateRanking:
                self.recalculateRanking()

            messageMobs = self.getSnakes() + self.map.getPowerUps()

            leaderBoard = ""
            for client in self.ranking[:10]:
                leaderBoard = leaderBoard + str(client.nickname) + ','
            leaderBoard = leaderBoard[:(len(leaderBoard) - 1)]

            leaderBoardChanged = False

            if self.leaderBoard != leaderBoard:
                self.leaderBoard = leaderBoard
                leaderBoardChanged = True
                leaderBoardMessage = "".join([Cts.MESSAGE_LEADERBOARD, self.leaderBoard])

            rankingLength = chr(len(self.ranking))

            for client in self.clients:
                snake = client.snake

                # mobs
                head = snake.getHead()
                client.sendMessage("".join([Cts.MESSAGE_MOBS, chr(int(head["i"])),
                        chr(int(head["j"])), messageMobs]))

                if snake.live:
                    # ranking
                    if client.rankingChanged:
                        client.rankingChanged = False
                        client.sendMessage("".join([Cts.MESSAGE_RANKING,
                                chr(client.ranking),
                                rankingLength]))

                    # leader board
                    if leaderBoardChanged or not snake.receivedLeaderBoard:
                        snake.receivedLeaderBoard = True
                        client.sendMessage(leaderBoardMessage)

                    # growth
                    if snake.grew:
                        snake.grew = False
                        client.sendMessage("".join([Cts.MESSAGE_SNAKE_SIZE, chr(snake.size)]))
                else:
                    # death
                    client.sendMessage(Cts.MESSAGE_DEATH)

            cur_time = time.time()
            elapsed_time = cur_time - previous_time

            # check if must sleep
            if elapsed_time < self.sleep_time:
                # sleep some time
                time.sleep(self.sleep_time - elapsed_time)

            previous_time = time.time()

        self.thread_exit = True
