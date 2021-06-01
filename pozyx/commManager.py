from pypozyx import (Data, RXInfo)
import time 
from struct import error as StructError
from uwbMsg import UWBMessage, blankData
from parameters import uwbDic, TDMA_MSG_CODE, RANGING_MSG_CODE, MSG_BYTE_SIZE
from commMedium import commMedium

def decode(data):

    pass

class commManager:
    def __init__(self, pozyx, lock, commMedium):
        self.pozyx = pozyx
        self.sharedLock = lock
        self.lastMsgMetaData = blankData(MSG_BYTE_SIZE)
        with self.sharedLock:
            self.pozyx.readRXBufferData(self.lastMsgMetaData)
        self.msgDict = {}
        self.newMsg = None
        self.commMedium = commMedium

    def receive_new_msg(self):
        info = RXInfo()
        try:
            with self.sharedLock:
                self.pozyx.getRxInfo(info)
            recvTime = time.time()
        except StructError as s:
            print("RxInfo crashes! ", str(s))
        data = blankData(MSG_BYTE_SIZE)

        if info[1] == data.byte_size:
            with self.sharedLock:
                self.pozyx.readRXBufferData(data)
            #print("receive ", data.data)
            if data != self.lastMsgMetaData:
                curMsg = UWBMessage(info[0], data, recvTime, self.commMedium.frameStartTime.value)
                self.lastMsgMetaData = data
                if curMsg.uwb_id in self.msgDict and self.msgDict[curMsg.uwb_id] == curMsg: # Make sure it's new msg from robot of uwb_id
                    return False
                else:
                    self.msgDict[curMsg.uwb_id] = curMsg
                    self.newMsg = curMsg
#                    print("Receive ", info[0], info[1], data)
                    return data[-1]

        return False
            

    def receive_once(self):
        info = RXInfo()
        try:
            with self.sharedLock:
                self.pozyx.getRxInfo(info)
            recvTime = time.time()
        except StructError as s:
            print("RxInfo crashes! ", str(s))
        data = blankData(MSG_BYTE_SIZE)

        if info[1] == data.byte_size:
            with self.sharedLock:
                self.pozyx.readRXBufferData(data)
            #print("receive ", data.data)
            recvTimeMsg = UWBMessage(info[0], data, recvTime)
            return recvTimeMsg
        return False


    def decode(self ):

        pass


    def broadcast_msg(self, data):
        print("BroadCast", data)
        with self.sharedLock:
            self.pozyx.sendData(destination=0, data=data)
        pass

