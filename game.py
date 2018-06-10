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
        self.client_id = 0

        Thread.__init__(self)

    def init(self):
        self.map.init()

    def sendMap(self, client):
        client.sendMessage(",".join([Cts.MESSAGE_MAP, self.map.getMapStr()]))

    def addClient(self, client, color):
        if color < Cts.SNAKE_COLOR:
            color = Cts.SNAKE_COLOR

        self.client_id += 1
        if (self.client_id > 255):
            self.client_id = 0

        for c in self.clients:
            if (c.id == self.client_id):
                self.client_id += 1
            else:
                # Found an available ID
                break

        if (self.client_id > 255):
            # gonged: server is full
            client.close()
            return

        client.setId(self.client_id)

        self.createSnake(client, color)

    def removeClient(self, client):
        client.snake.kill()
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

        snake = Snake(color, Cts.SNAKE_INITIAL_SIZE, i, j, self.map)
        client.setSnake(snake)

        self.clients.append(client)
        self.sendAllPlayers(client)

    def sendAllPlayers(self, client):
        """
        Send all players to new client
        """

        # message with all players to send to new client
        players_list = ""

        # message to send to all clients
        message = "".join([Cts.MESSAGE_PLAYERS, client.nickname, chr(client.snake.color)])

        for c in self.clients:
             players_list += c.nickname + chr(client.snake.color)

             if (c != client):
                # send new player to all clients
                c.sendMessage(message, binary=True)

        message = "".join([Cts.MESSAGE_PLAYERS, players_list])

        # send clients list
        client.sendMessage(message, binary=True)

    def broadcastClientExited(self, client):
        """
        Inform clients that client exited
        """

        message = "".join([Cts.MESSAGE_PLAYER_EXITED, chr(client.id)])
        for c in self.clients:
            # send message to all clients
            c.sendMessage(message, binary=True)

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

    def getSnakes(self):
        # clients count
        snakes = chr(len(self.clients))

        for client in self.clients:
            # CLIENT_ID | SNAKE_COLOR | SNAKE_SIZE | PIXELS...
            snk = client.snake
            snakes += chr(client.id) + chr(snk.color) + chr(snk.size) + snk.getPixelsStr()

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
                chr(client.id), chr(client.snake.color), chr(head["i"]), chr(head["j"])
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
                # clients iteration end

            messageMobs = Cts.MESSAGE_MOBS + self.getSnakes() + self.map.getPowerUps()

            for client in self.clients:
                client.sendMessage(messageMobs, binary=True)
                if not client.snake.live:
                    # death
                    client.sendMessage(Cts.MESSAGE_DEATH)
                    client.close()
                    self.clients.remove(client)

            cur_time = time.time()
            elapsed_time = cur_time - previous_time

            # check if must sleep
            if elapsed_time < self.sleep_time:
                # sleep some time
                time.sleep(self.sleep_time - elapsed_time)

            previous_time = time.time()

        self.thread_exit = True
