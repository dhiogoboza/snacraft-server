class Constants:
    # Game config
    #LINES = 150
    #COLUMNS = 150
    LINES = 60
    COLUMNS = 60
    SLEEP_TIME = 0.100
    MAX_BOTS = 1

    # Snakes config
    SNAKE_INITIAL_SIZE = 6
    SPEED_INCREMENT = 0.1
    INITIAL_SPEED = 0.5
    MAX_SNAKE_SIZE = 9999
    MAX_PLAYERS = 256

    # States
    STATE_EMPTY = 0
    STATE_BUSY = 1
    MOB_INCREASE = 16

    # Bots
    PROBABILITY_BOT_MOVE = 80
    BOTS = [30, 33, 35]
    # zombies, skeletons
    BOTS_NICKS = {BOTS[0]: ["zomber", "snombie", "zombinake", "zom"], BOTS[1]: ["snakeleton", "skelake", "toneike"], BOTS[2]: ["spidernake", "snaker"]}

    # Map
    WALLS_WIDTH = 5
    LOOPS_REMOVE_CORPSE = 10

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
    MOB_FOOD_ITEMS = [16, 20]
    MOB_CORPSE = [20, 23]
    MOB_MOVE_SPEED = 24
    SNAKE_COLOR = 25

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

    """
    Player speed information message type
    """
    MESSAGE_PLAYER_SPEED = chr(11)

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
