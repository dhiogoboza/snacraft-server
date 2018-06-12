class Constants:
    # Game config
    LINES = 150
    COLUMNS = 150
    SLEEP_TIME = 0.100
    MAX_BOTS = 10

    # Snakes config
    SNAKE_INITIAL_SIZE = 6
    SPEED_INCREMENT = 0.1
    INITIAL_SPEED = 0.5
    MAX_SNAKE_SIZE = 230
    MAX_PLAYERS = 255

    # States
    STATE_EMPTY = 0
    STATE_BUSY = 1
    MOB_INCREASE = 16

    # Bots
    PROBABILITY_BOT_MOVE = 80
    BOTS = [29, 32]
    # zombies, skeletons
    BOTS_NICKS = {29: ["zomber", "snombie", "zombinake", "zom"], 32: ["snakeleton", "skelake", "toneike"]}

    # Map
    WALLS_WIDTH = 5

    # Keys
    # TODO: client message to bytes
    KEY_UP = "0"
    KEY_DOWN = "1"
    KEY_LEFT = "2"
    KEY_RIGHT = "3"

    # Directions
    DIRECTION_UP = 0
    DIRECTION_DOWN = 1
    DIRECTION_LEFT = 2
    DIRECTION_RIGHT = 3

    # Tiles contants
    STONES = [1, 6]
    CLAY = [6, 11]
    GRASS = [11, 16]
    MAX_OBSTACLE_TILE = GRASS[1]
    MOB_FOOD_ITEMS = [16, 19]
    MOB_CORPSE = [19, 22]
    MOB_MOVE_SPEED = 23
    SNAKE_COLOR = 24

    # Messages types
    MESSAGE_MAP = chr(0)
    MESSAGE_CLIENT_DATA = chr(1)
    MESSAGE_MOBS = chr(2)
    MESSAGE_DEATH = chr(4)

    """
    Send players name, message:
    [MSG_PLAYERS | P0_ID | P0_NAME_SIZE | P0_NAME | P1_ID | P1_NAME_SIZE | P1_NAME | ...]
    """
    MESSAGE_PLAYERS = chr(7)

    """
    Inform that a client left or died
    """
    MESSAGE_PLAYER_EXITED = chr(8)

    """
    Inform in game players count
    """
    MESSAGE_PLAYERS_SIZE = chr(9)

    """
    Sound id to be played by the client
    """
    MESSAGE_SOUND = chr(10)

    @staticmethod
    def getDirectionStr(direction):
        if direction == Constants.DIRECTION_UP:
            return "UP"
        elif direction == Constants.DIRECTION_DOWN:
            return "DOWN"
        elif direction == Constants.DIRECTION_RIGHT:
            return "RIGHT"
        elif direction == Constants.DIRECTION_LEFT:
            return "LEFT"
