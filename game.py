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
        self.leaderBoardChanged = True
        self.leaderBoardMessage = ""

    def init(self):
        self.map.init()        
    
    def sendMap(self, client):
        client.sendMessage(",".join([Cts.MESSAGE_MAP, self.map.getMapStr()]))

    def addClient(self, client, color):
        if color < Cts.SNAKE_COLOR:
            color = Cts.SNAKE_COLOR
    
        self.createSnake(client, color)

    def removeClient(self, client):
        if (client in self.clients):
            self.clients.remove(client)
            client.snake.clear(self.map)

            for c in self.clients:
                c.rankingChanged = True

    def getMapStr(self):
        to_return = str(self.lines) + "," + str(self.columns)

        for i in range(0, self.lines):
            for j in range(0, self.columns):
                to_return = to_return + "," + str(self.map.pixel(i, j)["it"])

        return to_return

    def createSnake(self, client, color):
        i = int(self.lines / 2)
        j = int(self.columns / 2) + len(self.clients)

        client_id = 0
        previous_id = 10
        
        for c in self.clients:
            if (c.id - previous_id > 1):
                break

            previous_id = c.id
            client_id += 1
        
        client.setId(client_id)
            
        for c in self.clients:
            c.rankingChanged = True

        snake = Snake(color, Cts.SNAKE_INITIAL_SIZE, i, j, self.map)
        client.setSnake(snake)
        
        print("snake created")
        
        self.clients.append(client)
        self.sendAllPlayers(client)
    
    def sendAllPlayers(self, client):
        """
        Send all players to a single client
        """
        players_list = ""
        for c in self.clients:
             players_list += c.nickname
        
        message = "".join([Cts.MESSAGE_PLAYERS, players_list])
        
        # send clients list
        client.sendMessage(message, binary=True)
        
        # send leaderboard
        client.sendMessage(self.leaderBoardMessage, binary=True)
        
        self.leaderBoardChanged = True
        
    
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

            self.map.animated_power_ups[key] = power_up
            self.map.pixel(i, j)["mob"] = power_up_type
            self.map.pixel(i, j)["state"] = Cts.STATE_EMPTY

    def getSnakes(self):
        snakes = ""
        for client in self.clients:
            snakes = snakes + client.snake.getPixelsStr()

        return snakes

    def moveSnake(self, client, key):
        client.snake.move(key)

    def processMob(self, snake, pixel, i, j):
        key = self.map.getKey(i, j)
        
        if pixel["mob"] == Cts.MOB_INCREASE:
            power_up = self.map.power_ups[key]
            
            snake.increaseSize()
            self.map.generateRandomPowerUp(power_up["type"], power_up["item"])
            self.map.power_ups.pop(key)
        elif pixel["mob"] == Cts.MOB_CORPSE[0]:
            power_up = self.map.animated_power_ups[key]
            
            snake.increaseSize()
            self.map.animated_power_ups.pop(key)
            # do not generate another
        elif pixel["mob"] == Cts.MOB_MOVE_SPEED:
            power_up = self.map.power_ups[key]
            
            snake.speed = snake.speed + Cts.SPEED_INCREMENT
            
            if snake.speed > 1:
                snake.speed = 1
        
            self.map.generateRandomPowerUp(power_up["type"], power_up["item"])
            self.map.power_ups.pop(key)
        
        pixel["mob"] = Cts.STATE_EMPTY

    def recalculateRanking(self, client):
        c_index = self.clients.index(client)
        
        if (c_index > 0):
            # get client above
            a_index = c_index - 1
            
            # check if current client snake passed the above snake
            if (client.snake.size > self.clients[a_index].snake.size):
                self.clients[c_index], self.clients[a_index] = self.clients[a_index], self.clients[c_index]
                
                self.clients[a_index].setRanking(a_index)
                self.clients[c_index].setRanking(c_index)
                
                # ranking changed
                return True
        
        # ranking not changed
        return False

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
        client.sendMessage("".join([Cts.MESSAGE_HEAD, chr(head["i"]), chr(head["j"])]), binary=True)

    def run(self):
        previous_time = 0
        cur_time = 0
        count = 0
        
        while self.running:
            # randomize power ups items
            if (count == 10):
                for k, power_up in self.map.animated_power_ups.items():
                    if (power_up["type"] == Cts.MOB_CORPSE[0]):
                        power_up["item"] = random.randrange(Cts.MOB_CORPSE[0], Cts.MOB_CORPSE[1])
                
                count = 0
            else:
                count = count + 1
            
            leaderBoardMessage = Cts.MESSAGE_LEADERBOARD
            for client in self.clients:
                snake = client.snake
                
                if not snake.live:
                    continue

                head = snake.getHead()

                new_i = head["i"] + snake.di
                new_j = head["j"] + snake.dj
                
                int_new_i = int(new_i)
                int_new_j = int(new_j)
                
                if int_new_i == int(head["i"]) and int_new_j == int(head["j"]):
                    # snake do not moved
                    
                    head["i"] = new_i
                    head["j"] = new_j
                    
                    continue
                    
                pixel = self.map.pixel(int_new_i, int_new_j)
                
                if (pixel["state"] == Cts.STATE_BUSY):
                    self.killSnake(snake)
                    continue

                if not (pixel["mob"] == 0):
                    self.processMob(snake, pixel, int_new_i, int_new_j)

                previous_i = new_i
                previous_j = new_j

                pixel["state"] = Cts.STATE_BUSY

                previous_i, previous_j = snake.walk(previous_i, previous_j)

                self.map.pixel(int(previous_i), int(previous_j))["state"] = Cts.STATE_EMPTY
                snake.can_move = True
                
                # if leaderboard changed in previous step, update clients
                if self.leaderBoardChanged:
                    leaderBoardMessage += chr(client.id)

                # clients iteration end
            
            if self.leaderBoardChanged:
                # update global leaderboard
                self.leaderBoardMessage = leaderBoardMessage
            
            messageMobs = self.getSnakes() + self.map.getPowerUps()
            
            # TODO
            rankingLength = chr(10)
            
            localLeaderBoardChanged = False
            for client in self.clients:
                snake = client.snake
                
                if snake.grew:
                    # if snake grew recalculate ranking for this client
                    localLeaderBoardChanged = self.recalculateRanking(client)

                # mobs
                head = snake.getHead()
                
                # TODO: test if send message with type byte (b"") is more efficient
                client.sendMessage("".join([Cts.MESSAGE_MOBS, chr(int(head["i"])),
                        chr(int(head["j"])), messageMobs]), binary=True)

                if snake.live:
                    # ranking
                    if client.rankingChanged:
                        client.rankingChanged = False
                        client.sendMessage("".join([Cts.MESSAGE_RANKING,
                                chr(client.ranking),
                                rankingLength]))

                    # leader board
                    if self.leaderBoardChanged:
                        client.sendMessage(self.leaderBoardMessage, binary=True)

                    # growth
                    if snake.grew:
                        snake.grew = False
                        client.sendMessage("".join([Cts.MESSAGE_SNAKE_SIZE, chr(snake.size)]), binary=True)
                else:
                    # death
                    client.sendMessage(Cts.MESSAGE_DEATH)
            
            # update leaderboard flag to update clients in the next step
            self.leaderBoardChanged = localLeaderBoardChanged

            cur_time = time.time()
            elapsed_time = cur_time - previous_time

            # check if must sleep
            if elapsed_time < self.sleep_time:
                # sleep some time
                time.sleep(self.sleep_time - elapsed_time)

            previous_time = time.time()

        self.thread_exit = True
