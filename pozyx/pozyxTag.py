from pypozyx import (Data)
import time
from random import random, randint
import sys, os
from parameters import uwbDic, NUM_NODES, SLOT_SIZE, CLOCK_DIFF_THRESHOLD, MSG_BYTE_SIZE, NUM_SLOTS, TDMA_MSG_CODE, RANGING_MSG_CODE, TDMA_SLOT_RELEASE_CODE, NEIB_AGE_BUF

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tdmaCore'))

from mddTdma import mddTdma
from commManager import commManager
from commMedium import commMedium
from uwbMsg import blankData, UWBMessage, decodedTDMAData
import copy
from utlity import valueFrom4Byte, valueTo4Byte, setToBytes, setFromBytes, rangeAgeFrom3Byte

import numpy as np

class pozyxTag:
    def __init__(self, pozyx, uwbID, tagID, commMedium, lock, logfile):

        self.pozyx  = pozyx
        self.uwbID = uwbID
        self.id = tagID

        self.pozyxLock = lock
        self.commMedium = commMedium

        self.tdmaManager = mddTdma(self.id, NUM_NODES)
        self.commManager = commManager(self.pozyx, self.pozyxLock, self.commMedium)
        self.spacialManager = None
        
        self.frameSendSlots = []

        self.neibsInfoDict = {}
        self.diffNeib = set([])

        self.clockOffset = 0
        self.smallerNeibID = self.id
        self.syncEndTime = 0
        self.newMsgArrved = False
        self.neibsAge = [0]*NUM_NODES
        self.heardSlots = set([])
        self.startFlag = True
        self.synedFlag = False
        self.hangOneScheStep = False

        self.oldAllNeib = set([])
        self.rangingMap = np.zeros((NUM_NODES,NUM_NODES))
        self.rangingAge = np.zeros((NUM_NODES,NUM_NODES))

        self.lastActionCount = 0
        
        self.log = logfile 
        self.notDoneUpdate = True

        self.startingTime = time.time()


        


    def run(self):
        self.listen()
        #print(self.commMedium.actionCount.value)
        if self.lastActionCount != self.commMedium.actionCount.value:
            self.rangingAge = self.rangingAge + np.ones((NUM_NODES,NUM_NODES))
            #print(" update ranging age", self.rangingAge[0][0])
            self.lastActionCount = self.commMedium.actionCount.value
            if not self.notDoneUpdate:
                self.notDoneUpdate = True
        
        if self.commMedium.actionCount.value % NUM_NODES == 0 and self.newMsgArrved and self.notDoneUpdate: # Update once on Slot 0
            #print("run action",self.commMedium.actionCount.value)
            if self.synedFlag and self.commMedium.actionCount.value % NUM_SLOTS == 0:
                self.liveNeibUpdate()
                self.tdmaSchedule()
            self.updateToCommMedium()
            self.newMsgArrved = False
            self.notDoneUpdate = False
            #print("After scheduling", self.tdmaManager.neighbors, self.tdmaManager.candSlots, self.tdmaManager.sendSlots)

        

    def diffNeibSearch(self):
        self.diffNeib = set([])
        for ele in self.tdmaManager.neighbors:
            myUnique = set(self.tdmaManager.neighbors.difference(self.neibsInfoDict[ele].neighbors))
            self.diffNeib.update(myUnique)
        #print("diffNeib add ", self.diffNeib)

    def listen(self):
        dataReceived  = self.commManager.receive_new_msg()

        if dataReceived == TDMA_MSG_CODE:
            self.updateNeibInfo(self.commManager.newMsg)
            self.newMsgArrved = True
        elif dataReceived == RANGING_MSG_CODE:
            self.updateRanging(self.commManager.newMsg)
        elif dataReceived == TDMA_SLOT_RELEASE_CODE:
            self.updateNeibInfo(self.commManager.newMsg)
            self.newMsgArrved = True
            self.hangOneScheStep = True            
        else:
            pass

    def updateRanging(self, newMsg):
        data = self.commManager.newMsg.data
        senderID = uwbDic[self.commManager.newMsg.uwb_id]
        self.tdmaManager.neighbors.add(senderID)
        
        st = 0
        bytesNum = 4 # ID,Ranging
        while ((st + bytesNum +1)  < MSG_BYTE_SIZE) and data[st]!=0:
            receivedTargetId = data[st]
            [rangeMeas, age] = rangeAgeFrom3Byte(data[st+1:st+bytesNum])
            st = st + bytesNum
            #print("Received Ranging meas ", senderID, receivedTargetId, rangeMeas, age)
            if senderID < NUM_NODES and receivedTargetId < NUM_NODES:
                smallerID = int(min(senderID, receivedTargetId))
                biggerID = int(max(senderID, receivedTargetId))
                self.rangingMap[biggerID][smallerID] = rangeMeas
                self.rangingAge[biggerID][smallerID] = age

                if receivedTargetId == self.id and age < self.commMedium.rangingAge[senderID]:
                    self.commMedium.rangingAge[senderID] = age
                    self.commMedium.neibRanging[senderID] = rangeMeas
                    

        pass

    def updateNeib(self):
        
        self.tdmaManager.neighbors = set([])
        self.tdmaManager.updateHop2Neighbor(self.neibsInfoDict)
    

    def tdmaSchedule(self):
        curStep =  self.commMedium.actionCount.value
        self.log.write("\nStep "+str(curStep)+" time "+str(time.time()-self.startingTime))
        #print("Iterative Steps", curStep)
        if self.startFlag:
            self.tdmaManager.initialSteps(self.neibsInfoDict)
            self.startFlag = False
        else:
            self.liveHop2NeibUpdate()
            self.neibChangeActions()
            self.diffNeibSearch()
            if self.hangOneScheStep:
                self.hangOneScheStep = False
                self.tdmaManager.updateCandSlot(self.neibsInfoDict)
                #print(" hangOneScheStep, by pass one ")
                pass
            else:
                self.tdmaManager.iterativeSteps(self.neibsInfoDict)
                if self.tdmaManager.slotUsageCorrect():
                    self.hangOneScheStep = True
                    self.commMedium.realeaseSlots.value = 1

                # Dirty fix to force every node got one extra slot.
                resultSendSlot = set(self.tdmaManager.sendSlots)
                resultSendSlot.difference_update(set([self.id]))
                if len(resultSendSlot) == 0:
                    endPoint = NUM_NODES-1
                    randomSlot = randint(16,endPoint)
                    self.tdmaManager.sendSlots.add(randomSlot)
                    #print(randomSlot, self.tdmaManager.sendSlots)


                self.log.write("\nSchedule "+str(self.id)+str(self.tdmaManager.sendSlots)+" neibInfo "+str(self.tdmaManager.neighbors)+str(self.tdmaManager.hop2neighbors))
                print(" Schedule ", self.id, self.tdmaManager.sendSlots)

                curNeib = set(self.tdmaManager.neighbors.union(self.tdmaManager.hop2neighbors))
                target = copy.copy(curNeib)
                for ele in curNeib:
                    for to in target:
                        if to > ele :
                            self.log.write("\n ranging "+str(ele)+" to "+ str(to)+" " + str(self.rangingMap[to][ele]) + " age " + str(self.rangingAge[to][ele]))

                for ele in curNeib:
                    self.log.write("\n ranging "+str(self.id)+" to "+ str(ele)+" " + str(self.commMedium.neibRanging[ele]) + " age " + str(self.commMedium.rangingAge[ele]))


    def updateNeibInfo(self, newMsg):

        recvTimeToFrameStart = newMsg.timestamp - newMsg.curFrameTime

        data = self.decodeTDMA(newMsg)

        frameLength = NUM_SLOTS*SLOT_SIZE
        timeDiff = int(recvTimeToFrameStart%frameLength*1e9) - data.sendTimeNanoSecFromStart
        #print("time to start ", self.commMedium.frameStartTime.value, self.commMedium.actionCount.value)
        #print("Decoded received ",data.sendTimeNanoSecFromStart, data.dataSenderId, data.neibs, data.neibCandSlots, data.neibNeibCandSlots, int(recvTimeToFrameStart%1*1e9), timeDiff)
        if data.dataSenderId <= self.smallerNeibID:
            if abs(timeDiff) > CLOCK_DIFF_THRESHOLD:
                self.commMedium.timeToSleep.value = timeDiff
                #print("set time diff ",timeDiff)
                #self.log.write("set time diff ",timeDiff)
                self.synedFlag = False
                if data.dataSenderId < self.smallerNeibID:
                    self.smallerNeibID = data.dataSenderId
            else:
                self.synedFlag = True
        if self.smallerNeibID == self.id:
            self.synedFlag = True


        self.tdmaManager.neighbors.add(data.dataSenderId)
        self.neibsInfoDict[data.dataSenderId] = nodeInfo(neighbors=set(data.neibs), candSlots = set(data.neibCandSlots), sendSlots = set(data.neibSendSlots))

        for ele in data.neibs: # create entry for potential hop2 neib if not exist
            if ele not in self.neibsInfoDict:
                self.neibsInfoDict[ele] = nodeInfo()

        self.log.write("\nrcv"+str(data.dataSenderId)+str(data.neibSendSlots)+" "+str(data.neibCandSlots)+str(data.msgCode))
        #print(" rcv ",  data.dataSenderId, data.neibCandSlots, data.neibSendSlots, data.msgCode)
        # print("Received neibNeib", data.neibNeibCandSlots)
        for ele in data.neibNeibCandSlots:
            if ele not in self.tdmaManager.neighbors and ele != self.id:
                self.neibsInfoDict[ele] = nodeInfo(candSlots = data.neibNeibCandSlots[ele], sendSlots = set(data.neibNeibSendSlots[ele]))
                #print("rcv neibNeib ",ele,  data.neibNeibCandSlots[ele], data.neibNeibSendSlots[ele])
       
        self.neibsAge[data.dataSenderId] = 0 



            


    def decodeTDMA(self, newMsg): # Msg protocol: neibCandSlots|neibSendSlots|{targetID(neibneibID,6bit)|tID_SendSlotsBit|tID_CandSlotsBit|tID_SendSlot(if has)|tID_CandSlots(if has) ...}
        data = newMsg.data
        neibID = uwbDic[newMsg.uwb_id]

        bytesNum = int(NUM_NODES /8)+1
        timeBytes = 4
        sendTimeNanoSec = valueFrom4Byte(data[0:timeBytes])

        neibs = setFromBytes(data.data[timeBytes:bytesNum+timeBytes])
        neibCandSlots = setFromBytes(data.data[bytesNum+timeBytes:2*bytesNum+timeBytes])
        neibSendSlots = setFromBytes(data.data[2*bytesNum+timeBytes:3*bytesNum+timeBytes])
        msgCode = data.data[-1]

        st = 3*bytesNum+timeBytes
        neibNeibCandSlots = {}
        neibNeibSendSlots = {}
        while ((st + bytesNum +1) < MSG_BYTE_SIZE and data[st] != 0):
            
            v = data[st]
            tID = v&((1<<6)-1)
            sBit = (v>>6)&1
            cBit = (v>>7)&1      

            st = st+1
            if cBit==1:
                neibNeibCandSlots[tID] = setFromBytes(data[st: st+bytesNum])
                st = st+bytesNum
            else:
                neibNeibCandSlots[tID] = set([])

            if sBit==1:
                neibNeibSendSlots[tID] = setFromBytes(data[st: st+bytesNum])
                st = st+bytesNum
            else:
                neibNeibSendSlots[tID] = set([])
            #print("decode ", neibNeibCandSlots[tID], neibNeibSendSlots[tID] )
        
        #print("neibNeibSendSlots", neibNeibSendSlots)
        return decodedTDMAData(sendTimeNanoSec, neibID, neibs, neibCandSlots, neibSendSlots, neibNeibCandSlots, neibNeibSendSlots, msgCode)

    def liveNeibUpdate(self):
        self.neibsAge = [x+1 for x in self.neibsAge]
        for ele in copy.copy(self.tdmaManager.neighbors):
            if self.neibsAge[ele] > NEIB_AGE_BUF: # this neib is left
                self.tdmaManager.neighbors.remove(ele)
                #print(ele , " leave my neig with age", self.neibsAge[ele] )

    def liveHop2NeibUpdate(self):
        self.tdmaManager.updateHop2Neighbor(self.neibsInfoDict)
        
    def neibChangeActions(self):
        curAllNeib = set(self.tdmaManager.neighbors.union(self.tdmaManager.hop2neighbors))
        freedSlot = set([])
        if self.oldAllNeib == curAllNeib: # no neib change
            pass
        else: # neib changed
            intsectNeib = set(self.oldAllNeib.intersection(curAllNeib))
            leftNeib = set(self.oldAllNeib.difference(intsectNeib))
            joinedNeib = set(curAllNeib.difference(intsectNeib))

            for ele in joinedNeib:
                self.tdmaManager.sendSlots.difference_update(joinedNeib)
            
            for ele in leftNeib:
                self.hangOneScheStep = True
                freedSlot.update(self.neibsInfoDict[ele].sendSlots)
                #self.neibsInfoDict.pop(ele, None)
            self.tdmaManager.candSlots.update(freedSlot)
            #print("neib ", self.tdmaManager.neighbors, self.tdmaManager.hop2neighbors, len(self.neibsInfoDict), "free-candslot ", freedSlot, self.tdmaManager.candSlots)

        self.oldAllNeib = curAllNeib

    def reset(self):

        self.tdmaManager.candSlots.clear()
        self.tdmaManager.sendSlots.clear()
        #self.neibsInfoDict = {}
        for ele in self.tdmaManager.neighbors:
            self.neibsInfoDict[ele].neighbors.clear()
            self.neibsInfoDict[ele].candSlots.clear()
            self.neibsInfoDict[ele].sendSlots.clear()
        #self.tdmaManager.neighbors.clear()
        self.startFlag = True
        pass

    def updateToCommMedium(self):

        #self.tdmaManager.candSlots.difference_update(self.heardSlots)
        self.tdmaManager.candSlots.difference_update(self.tdmaManager.sendSlots)

        for i in range(NUM_NODES):
            self.commMedium.neibArray[i] = 0
            self.commMedium.candSlots[i] = 0
            self.commMedium.sendSlots[i] = 0
        for ele in self.tdmaManager.neighbors:
            self.commMedium.neibArray[ele] = 1
        for ele in self.tdmaManager.candSlots:
            self.commMedium.candSlots[ele] = 1
        for ele in self.tdmaManager.sendSlots:
            self.commMedium.sendSlots[ele] = 1
        #print("diffNeib ", self.diffNeib, " Total neibInfo size ", len(self.neibsInfoDict))
        for ele in self.diffNeib:
            neibSlotsToBD = [ele, list(self.neibsInfoDict[ele].candSlots), list(self.neibsInfoDict[ele].sendSlots) ]
            #print( "neibSlotsToBD ", neibSlotsToBD)
            self.commMedium.reTransmitMsg.put_nowait(neibSlotsToBD)

        self.heardSlots.clear()


def getFromMap(aID, bID, infoMap):
    smallerID = int(min(aID, bID))
    biggerID = int(max(aID, bID))
    return infoMap[biggerID][smallerID]

    
        



class nodeInfo:
    def __init__(self, neighbors = set([]), candSlots = set([]), sendSlots = set([])):
        self.neighbors = neighbors
        self.candSlots = candSlots
        self.sendSlots = sendSlots


if __name__ == "__main__":

    try:
        a = set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19])
        #b = valueTo4Byte(valueFrom4Byte(a))
        #print(a, b)
        print(setFromBytes(setToBytes(a)))
        a = blankData(10)


    except (KeyboardInterrupt, SystemExit):

        pass
