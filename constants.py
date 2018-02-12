class Constants:
    SNAKE_INITIAL_SIZE = 5
    SPEED_INCREMENT = 0.1

    STATE_EMPTY = 0
    STATE_BUSY = 1
    MOB_INCREASE = 16

    # Tiles contants

    STONES = [1, 6]
    CLAY = [6, 11]
    GRASS = [11, 16]
    MOB_FOOD_ITEMS = [16, 19]
    MOB_CORPSE = 19
    MOB_MOVE_SPEED = 20
    SNAKE_COLOR = 21 # TODO: change snakes colors


    # Messages types
    MESSAGE_MAP = chr(0)
    MESSAGE_HEAD = chr(1)
    MESSAGE_MOBS = chr(2)
    MESSAGE_SNAKE_SIZE = chr(3)
    MESSAGE_DEATH = chr(4)
    MESSAGE_RANKING = chr(5)
    MESSAGE_LEADERBOARD = chr(6)
    
