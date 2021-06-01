from enum import IntEnum

uwbDic = {8193:1, 8200:2, 8201:3, 8214:4, 8225:5, 8197:6, 8228:7, 8212:8 , 8224:9, 8208:10, 8198:11, 8194:12, 8216:13, 8240:14, 8215:15}


NUM_NODES = 30
NUM_SLOTS = 2*NUM_NODES
SLOT_SIZE = 0.05
CLOCK_DIFF_THRESHOLD = int(0.02*1e9) # in nano second
RESCHEDULE_TIME = 0.0024 # in second
MSG_BYTE_SIZE = 80

TDMA_MSG_CODE = 1
TDMA_SLOT_RELEASE_CODE = 2
RANGING_MSG_CODE = 3
NEIB_AGE_BUF = 3 # If not received in 3 super frame, it will removed from neighbourhood.

