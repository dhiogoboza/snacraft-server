import utils

from constants import Constants as Cts

class Pixel():

    def __init__(self, i, j, it):
        self.i = i
        self.j = j
        self.it = it

    def getIChar(self):
        return chr(utils.toint(self.i))

    def getJChar(self):
        return chr(utils.toint(self.j))

    def copy(self):
        return Pixel(self.i, self.j, self.it)

class MapPixel(Pixel):

    def __init__(self, i, j, it, state, mob, client):
        Pixel.__init__(self, i, j, it)
        self.state = state
        self.mob = mob
        self.client = client

    def getIChar(self):
        return chr(self.i)

    def getJChar(self):
        return chr(self.j)

    def withoutMob(self):
        return self.mob == Cts.STATE_EMPTY

    def hasMob(self):
        return self.mob != Cts.STATE_EMPTY

    def isBusy(self):
        return self.state != Cts.STATE_EMPTY

    def isEmpty(self):
        return self.state == Cts.STATE_EMPTY
