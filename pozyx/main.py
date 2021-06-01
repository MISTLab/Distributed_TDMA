from multiprocessing import Process, Queue, Lock

import sys, os, time
from random import randint
from commMedium import commMedium
from pozyxTag import pozyxTag
from pozyxBD import pozyxBD

from pypozyx import (PozyxSerial, PozyxConstants, version, get_first_pozyx_serial_port, Data)
from pypozyx.definitions.registers import POZYX_NETWORK_ID
from parameters import uwbDic

if __name__ == "__main__":
    commMed = commMedium()
    pozyxLock = Lock()

    serial_port = get_first_pozyx_serial_port()
    if serial_port is None:
        print("No Pozyx connected. Check your USB cable or your driver!")
        quit()
    pozyx = PozyxSerial(serial_port)

    data = Data([0] * 2)
    pozyx.getRead(POZYX_NETWORK_ID, data)
    uwbID = int(hex(data[1] * 256 + data[0]),16)
    tagID = uwbDic[uwbID]
    print("Setup Done for UWB ", uwbID, tagID)

    curDir = os.path.dirname(os.path.abspath(__file__))
    filePath = curDir+'/log.txt'
    logfile = open(filePath , 'w')

    node = pozyxTag(pozyx, uwbID, tagID, commMed, pozyxLock, logfile)
    bdTask = pozyxBD(pozyx, tagID, commMed, pozyxLock, logfile)

    randomSleepTime = randint(0,500)/1000
    time.sleep(randomSleepTime)

    schProc = Process(target=bdTask.scheStart)
    schProc.start()
    try:
        while True:
            node.run()
    except(KeyboardInterrupt, SystemExit):
        schProc.terminate()
        logfile.close()
        exit




        