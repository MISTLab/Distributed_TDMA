# A fully distributed TDMA for highly mobile network

import numpy as np
from random import randrange
import matplotlib 
from matplotlib import pyplot as plt
import pickle
import random
import copy



class mddTdma:
    def __init__(self, id, numNodes):
        self.id = id
        self.numNodes = numNodes
        self.position = [0,0]
        self.neighbors = set([])
        self.hop2neighbors = set([])
        self.candSlots = set([])
        self.neighborSlots = set([])
        self.siblingNeib = set([])
        self.filtedSlot = set([])
        self.firstPick = False
        self.sendSlots = set([self.id])
        self.neibsInfo = {}
        self.usageBuf = []
        self.candSlotsRecords = []

    def updateNeighbor(self, nodes):
        for i in range(self.numNodes):
            if np.linalg.norm([nodes[i].position[0] - self.position[0], nodes[i].position[1] - self.position[1]]) < COMM_RANGE and i != self.id:
                self.neighbors.add(nodes[i].id)

    def updateHop2Neighbor(self, nodes):
        allNeibs = set([])
        for neib in self.neighbors:
            allNeibs.update(nodes[neib].neighbors)
        
        self.hop2neighbors = set(allNeibs.difference(self.neighbors))
        self.hop2neighbors.difference_update(set([self.id]))


    def updateCandSlot(self, nodes):
        self.candSlots = set(list(range(1,self.numNodes)))
        self.candSlots.difference_update(set([self.id]))
        self.candSlots.difference_update(self.sendSlots)
        curAllNeibs = set(self.neighbors.union(self.hop2neighbors))
        for neib in curAllNeibs:
            if neib in nodes:
                self.candSlots.difference_update(nodes[neib].sendSlots)
            self.candSlots.difference_update(set([neib]))

        #print("updateCandSlot", self.candSlots)

    
    def siblingNeibFilter(self,nodes):
        id = self.id
        if len(self.candSlots)>0:
            self.siblingNeib = set([])
            curAllNeibs = set(self.neighbors.union(self.hop2neighbors))
            for neib in curAllNeibs:
                if neib in nodes and set(nodes[neib].candSlots) == set(self.candSlots):
                    self.siblingNeib.add(neib)


    def slotFilter(self, nodes):
        self.filtedSlot = set(self.candSlots)
        self.firstPick = False
        curAllNeibs = set(self.neighbors.union(self.hop2neighbors))
        for neib in curAllNeibs-set(self.siblingNeib):
            if neib in nodes and (not nodes[neib].candSlots.issuperset(self.candSlots)):
                self.filtedSlot.difference_update(nodes[neib].candSlots.intersection(self.candSlots))
                self.firstPick = True

    def addVirtualSlots(self):

        if len(self.filtedSlot)>0:
            if len(self.siblingNeib) == 0:
                if False:# len(self.filtedSlot)>1.5*int(self.numNodes/len(self.neighbors)):
                    temp = list(self.filtedSlot)
                    halfSet = [temp[i] for i in range(len(self.filtedSlot)) if i%2==0] # select half of filtedSlot to occupied
                    self.sendSlots.update(set(halfSet))
                    self.filtedSlot=set(halfSet)
                else:
                    self.sendSlots.update(self.filtedSlot)
                self.candSlots.difference_update(self.filtedSlot)
            else:
                tempSet = self.siblingNeib
                tempSet.add(self.id)
                groupids = list(tempSet)
                groupids.sort()
                groupSize = len(self.siblingNeib)
                rank = groupids.index(self.id)
                sharedSlots = list(self.filtedSlot)
                sharedSlots.sort()
                slotSize = len(sharedSlots)
                temp = rank
                while temp < slotSize:
                    self.sendSlots.add(sharedSlots[temp])
                    temp += groupSize
                pass

    def virtualNeibSlotUpdate(self, nodes):
        curAllNeibs = set(self.neighbors.union(self.hop2neighbors))
        self.updateCandSlot(nodes)
        self.candSlots.difference_update(self.sendSlots)


    def collisionCheck(self, nodes):
        
        myNeib = list(self.neighbors)
        size = len(myNeib)
        for i in range(size):
            for j in range(i, size):
                if i != j and len(nodes[myNeib[i]].sendSlots.intersection(nodes[myNeib[j]].sendSlots)):
                    print("selfCheck", myNeib[i], myNeib[j], " has collision", nodes[myNeib[i]].sendSlots.intersection(nodes[myNeib[j]].sendSlots))

    def solveCollision(self,nodes):
        curNeib = set(self.neighbors.union(self.hop2neighbors))
        for ele in curNeib:
            collisionSlots = set([])
            if ele in nodes:
                collisionSlots = self.sendSlots.intersection(nodes[ele].sendSlots) 
            if collisionSlots:
                #print("Got sending collision", collisionSlots)
                mySize = len(self.sendSlots) 
                neibSize = len(nodes[ele].sendSlots)
                if mySize > neibSize or (mySize == neibSize and self.id < ele) :
                #if self.id < ele:
                    self.sendSlots.difference_update(collisionSlots)
                    #print("solve collision", collisionSlots)
                    pass

    def slotUsageCheck(self, nodes):
        curNeib = set(self.neighbors.union(self.hop2neighbors))
        usedSlot = set(self.sendSlots)
        slotCount = len(self.sendSlots)
        for ele in curNeib:
            if ele in nodes:
                usedSlot.update(nodes[ele].sendSlots)
                slotCount += len(nodes[ele].sendSlots)
        #print(self.id, " used ", len(usedSlot), " rate ", len(usedSlot)/(self.numNodes-1), slotCount/(self.numNodes-1))

    def initialSteps(self, nodes):
        self.updateHop2Neighbor(nodes)
        self.updateCandSlot(nodes)


    def dilemmaCheck(self):
        if len(self.candSlotsRecords)>3:
            if len(self.candSlotsRecords[0])>0 and self.candSlotsRecords[0] == self.candSlotsRecords[0] and self.candSlotsRecords[0] == self.candSlotsRecords[2]:
                self.candSlotsRecords = []
                return True
            else:
                self.candSlotsRecords.pop(0)
                return False

    def dilemmaHandling(self):
        avgSlotSize = int(len(self.candSlots)/len(self.neighbors))
        randomSelect = set(random.choices(list(self.candSlots), k=avgSlotSize))
        self.sendSlots.update(randomSelect)
        self.candSlots.difference_update(randomSelect)



    def iterativeSteps(self, nodes):
        #self.collisionCheck(nodes)
        self.solveCollision(nodes)
        self.slotUsageCheck(nodes)
        self.virtualNeibSlotUpdate(nodes)  
        if (len(self.candSlots)>0):
            self.siblingNeibFilter(nodes)
            self.slotFilter(nodes) 
            self.addVirtualSlots()   
            self.candSlots.difference_update(self.filtedSlot)
            self.candSlotsRecords.append(self.candSlots)

            if self.dilemmaCheck():
                self.dilemmaHandling()
        else:
            pass


    def slotUsageCorrect(self):
        curNeib = set(self.neighbors.union(self.hop2neighbors))
        totalFreeSlot = self.numNodes - len(curNeib)
        curUsage = len(self.sendSlots)/totalFreeSlot
        self.usageBuf.append(curUsage)
        if len(self.usageBuf)>4:
            self.usageBuf.remove(self.usageBuf[0])
        avgUsage = 1/(len(curNeib)+1)
        #print(" avg usage ", avgUsage, " myusage ", curUsage)
        if curUsage > 2.5*avgUsage and np.mean(self.usageBuf) > 2.3*avgUsage and len(self.usageBuf)>3:
            temp = copy.copy(self.sendSlots)
            numToDiscard = len(self.sendSlots) - 0.8*avgUsage*totalFreeSlot
            setDiscarded = set([])
            i = 0
            for ele in temp:
                if i < numToDiscard:
                    self.sendSlots.discard(ele)
                    setDiscarded.add(ele)
                    i += 1
                else: break
            self.candSlots.update(setDiscarded)
            print(" release slots", i, setDiscarded)
            self.usageBuf = []
            return True
        return False

  

def draw(nodes, id):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    plt.grid(True)

    for i in range(SIZE_NODES):
        plt.scatter(nodes[i].position[0],nodes[i].position[1])
        plt.text(nodes[i].position[0],nodes[i].position[1],str(i)+str(nodes[i].neighbors)+str(nodes[i].hop2neighbors)+str(nodes[i].siblingNeib), fontsize=5)
        plt.text(nodes[i].position[0],nodes[i].position[1]-0.5,str(nodes[i].candSlots) + str(nodes[i].sendSlots), fontsize=5)
    plt.savefig("./v2/tdmaCore/mddTdma" + id + ".svg")



SIZE_NODES = 10 # same as slots size
COMM_RANGE = 7

if __name__ == "__main__":
    nodes = []

    new = 0
    if new:
        for i in range(SIZE_NODES):
            x = randrange(200)/10.0
            y = randrange(200)/10.0
            nodes.append(mddTdma(i,SIZE_NODES))
            nodes[-1].position = [x, y]

        pickle.dump(nodes, open("./v2/tdmaCore/mddTdma.p", "wb"))
    else:
        nodes = pickle.load(open("./v2/tdmaCore/mddTdma.p", "rb")) 
        #nodes = pickle.load(open("mdtdmaSave_collisionCase.p", "rb")) 
        SIZE_NODES = len(nodes)

    for i in range(SIZE_NODES):
        nodes[i].updateNeighbor(nodes)

    curState = copy.deepcopy(nodes) # Simulated the communication state
    for i in range(SIZE_NODES):
        nodes[i].initialSteps(curState)

    draw(nodes, str(0))

    for step in range(1,10):
        curState = copy.deepcopy(nodes) # Simulated the communication state
        for i in range(SIZE_NODES):
            nodes[i].iterativeSteps(curState)
        
        draw(nodes, str(step))

    for i in range(SIZE_NODES):
        print("id", i, nodes[i].neighbors, nodes[i].hop2neighbors, nodes[i].candSlots,"---", nodes[i].siblingNeib, nodes[i].filtedSlot, "---", nodes[i].sendSlots)
        nodes[i].collisionCheck(nodes)

    pass




