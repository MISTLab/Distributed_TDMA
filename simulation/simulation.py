
from simEnv import simEnv
import pickle
import copy

if __name__ == "__main__":
    newSim = 1
    simSteps = 20
    sense = None
    arenaSize = 50
    if newSim:
        numNodes = 100 # same as slots size
        scene = simEnv(numNodes)
        #scene.setupCustomize()
        scene.setupRandom(arenaSize)
    else:
        scene = pickle.load(open("simEnv.p", "rb")) 
        scene.clear()


    scene.updateNeib()
    scene.commStep()
    scene.initialStep()
    scene.draw(0)
    totalCand = 0
    totalSend = 0
    for step in range(1,simSteps):
        totalCand = 0
        totalSend = 0
        scene.commStep()
        #scene.draw(step)
        #scene.drawBrifSend(step)
        #scene.drawBrifCand(step)
        curSit = copy.deepcopy(scene.nodesList)
        for i in range(scene.numNodes):
            scene.nodesList[i].tdmaManager.iterativeSteps(curSit[i].tdmaManager.neibsInfo)
            totalCand += len(scene.nodesList[i].tdmaManager.candSlots)
            totalSend += len(scene.nodesList[i].tdmaManager.sendSlots)
            #scene.nodesList[i].tdmaManager.slotUsageCorrect()
        scene.collisionCheck()
        #scene.motionStep()
        scene.updateNeib()
        scene.neibChangingActions()

        print("Nodes num: ", scene.numNodes, " Area size:", arenaSize, "Step ", step, "sendSlots: ", totalSend, " avg ", totalSend/scene.numNodes , " candSlots: ", totalCand, " avg ", totalCand/scene.numNodes)


    pickle.dump(scene, open("simEnv.p", "wb"))



