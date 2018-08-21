import random
import time

from client import Client
from constants import Constants as Cts

from threading import Thread

class BotManager(Thread):
    """
    Bots manager
    """
    def __init__(self, game, max_bots, sleep_time):
        self.game = game
        self.max_bots = max_bots
        self.bots = []
        self.monsters_bots = 0
        self.players_bots = 0
        self.running = True
        self.sleep_time = sleep_time

        random.seed()
        Thread.__init__(self)

    def removeBot(self, bot):
        if (bot in self.bots):
            self.bots.remove(bot)
            if bot.monster:
                self.monsters_bots -= 1
            else:
                self.players_bots -= 1

        self.game.releaseClientId(bot.id)

    def addBots(self, players):
        if len(self.bots) >= Cts.MAX_BOTS:
            return

        bots_to_add = (Cts.MAX_PLAYERS - players)
        if bots_to_add > self.max_bots:
            bots_to_add = self.max_bots

        if bots_to_add + len(self.bots) > Cts.MAX_PLAYERS:
            bots_to_add = Cts.MAX_PLAYERS - players

        if len(self.bots) + bots_to_add >= Cts.MAX_BOTS:
            bots_to_add = Cts.MAX_BOTS - len(self.bots)

        for i in range(0, bots_to_add):
            if self.monsters_bots > self.players_bots:
                bt = random.choice(Cts.BOTS_PLAYERS)
                monster = False
                self.players_bots += 1
            else:
                bt = random.choice(Cts.BOTS_MONSTERS)
                monster = True
                self.monsters_bots += 1
            bot = Client(None, bot=True, monster=monster, manager=self)
            bot_name = random.choice(Cts.BOTS_NICKS[bt])
            if bot_name.endswith("*"):
                bot.setNickname(bot_name[0:-1])
            elif len(bot_name):
                bot.setNickname("-".join([bot_name, str(random.randint(1, 99))]))

            self.game.addClient(bot, bt)
            self.bots.append(bot)

    def close():
        self.running = False

    def moveBot(self, bot):
        game_map = self.game.getMap()
        snake = bot.snake
        head = snake.getHead()

        cur_i = int(head.i)
        cur_j = int(head.j)

        new_i = head.i + snake.di
        new_j = head.j + snake.dj

        int_new_i = int(new_i)
        int_new_j = int(new_j)

        if int_new_i == cur_i and int_new_j == cur_j:
            # same position
            return

        pixel = game_map.pixel(int_new_i, int_new_j)
        if pixel.isBusy() and pixel.client != bot.id:
            # if pixel is busy change direction
            if snake.direction == Cts.DIRECTION_UP or snake.direction == Cts.DIRECTION_DOWN:
                pix_right = game_map.pixel(cur_i, cur_j + 1)
                pix_left = game_map.pixel(cur_i, cur_j - 1)

                pix_right_busy = pix_right.isBusy() and pix_right.client != bot.id
                pix_left_busy = pix_left.isBusy() and pix_left.client != bot.id

                if pix_right_busy:
                    snake.move(Cts.KEY_LEFT)
                elif pix_left_busy:
                    snake.move(Cts.KEY_RIGHT)
                else:
                    snake.move(Cts.KEY_RIGHT if random.randint(0, 1) == 1 else Cts.KEY_LEFT)
            else:
                pix_down = game_map.pixel(cur_i + 1, cur_j)
                pix_up = game_map.pixel(cur_i - 1, cur_j)

                pix_down_busy = pix_down.isBusy() and pix_down.client != bot.id
                pix_up_busy = pix_up.isBusy() and pix_up.client != bot.id

                if pix_down_busy:
                    snake.move(Cts.KEY_UP)
                elif pix_up_busy:
                    snake.move(Cts.KEY_DOWN)
                else:
                    snake.move(Cts.KEY_UP if random.randint(0, 1) == 1 else Cts.KEY_DOWN)

    def run(self):
        # Randomize bots movements
        previous_time = 0
        cur_time = 0
        game_map = self.game.getMap()

        while self.running:
            for bot in self.bots:
                if random.randint(0, 100) < Cts.PROBABILITY_BOT_MOVE:
                    snake = bot.snake
                    head = snake.getHead()
                    cur_i = int(head.i)
                    cur_j = int(head.j)

                    # Use keys instead of directions
                    movement = random.randint(Cts.DIRECTION_UP, Cts.DIRECTION_RIGHT)

                    if (movement < 2 and bot.snake.direction < 2) or (movement > 1 and bot.snake.direction > 1):
                        continue

                    busy = False
                    pix = None
                    if movement == Cts.DIRECTION_UP:
                        pix = game_map.pixel(cur_i - 1, cur_j)
                    elif movement == Cts.DIRECTION_DOWN:
                        pix = game_map.pixel(cur_i + 1, cur_j)
                    elif snake.direction == Cts.DIRECTION_RIGHT:
                        pix = game_map.pixel(cur_i, cur_j - 1)
                    else:
                        pix = game_map.pixel(cur_i, cur_j + 1)

                    busy = pix.isBusy() and pix.client != bot.id
                    if not busy:
                        bot.snake.move(str(movement))

            cur_time = time.time()
            elapsed_time = cur_time - previous_time

            # check if must sleep
            if elapsed_time < self.sleep_time:
                # sleep some time
                time.sleep(self.sleep_time - elapsed_time)

            previous_time = time.time()
