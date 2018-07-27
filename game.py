import random
import time

from map import Map
from snake import Snake
from client import Client
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
        self.client_ids = range(1, Cts.MAX_PLAYERS - 1) # fifo of available client_ids

        random.seed()
        Thread.__init__(self)

    def init(self, bot_manager):
        self.bot_manager = bot_manager
        self.map.init()

    def sendMap(self, client):
        client.sendMessage(",".join([Cts.MESSAGE_MAP, self.map.getMapStr()]))

    def addClient(self, client, color):
        if color < Cts.SNAKE_COLOR:
            color = Cts.SNAKE_COLOR

        if (len(self.clients) > (Cts.MAX_PLAYERS - 1) or len(self.client_ids) == 0):
            # server is full
            client.close()
            return

        client.setId(self.client_ids.pop(0))
        self.createSnake(client, color)

    def removeClient(self, client):
        client.snake.kill()
        self.broadcastClientExited(client)

        if (client in self.clients):
            self.clients.remove(client)
            client.snake.clear(self.map)

        self.releaseClientId(client.id)

    def releaseClientId(self, client_id):
        self.client_ids.append(client_id)

    def getMap(self):
        return self.map

    def createSnake(self, client, color):
        offset = 3 + Cts.SNAKE_INITIAL_SIZE + Cts.WALLS_WIDTH

        while True:
            i = random.randint(offset, self.lines - offset)
            j = random.randint(offset, self.columns - offset)
            map_pixel = self.map.pixel(i, j)

            if map_pixel["mob"] == Cts.STATE_EMPTY and map_pixel["state"] == Cts.STATE_EMPTY:
                break;

        snake = Snake(color, client.id, Cts.SNAKE_INITIAL_SIZE, i, j, self.map)
        client.setSnake(snake)

        self.clients.append(client)
        self.sendAllPlayers(client)
        # notify speed
        client.sendMessage("".join([
            Cts.MESSAGE_PLAYER_SPEED,
            chr(int((snake.speed - 0.5) * (10 - 1) / (1.0 - 0.5) + 1))]),
            binary=True)

    def sendAllPlayers(self, client):
        """
        Send all players to new client
        """
        # Message [MSG_TYPE | PLAYER_ID | NICKNAME_SIZE | NICKNAME | COLOR | ... ]
        # message with all players to send to new client
        players_list = Cts.MESSAGE_PLAYERS

        # Message with all players to send to new client
        players_list = Cts.MESSAGE_PLAYERS

        # message to send to all clients
        message = "".join([Cts.MESSAGE_PLAYERS, client.nickname, chr(client.snake.color)])

        for c in self.clients:
             players_list = "".join([players_list, c.nickname, chr(c.snake.color)])
             if (c != client):
                # send new player to all clients
                c.sendMessage(message, binary=True)

        # send clients list
        client.sendMessage(players_list, binary=True)
        client.sendMessage(Cts.MESSAGE_MOBS + self.getSnakes() + self.map.getPowerUps(), binary=True)

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
        power_ups_generated_message = ""

        for pixel in client.snake.pixels:
            i, j = int(pixel['i']), int(pixel['j'])
            map_pixel = self.map.pixel(i, j)

            if not map_pixel["it"] or map_pixel["it"] > Cts.MAX_OBSTACLE_TILE:
                power_up = {}
                power_up["i"] = i
                power_up["j"] = j
                power_up["item"] = random.randint(Cts.MOB_CORPSE[0], Cts.MOB_CORPSE[1])
                power_up["type"] = power_up_type
                power_up["loop"] = Cts.LOOPS_REMOVE_CORPSE

                key = self.map.getKey(i, j)
                self.map.animated_power_ups[key] = power_up
                map_pixel["mob"] = power_up_type
                map_pixel["state"] = Cts.STATE_EMPTY
                map_pixel["client"] = Cts.STATE_EMPTY

                power_ups_generated_message += chr(power_up["i"]) + chr(power_up["j"]) + chr(power_up["item"])

        self.broadcastClientExited(client)
        self.bot_manager.addBots(len(self.clients))

        return power_ups_generated_message

    def getSnakes(self):
        # clients count
        snakes = chr(len(self.clients))

        for client in self.clients:
            # CLIENT_ID | SNAKE_COLOR | SNAKE_SIZE_MOST | SNAKE_SIZE_LESS | SNAKE_SPEED | PIXELS...
            snk = client.snake
            # FIXME: cache this message in snake
            snakes += chr(client.id) + chr(snk.color) + chr(snk.size >> 8) + chr(snk.size & 0xFF) + snk.getPixelsStr()

        return snakes

    def moveSnake(self, client, key):
        client.snake.move(key)

    def processMob(self, client, pixel, i, j):
        snake = client.snake
        key = self.map.getKey(i, j)
        power_up_generated_message = ""

        if pixel["mob"] == Cts.MOB_INCREASE:
            power_up = self.map.power_ups[key]

            snake.increaseSize()
            power_up_generated_message = self.map.generateRandomPowerUp(power_up["type"], power_up["item"])
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
            else:
                # notify speed boost
                client.sendMessage("".join([
                    Cts.MESSAGE_PLAYER_SPEED,
                    chr(int((snake.speed - 0.5) * (10 - 1) / (1.0 - 0.5) + 1))]),
                    binary=True)

            power_up_generated_message = self.map.generateRandomPowerUp(power_up["type"], power_up["item"])
            self.map.power_ups.pop(key)

        client.sendMessage("".join([Cts.MESSAGE_SOUND, chr(power_up["item"])]), binary=True)
        pixel["mob"] = Cts.STATE_EMPTY

        return power_up_generated_message

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
        sort_count = 0
        messageSnakesChange = ""
        messageMobsChange = ""
        aux = 0

        while self.running:
            # randomize power ups items
            if (count == 10):
                index = 0
                to_delete = []
                for k, power_up in self.map.animated_power_ups.items():
                    if (power_up["type"] == Cts.MOB_CORPSE[0]):
                        aux = power_up["item"]
                        power_up["item"] = random.randint(Cts.MOB_CORPSE[0], Cts.MOB_CORPSE[1])

                        # power up changed
                        if aux != power_up["item"]:
                            messageMobsChange += chr(power_up["i"]) + chr(power_up["j"]) + chr(power_up["item"])

                    if power_up["loop"]:
                        power_up["loop"] -= 1
                        if not power_up["loop"]:
                            # remove corpse
                            self.map.pixel(power_up["i"], power_up["j"])["mob"] = Cts.STATE_EMPTY

                            # update clients
                            messageMobsChange += chr(power_up["i"]) + chr(power_up["j"]) + Cts.STATE_EMPTY_CHAR

                            to_delete.append(k)
                for k in to_delete:
                    self.map.animated_power_ups.pop(k)
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
                    snake.moved = False

                    if client.bot:
                        # head off bot from obstacles
                        self.bot_manager.moveBot(client)
                    continue
                else:
                    snake.moved = True

                pixel = self.map.pixel(int_new_i, int_new_j)

                if pixel["state"] == Cts.STATE_BUSY and pixel["client"] != client.id:
                    messageMobsChange += self.kill(client)
                    continue

                if pixel["mob"] != Cts.STATE_EMPTY:
                    messageMobsChange += self.processMob(client, pixel, int_new_i, int_new_j)

                previous_i = new_i
                previous_j = new_j

                pixel["state"] = Cts.STATE_BUSY
                pixel["client"] = client.id

                previous_i, previous_j = snake.walk(previous_i, previous_j)

                if client.bot:
                    # head off bot from obstacles
                    self.bot_manager.moveBot(client)

                map_pixel = self.map.pixel(int(previous_i), int(previous_j))

                if not map_pixel["it"] or map_pixel["it"] > Cts.MAX_OBSTACLE_TILE:
                    map_pixel["state"] = Cts.STATE_EMPTY
                    map_pixel["mob"] = Cts.STATE_EMPTY
                    map_pixel["client"] = Cts.STATE_EMPTY
                    key = self.map.getKey(int(previous_i), int(previous_j))
                    if key in self.map.power_ups:
                        pu = self.map.power_ups[key]
                        messageMobsChange += self.map.generateRandomPowerUp(pu["type"], pu["item"])
                        self.map.power_ups.pop(key)
                snake.can_move = True
                # clients iteration end

            # FIXME: find a better way to do this
            if sort_count == 10:
                sort_count = 0

                # sort clients
                self.clients.sort(key=lambda client: client.snake.size, reverse=True)
            else:
                sort_count += 1

            messageMobs = Cts.MESSAGE_MOBS + self.getSnakes() + messageMobsChange
            messageSnakesChange = ""
            messageMobsChange = ""

            for client in self.clients:
                client.sendMessage(messageMobs, binary=True)
                if not client.snake.live:
                    # death
                    client.sendMessage(Cts.MESSAGE_DEATH)
                    client.close()
                    self.clients.remove(client)
                elif client.snake.moved:
                    client.snake.checkMovement()

            cur_time = time.time()
            elapsed_time = cur_time - previous_time

            # check if must sleep
            if elapsed_time < self.sleep_time:
                # sleep some time
                time.sleep(self.sleep_time - elapsed_time)

            previous_time = time.time()

        self.thread_exit = True
