from multiprocessing import Value, Array, Queue
from parameters import NUM_NODES



class commMedium:
    def __init__(self, actionCount = Value('i', 0), timeToSleep = Value('i', 0), restartProposalFlag = Value('i', 0), neibArray = Array('i', NUM_NODES), candSlots = Array('i', NUM_NODES),  sendSlots = Array('i', NUM_NODES), neibRanging = Array('i', NUM_NODES), rangingAge = Array('i', NUM_NODES), frameStartTime = Value('d', 0), realeaseSlots  = Value('i', 0)):
        self.actionCount = actionCount
        self.timeToSleep = timeToSleep
        self.restartProposalFlag = restartProposalFlag
        self.neibArray = neibArray
        self.candSlots = candSlots
        self.sendSlots = sendSlots
        self.frameStartTime = frameStartTime
        self.reTransmitMsg = Queue() #Queue(NUM_NODES*NUM_NODES)
        self.neibRanging = neibRanging
        self.rangingAge = rangingAge
        self.realeaseSlots = realeaseSlots



