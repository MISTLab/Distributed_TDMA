from parameters import NUM_NODES, NUM_SLOTS


def valueFrom4Byte(bytes):
    v = bytes[0]
    for i in range(1,4):
        v = v<<8
        v|=bytes[i]
    return v

def valueTo4Byte(value):
    bytes = [-1]*4
    MASK = (1<<8)-1
    for i in range(4):
        bytes[3-i] = value & MASK
        value = value>>8
    return bytes

def rangeAgeTo3Byte(rangeMeas, age): # 14bit for rangeMeas measurement, limit to 16383cm (change unit to cm to transmit); 10 bit for age, limit to  1023()
    rangeMeas = round(rangeMeas/10)
    if rangeMeas > 16383:
        rangeMeas = 16383
    if age >1023:
        age = 1023

    bytes = [-1]*3
    bytes[0] = rangeMeas>>6
    bytes[1] = ((rangeMeas&((1<<6)-1))<<2 )+(age>>8)
    #bytes[1] = ((rangeMeas)&((1<<6)-1))<<2 
    bytes[2] = age&((1<<8)-1)

    return bytes

def rangeAgeFrom3Byte(bytes):
    rangeMeas = ((bytes[0]<<8)+bytes[1]>>2)*10
    age = (bytes[1]&(1<<2)-1)*256 + bytes[2]
    return [rangeMeas, age]


def setToBytes(set):
    bytesList = [0]*(int(NUM_NODES/8)+1)
    for i in set:
        if i < NUM_NODES:
            byteIdx = int(i/8)
            bitIdx = int(i%8)
            bytesList[byteIdx] = bytesList[byteIdx] | (1<<bitIdx)
        else:
            print(i ," is bigger than NUM_NODES, droped")
    return bytesList

def setFromBytes(bytesList):
    setv = set([])
    for i in range(len(bytesList)):
        for j in range(8):
            bitID = i*8+j
            if(bitID < NUM_NODES and 1&(bytesList[i]>>j)):
                setv.add(bitID)
    return setv



if __name__ == "__main__":

    a = set([1,2,3,21, 22, 18, 19, 20])
    c = setToBytes(a)
    d = setFromBytes(c)
    print(a,c,d)
    pass