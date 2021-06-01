from ctypes import c_uint32 as uint32
from pypozyx import Data
from parameters import  MSG_BYTE_SIZE
from collections import deque
from typing import Union


def blankData(ByteSize):
    byteStr = "B"*ByteSize
    dataForm = [0] * ByteSize
    return Data(dataForm, byteStr)


class decodedTDMAData:
    def __init__(self,sendTimeNanoSecFromStart = 0, dataSenderId = 0, neibs = set([]), neibCandSlots = set([]), neibSendSlots = set([]), neibNeibCandSlots = set([]), neibNeibSendSlots = set([]), msgCode = 0):
        self.sendTimeNanoSecFromStart = sendTimeNanoSecFromStart
        self.dataSenderId = dataSenderId
        self.neibs = neibs
        self.neibCandSlots = neibCandSlots
        self.neibSendSlots = neibSendSlots
        self.neibNeibCandSlots = neibNeibCandSlots
        self.neibNeibSendSlots = neibNeibSendSlots
        self.msgCode = msgCode


class decodedRangingData:
    def __init__(self, sender_id, ):
        self.sender_id = sender_id

class UWBMessage(object):
    def __init__(self, sender_id = 0, data = 0, timestamp = 0, curFrameTime = 0):
        self.uwb_id = sender_id
        self.data = data
        self.timestamp = timestamp
        self.msgAge = 0
        self.curFrameTime = curFrameTime

    def __eq__(self, other):
        return self.uwb_id == other.uwb_id and self.data == other.data 
        
    def decode(self):
        pass

    def encode(self):
        pass

