import re
from matplotlib import pyplot as plt
import numpy as np
import sys, os

#sys.path.append('../src/interfaces')
#sys.path.append(os.path.join(os.path.dirname(os.path.dirname(sys.path[0])),'src', 'interfaces'))
testingDir = os.path.dirname((os.path.abspath(__file__)))



extractInfo = re.compile('Nodes num:  (\d*)  AS: (\d*) Step  (\d*) ; sS:  (\d*)  avg  (\d*.\d*) ; cS:  (\d*)  avg  (\d*.\d*) ; tC  (\d*)  avg  (\d*.\d*) ; avgNs:  (\d*.\d*) ; Done: (\d*)')

#testDict = {10:0, 100:1, 1000:2, 2000:3}
#testDict = {10:0, 100:1, 1000:2}
testDict = {100:0}


class rawdata():
    def __init__(self,sourceFile):
        self.sourceFile = sourceFile
        self.totalSendSlots = []
        self.totalCandSlots = []
        self.avgNeib = []
        for i in range(len(testDict)):
            self.totalCandSlots.append([])
            self.totalSendSlots.append([1])
            self.avgNeib.append(0)

    def extractData(self):
        with open(self.sourceFile) as f:
            content = f.readlines()
        content = [x.strip() for x in content]

        for ele in content:
            if(extractInfo.search(ele)):
                results = extractInfo.search(ele)
                idx = testDict[int(results[1])]
                # for i in range(len(results.groups())):
                #     print(results[i])
                self.totalSendSlots[idx].append(float(results[5]))
                self.totalCandSlots[idx].append(float(results[7]))
                if self.avgNeib[idx] == 0:
                    self.avgNeib[idx] = 1
                #print(len(results.groups()))


            #print(self.data)


    def draw(self):
        fig = plt.figure()
        #fig = plt.figure(figsize=(5,7))
        ax = fig.add_subplot(1, 1, 1)
        for i in testDict:
            idx = testDict[i]
            plt.plot(self.totalCandSlots[idx], label = 'Avg candidate slots - '+str(i)+' nodes')
            plt.plot(self.totalSendSlots[idx], label = 'Avg send slots - '+str(i)+' nodes')
        ax.set_xlabel("Frame iterations")
        ax.set_ylabel("Slots number")
        plt.legend()
        plt.savefig('result.pdf')
        # ax.grid(linewidth=0.2)
        # plt.grid(False)

        # idx = 0
        # legendID = []
        # for ele in self.spaticalSlots:
        #     if realtime:
        #         curTime = self.timeOffset[idx]
        #     else: 
        #         curTime = self.stepCount[idx]
        #     for i in range(len(ele)):
        #         nodeID = ele[i]
        #         if nodeID!=0:
        #             if nodeID in legendID:
        #                 plt.scatter(i, curTime, marker="_", c=color[ele[i]],s=20)
        #             else:
        #                 plt.scatter(i, curTime, marker="_", c=color[ele[i]],s=20, label=nodeID )
        #                 legendID.append(nodeID)

        #     if curTime in self.collisionsDict:
        #         offset = [0.1]*NUM_SLOTS
        #         for ele in self.collisionsDict[curTime]:
        #             plt.scatter(ele[0]+offset[ele[0]], curTime, marker=".", c=color[ele[1]],s=5)
        #             offset[ele[0]] = offset[ele[0]] + 0.1


        #     idx += 1

        pass


    def drawExp(self):
        self.extractData()
        self.draw()
        pass



if __name__ == '__main__':
    print(testingDir)
    filename = testingDir+'/result.txt'
    work = rawdata(filename)
    work.drawExp()