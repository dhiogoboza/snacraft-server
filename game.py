import random
import time

from map import Map
from snake import Snake
from threading import Thread
from constants import Constants as Cts

class Game(Thread):

    def __init__(self, lines, columns, sleep_time):
        self.thread_exit = False
        self.lines = lines
        self.columns = columns
        self.sleep_time = sleep_time
        self.running = True
        self.map = Map(lines, columns)
        self.clients = []
        #self.leaderBoardChanged = True
        #self.leaderBoardMessage = ""
        
        Thread.__init__(self)

    def init(self):
        self.map.init()        
    
    def sendMap(self, client):
        client.sendMessage(",".join([Cts.MESSAGE_MAP, self.map.getMapStr()]))

    def addClient(self, client, color):
        if color < Cts.SNAKE_COLOR:
            color = Cts.SNAKE_COLOR
    
        self.createSnake(client, color)

    def removeClient(self, client):
        self.broadcastClientExited(client)
        
        if (client in self.clients):
            self.clients.remove(client)
            client.snake.clear(self.map)

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
            
        #for c in self.clients:
        #    c.rankingChanged = True

        snake = Snake(color, Cts.SNAKE_INITIAL_SIZE, i, j, self.map)
        client.setSnake(snake)
        
        self.clients.append(client)
        self.sendAllPlayers(client)
    
    def sendAllPlayers(self, client):
        """
        Send all players to a single client
        """
        #self.leaderBoardChanged = True
        
        # message with all players to send to new client
        players_list = ""
        
        # message to send to all clients
        message = "".join([Cts.MESSAGE_PLAYERS, client.nickname])
        
        for c in self.clients:
             players_list += c.nickname
             if (c != client):
                # send new player to all clients
                c.sendMessage(message, binary=True)
        
        message = "".join([Cts.MESSAGE_PLAYERS, players_list])
        
        # send clients list
        client.sendMessage(message, binary=True)
        
        for c in self.clients:
            c.leaderBoardUpdated = False
        
    
    def kill(self, client):
        client.snake.kill()

        power_up_type = Cts.MOB_CORPSE[0]

        for pixel in client.snake.pixels:
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
         
        self.broadcastClientExited(client)
        
    def broadcastClientExited(self, client):
        # update clients
        #self.leaderBoardChanged = True
        
        # inform clients that client exited
        message = "".join([Cts.MESSAGE_PLAYER_EXITED, chr(client.id)])
        for c in self.clients:
            # send message to all clients
            c.sendMessage(message, binary=True)
            #c.leaderBoardUpdated = False
            #c.rankingChanged = True

    def getSnakes(self):
        # clients count
        snakes = chr(len(self.clients))
        
        for client in self.clients:
            # CLIENT_ID | SNAKE_SIZE | PIXELS...
            snakes += chr(client.id) + chr(client.snake.size) + client.snake.getPixelsStr()

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
                
                #self.clients[a_index].setRanking(a_index)
                #self.clients[c_index].setRanking(c_index)
                
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

    def sendClientData(self, client):
        head = client.snake.getHead()
        client.sendMessage("".join([Cts.MESSAGE_CLIENT_DATA,
                chr(head["i"]), chr(head["j"]), chr(client.id)
                ]), binary=True)

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
            
            #leaderBoardMessage = Cts.MESSAGE_LEADERBOARD
            #debugLeaderBoardMessage = "6,"
            
            #leaderBoardCount = 0
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
                    self.kill(client)
                    continue

                if not (pixel["mob"] == 0):
                    self.processMob(snake, pixel, int_new_i, int_new_j)

                previous_i = new_i
                previous_j = new_j

                pixel["state"] = Cts.STATE_BUSY

                previous_i, previous_j = snake.walk(previous_i, previous_j)

                self.map.pixel(int(previous_i), int(previous_j))["state"] = Cts.STATE_EMPTY
                snake.can_move = True
                
                # update leaderboard
                """
                if leaderBoardCount < 10:
                    leaderBoardMessage += chr(client.id)
                    debugLeaderBoardMessage += str(client.id) + ","
                else:
                    leaderBoardCount += 1
                """
                # clients iteration end
            
            # if leaderboard changed in previous step, update clients
            """
            if self.leaderBoardChanged:
                # update global leaderboard
                self.leaderBoardMessage = leaderBoardMessage
                print("debugLeaderBoardMessage: " + debugLeaderBoardMessage)
            """
            
            #messageMobs = self.getSnakes() + self.map.getPowerUps()
            
            messageMobs = Cts.MESSAGE_MOBS + self.getSnakes() + self.map.getPowerUps()
            
            # TODO
            #rankingLength = chr(10)
            
            #localLeaderBoardChanged = False
            for client in self.clients:
                snake = client.snake

                #if snake.grew:
                    # if snake grew recalculate ranking for this client
                    #localLeaderBoardChanged = self.recalculateRanking(client)

                # mobs
                head = snake.getHead()
                
                # TODO: test if send message with type byte (b"") is more efficient
                client.sendMessage("".join([Cts.MESSAGE_MOBS, chr(int(head["i"])),
                        chr(int(head["j"])), messageMobs]), binary=True)

                #if snake.live:
                # ranking
                """
                if client.rankingChanged:
                    client.rankingChanged = False
                    client.sendMessage("".join([Cts.MESSAGE_RANKING,
                            chr(client.ranking),
                            rankingLength]))
                """
                
                # leader board
                #if self.leaderBoardChanged or not client.leaderBoardUpdated:
                #    client.sendMessage(self.leaderBoardMessage, binary=True)
                #    client.leaderBoardUpdated = True

                # growth
                #if snake.grew:
                #    snake.grew = False
                #    client.sendMessage("".join([Cts.MESSAGE_SNAKE_SIZE, chr(snake.size)]), binary=True)
                if not snake.live:
                    # death
                    client.sendMessage(Cts.MESSAGE_DEATH)
            
            # update leaderboard flag to update clients in the next step
            #self.leaderBoardChanged = localLeaderBoardChanged

            cur_time = time.time()
            elapsed_time = cur_time - previous_time

            # check if must sleep
            if elapsed_time < self.sleep_time:
                # sleep some time
                time.sleep(self.sleep_time - elapsed_time)

            previous_time = time.time()

        self.thread_exit = True
