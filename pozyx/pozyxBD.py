
from apscheduler.schedulers.blocking import BlockingScheduler
import apscheduler
from commMedium import commMedium
from uwbMsg import blankData, UWBMessage
from parameters import uwbDic, NUM_NODES, SLOT_SIZE, MSG_BYTE_SIZE, RESCHEDULE_TIME, NUM_SLOTS, TDMA_SLOT_RELEASE_CODE, TDMA_MSG_CODE, RANGING_MSG_CODE
import time
from utlity import valueFrom4Byte, valueTo4Byte, setToBytes, rangeAgeTo3Byte
from pypozyx import DeviceRange, POZYX_SUCCESS, POZYX_FAILURE, SingleRegister

dictID2UWB = {uwbDic[x]:x for x in uwbDic}

class pozyxBD:
    def __init__(self, pozyx, tagID, commMedium, lock, logfile):
        self.pozyx = pozyx
        self.uwbID = None
        self.id = tagID
        self.actionCount = 0
        self.neibSet = set([])
        self.candSlots = set([])
        self.sendSlots = set([])
        self.commMedium = commMedium
        self.sharedLock = lock
        self.scheduler = BlockingScheduler()
        self.sleepTest = True

        #self.neibRangingAge = [0]*NUM_NODES
        self.sortRangingAge = []
        #self.neibRanging = [0]*NUM_NODES
        self.log = logfile


    def own_slot_execution(self):

        data = self.createMsg(TDMA_MSG_CODE)
        #print("Sending", data.data)
        with self.sharedLock:
            self.pozyx.sendData(destination=0, data=data)


    def updateFromCommMedium(self):
        self.neibSet = set([])
        self.candSlots = set([])
        self.sendSlots = set([])
        for i in range(NUM_NODES):
            if self.commMedium.neibArray[i] == 1:
                self.neibSet.add(i)
            if self.commMedium.candSlots[i] == 1:
                self.candSlots.add(i)
            if self.commMedium.sendSlots[i] == 1:
                self.sendSlots.add(i)
        self.candSlots.difference_update(self.neibSet)


    def extra_slot_execution(self):
        # 1. do ranging to target
        target = self.find_neib_to_ranging()
        targetUWB = dictID2UWB[target]
        with self.sharedLock:
            rangingResult = self.ranging_update(targetUWB)
        if rangingResult:
            self.commMedium.neibRanging[target] = rangingResult.distance
            self.commMedium.rangingAge[target] = 0
        # 2. broadcasting ranging: a: update from medium about ranging and age. b: broadcast the young ranging measurements.

            #self.updateRangingFromMedium()
            data = self.createMsg(RANGING_MSG_CODE)

            with self.sharedLock:
                self.pozyx.sendData(destination=0, data=data)
            pass

    def createMsg(self, type):
        data = blankData(MSG_BYTE_SIZE)
        if type == TDMA_MSG_CODE:
            bytesNum = int(NUM_NODES /8)+1
            
            synB = 4
            # Encode neib, candSlot, sendSlots data to send. Time is put in last second.
            data.data[synB:bytesNum+synB] = setToBytes(self.neibSet)
            data.data[bytesNum+synB:2*bytesNum+synB] = setToBytes(self.candSlots)
            data.data[2*bytesNum+synB:3*bytesNum+synB] = setToBytes(self.sendSlots)


            # Broadcast neib's cand slot for others
            st = 3*bytesNum+synB

            while((st + 2*bytesNum +1)  < MSG_BYTE_SIZE and not self.commMedium.reTransmitMsg.empty()):
                #print("bd size", self.commMedium.reTransmitMsg.qsize())
                temp = self.commMedium.reTransmitMsg.get_nowait()
                #print("bdTemp ", temp)
                cBit = 1 if len(temp[1])>0 else 0
                sBit = 1 if len(temp[2])>0 else 0
                #print("Sending", cBit, sBit, (cBit<<7)+(sBit<<6)+temp[0])
                data.data[st] =(cBit<<7)+(sBit<<6)+temp[0]
                st = st + 1
                if cBit == 1:
                    data.data[st:st+bytesNum] = setToBytes(set(temp[1]))
                    st = st + bytesNum
                if sBit == 1:
                    data.data[st:st+bytesNum] = setToBytes(set(temp[2]))
                    st = st + bytesNum

            #print("BD restartProposalFlag: ", self.commMedium.restartProposalFlag.value)
            if self.commMedium.realeaseSlots.value:
                data.data[-1] = TDMA_SLOT_RELEASE_CODE
                self.commMedium.realeaseSlots.value = 0
            else:   
                data.data[-1] = TDMA_MSG_CODE

            curTime = time.time() - self.commMedium.frameStartTime.value
            frameLength = NUM_SLOTS*SLOT_SIZE
            nanoSec = int(curTime%frameLength*1e9)
            data.data[0:synB] = valueTo4Byte(nanoSec)
            return data
        elif type == RANGING_MSG_CODE:
            
            st = 0
            bytesNum = 4 # ID,Ranging
            i = 0
            rangingAge = {i:self.commMedium.rangingAge[i] for i in self.neibSet}
            inverseSortRangingAge = sorted(rangingAge.items(), key=lambda x: x[1])
            size = len(self.neibSet)
            while (i < size) and ((st + bytesNum +1)  < MSG_BYTE_SIZE):
                toSendTargetId = inverseSortRangingAge[i][0]
                toSendRange = self.commMedium.neibRanging[toSendTargetId]
                measAge = self.commMedium.rangingAge[toSendTargetId]
                data.data[st] = toSendTargetId
                data.data[st+1:st+bytesNum] = rangeAgeTo3Byte(toSendRange, measAge)
                st = st + bytesNum
                i += 1 
                #print(" bd ", toSendTargetId, toSendRange, measAge)
            data.data[-1] = RANGING_MSG_CODE
            return data 



    def find_neib_to_ranging(self):
        rangingAge = {i:self.commMedium.rangingAge[i] for i in self.neibSet}
        self.sortRangingAge = sorted(rangingAge.items(), key=lambda x: x[1],reverse=True)

        #print(rangingAge, " sorted ", self.sortRangingAge)
        return self.sortRangingAge[0][0]

    def ranging_update(self,target):
        device_range = DeviceRange()

        status = self.pozyx.doRanging(target, device_range, None)
        if status == POZYX_SUCCESS:
            #self.log.write("\nrangingMeas")
            #print(uwbDic[target], device_range)
            return device_range
        else:
            error_code = SingleRegister()
            status = self.pozyx.getErrorCode(error_code)
            if status == POZYX_SUCCESS:
                #print("ERROR Ranging, local %s" %
                #      self.pozyx.getErrorMessage(error_code))
                pass
            else:
                #print("ERROR Ranging, couldn't retrieve local error")
                pass
            return False


    def update_schedule(self):
        self.commMedium.frameStartTime.value = time.time()
        if self.commMedium.timeToSleep.value != 0:
            self.clockSyncAdjust()

        pass

    def clockSyncAdjust(self):
        st = time.time()
        safeTimeToSleep = SLOT_SIZE*NUM_SLOTS + self.commMedium.timeToSleep.value*1e-9
        self.scheduler.remove_all_jobs()
        time.sleep(safeTimeToSleep-RESCHEDULE_TIME)
        self.scheduler.add_job( self.slot_actions, 'interval', seconds= SLOT_SIZE, id='uwbBD',)
        intv = time.time()-st
        extra = intv- safeTimeToSleep

        self.commMedium.actionCount.value = 0
        self.commMedium.timeToSleep.value = 0
        self.commMedium.frameStartTime.value = time.time()

        self.commMedium.restartProposalFlag.value = 1
        print("Adjust Scheduler for SYNC ",safeTimeToSleep , intv, extra)


    def slot_actions(self):
        self.updateFromCommMedium()
        #print("Slot action ", self.neibSet, self.candSlots, self.sendSlots)
        curSlotID = self.commMedium.actionCount.value%NUM_SLOTS
        if curSlotID == 0:
            self.update_schedule()
        elif curSlotID == self.id or curSlotID - NUM_NODES == self.id:
            self.own_slot_execution()
            #if len(self.neibSet)>0:
            #    self.extra_slot_execution()
        elif curSlotID in self.sendSlots or (curSlotID - NUM_NODES) in self.sendSlots:
            self.extra_slot_execution()
            pass
        else:
            pass
        self.commMedium.actionCount.value += 1
        for i in range(NUM_NODES):
            self.commMedium.rangingAge[i] += 1


    def scheStart(self):
        self.scheduler.add_job( self.slot_actions, 'interval', seconds= SLOT_SIZE, id='uwbBD',)
        self.scheduler.start()


