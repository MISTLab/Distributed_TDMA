# A fully distributed TDMA for highly mobile network

import numpy as np
from random import randrange
from matplotlib import pyplot as plt
import pickle
from mobileNode import mobileNode
import copy

COMM_RANGE  = 5

class simEnv:
    def __init__(self, numNodes):
        self.numNodes = numNodes
        self.nodesList = []


    def setupCustomize(self):
        posList = [ [0]*2 for i in range(self.numNodes)]
        posList[4] = [0,6.5]
        posList[13] = [0,7.5]
        posList[8] = [3,6.7]
        posList[12] = [6,7.2]
        posList[6] = [9,6.5]
        posList[10] = [9,7.5]
        posList[11] = [9,2.6]

        for i in range(self.numNodes):
            arenaSize = 10
            #initPos = [randrange(0,arenaSize*10)/10,randrange(0,arenaSize*10)/10]
            initPos = posList[i]
            self.nodesList.append(mobileNode(id=i, iniPos=initPos, numNodes=self.numNodes))

    def setupRandom(self, arenaSize):
        for i in range(self.numNodes):
            arenaSize = arenaSize
            initPos = [randrange(0,arenaSize*10)/10,randrange(0,arenaSize*10)/10]
            self.nodesList.append(mobileNode(id=i, iniPos=initPos, numNodes=self.numNodes))



    def clear(self):
        for i in range(self.numNodes):
            self.nodesList[i].tdmaManager.neighbors.clear()
            self.nodesList[i].tdmaManager.candSlots.clear()
            self.nodesList[i].tdmaManager.sendSlots.clear()
            self.nodesList[i].tdmaManager.siblingNeib.clear()
            self.nodesList[i].tdmaManager.neibsInfo = {}
            self.nodesList[i].tdmaManager.hop2neighbors.clear()



    def commStep(self):
        for i in range(self.numNodes):
            self.nodesList[i].oldAllNeib = set(self.nodesList[i].tdmaManager.neighbors.union(self.nodesList[i].tdmaManager.hop2neighbors))
            self.nodesList[i].tdmaManager.updateCandSlot(self.nodesList[i].tdmaManager.neibsInfo)
            self.nodesList[i].tdmaManager.neibsInfo = {}
            for ele in self.nodesList[i].tdmaManager.neighbors: 
                self.nodesList[i].tdmaManager.neibsInfo[ele] = neibInfo(self.nodesList[ele].tdmaManager.neighbors, self.nodesList[ele].tdmaManager.candSlots, self.nodesList[ele].tdmaManager.sendSlots )
            for ele in self.nodesList[i].tdmaManager.hop2neighbors: 
                self.nodesList[i].tdmaManager.neibsInfo[ele] = neibInfo(self.nodesList[ele].tdmaManager.neighbors, self.nodesList[ele].tdmaManager.candSlots, self.nodesList[ele].tdmaManager.sendSlots )

        pass
    
    def updateNeib(self):
        for i in range(self.numNodes):
            self.nodesList[i].tdmaManager.neighbors = set([])
        for i in range(self.numNodes):
            for j in range(i+1, self.numNodes):
                dist = [self.nodesList[i].pos[0] - self.nodesList[j].pos[0], self.nodesList[i].pos[1] - self.nodesList[j].pos[1]]
                if np.linalg.norm(dist) < COMM_RANGE:

                    self.nodesList[i].tdmaManager.neighbors.add(j)
                    self.nodesList[j].tdmaManager.neighbors.add(i)
        
        nodesNeibList={}
        for i in range(self.numNodes):
            nodesNeibList[i] = neibInfo(self.nodesList[i].tdmaManager.neighbors)

        for i in range(self.numNodes):
            self.nodesList[i].tdmaManager.updateHop2Neighbor(nodesNeibList)
    

    def neibChangingActions(self):
        for i in range(self.numNodes):
            curAllNeib = set(self.nodesList[i].tdmaManager.neighbors.union(self.nodesList[i].tdmaManager.hop2neighbors))
            if self.nodesList[i].oldAllNeib == curAllNeib: # no neib change
                pass
            else: # neib changed
                intsectNeib = set(self.nodesList[i].oldAllNeib.intersection(curAllNeib))
                leftNeib = set(self.nodesList[i].oldAllNeib.difference(intsectNeib))
                joinedNeib = set(curAllNeib.difference(intsectNeib))

                for ele in joinedNeib:
                    self.nodesList[i].tdmaManager.sendSlots.difference_update(joinedNeib)
                    #self.nodesList[i].tdmaManager.sendSlots.difference_update(self.nodesList[ele].tdmaManager.sendSlots)
                
                freedSlot = set([])
                for ele in leftNeib:
                    freedSlot.update(self.nodesList[i].tdmaManager.neibsInfo[ele].sendSlots)
                    self.nodesList[i].tdmaManager.neibsInfo.pop(ele, None)
                self.nodesList[i].tdmaManager.candSlots.update(freedSlot)






    def initialStep(self):

        curSit = copy.deepcopy(self.nodesList)
        for i in range(self.numNodes):
            self.nodesList[i].tdmaManager.initialSteps(curSit[i].tdmaManager.neibsInfo)

    def schedule(self):
        curSit = copy.deepcopy(self.nodesList)
        for i in range(self.numNodes):
            self.nodesList[i].tdmaManager.iterativeSteps(curSit[i].tdmaManager.neibsInfo)


    def collisionCheck(self):
        for t in range(self.numNodes):
            tNode = self.nodesList[t]
            occupiedSlot = set(tNode.tdmaManager.sendSlots)
            for i in tNode.tdmaManager.neighbors:
                interSet = occupiedSlot.intersection(self.nodesList[i].tdmaManager.sendSlots) 
                if len(interSet):
                    #print(tNode.id, i, " has collision", interSet, occupiedSlot)                 occupiedSlot.update(self.nodesList[i].tdmaManager.sendSlots)
                    pass


    def motionStep(self):
        for i in range(self.numNodes):
            motion = [randrange(0,10)/10,randrange(0,10)/10]
            oldPos = self.nodesList[i].pos 
            self.nodesList[i].pos = [oldPos[0]+motion[0], oldPos[1]+motion[1]]
        pass


    def draw(self, step):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        plt.grid(True)

        for i in range(self.numNodes):
            plt.scatter(self.nodesList[i].pos[0],self.nodesList[i].pos[1])
            plt.text(self.nodesList[i].pos[0],self.nodesList[i].pos[1],str(i)+str(self.nodesList[i].tdmaManager.neighbors)+str(self.nodesList[i].tdmaManager.hop2neighbors)+str(self.nodesList[i].tdmaManager.siblingNeib), fontsize=5)
            plt.text(self.nodesList[i].pos[0],self.nodesList[i].pos[1]-0.2,str(self.nodesList[i].tdmaManager.candSlots) + str(self.nodesList[i].tdmaManager.sendSlots), fontsize=5)
        plt.tight_layout()
        plt.savefig("./results/simulations/"+str(step)+".svg")


    def drawBrifSend(self, step):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        plt.grid(True)

        for i in range(self.numNodes):
            plt.scatter(self.nodesList[i].pos[0],self.nodesList[i].pos[1])
            #plt.text(self.nodesList[i].pos[0],self.nodesList[i].pos[1],str(i)+str(self.nodesList[i].tdmaManager.neighbors)+str(self.nodesList[i].tdmaManager.hop2neighbors)+str(self.nodesList[i].tdmaManager.siblingNeib), fontsize=5)
            plt.text(self.nodesList[i].pos[0],self.nodesList[i].pos[1]-0.2,str(i)+str(self.nodesList[i].tdmaManager.sendSlots), fontsize=5)
        plt.tight_layout()
        plt.savefig("./results/simulations/"+str(step)+"_send.svg")


    def drawBrifCand(self, step):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        plt.grid(True)

        for i in range(self.numNodes):
            plt.scatter(self.nodesList[i].pos[0],self.nodesList[i].pos[1])
            #plt.text(self.nodesList[i].pos[0],self.nodesList[i].pos[1],str(i)+str(self.nodesList[i].tdmaManager.neighbors)+str(self.nodesList[i].tdmaManager.hop2neighbors)+str(self.nodesList[i].tdmaManager.siblingNeib), fontsize=5)
            plt.text(self.nodesList[i].pos[0],self.nodesList[i].pos[1]-0.2,str(i)+str(self.nodesList[i].tdmaManager.candSlots), fontsize=5)
        plt.tight_layout()
        plt.savefig("./results/simulations/"+str(step)+"_cand.svg")


class neibInfo():
    def __init__(self, neighbors = set([]), candSlots = set([]), sendSlots = set([])):
        self.neighbors = neighbors
        self.candSlots = candSlots
        self.sendSlots = sendSlots