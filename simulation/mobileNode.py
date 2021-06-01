# A fully distributed TDMA for highly mobile network

import numpy as np
from random import randrange
from matplotlib import pyplot as plt
import pickle
import sys, os

upperFolderDir =  os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(upperFolderDir,'tdmaCore'))

from mddTdma import mddTdma


class mobileNode():
    def __init__(self, id, iniPos, numNodes):
        self.id = id
        self.tdmaManager = mddTdma(id, numNodes)
        self.initialPos = iniPos
        self.pos = iniPos
        self.recvMsgList = []
        self.toBraodcastList = []
        self.oldAllNeib = set([])
        self.restartFlag = False
        self.hangOneScheStep = False

    def receive_msg(self):
        pass

    def broadcast_msg(self):
        pass

    def reset(self):

        self.tdmaManager.candSlots.clear()
        self.tdmaManager.sendSlots.clear()
        #self.neibsInfoDict = {}
        self.restartFlag = True
        pass


if __name__ == "__main__":
    pass