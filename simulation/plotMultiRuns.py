import re
from matplotlib import pyplot as plt
import numpy as np
import sys, os

#sys.path.append('../src/interfaces')
#sys.path.append(os.path.join(os.path.dirname(os.path.dirname(sys.path[0])),'src', 'interfaces'))
testingDir = os.path.dirname((os.path.abspath(__file__)))



extractInfo = re.compile('Nodes num:  (\d*)  AS: (\d*) Step  (\d*) ; sS:  (\d*)  avg  (\d*.\d*) ; cS:  (\d*)  avg  (\d*.\d*) ; tC  (\d*)  avg  (\d*.\d*) ; avgNs:  (\d*.\d*) ; Done: (\d*)')

extractRunTime = re.compile('Welcome (\d*) times')

#testDict = {10:0, 100:1, 1000:2, 2000:3}
#testDict = {10:0, 100:1, 1000:2}
testDict = {100:0}


class rawdata():
    def __init__(self,sourceFile):
        self.sourceFile = sourceFile
        self.totalSendSlots = []
        self.totalCandSlots = []
        self.avgConvergeRun = []
        self.avgConvergeSendslot = []
        self.avgNeib = []
        self.multiRun = []
        self.idSeq = []

    def extractData(self):
        with open(self.sourceFile) as f:
            content = f.readlines()
        content = [x.strip() for x in content]

        sendSlots = []
        candSlots = []
        curNodeNum = 0
        avgNeib = []
        neibSize = 0
        idx = -1
        for ele in content:
            if(extractInfo.search(ele)):
                results = extractInfo.search(ele)
                # for i in range(len(results.groups())):
                #     print(results[i])
                curNodeNum = int(results[1])
                sendSlots.append(float(results[5]))
                candSlots.append(float(results[7]))
                neibSize = float(results[10])

                #print(len(results.groups()))
            elif (extractRunTime.search(ele)):

                results = extractRunTime.search(ele)
                curRun = float(results[1])
                if curRun>1:
                    self.totalCandSlots[idx].append(candSlots)
                    self.totalSendSlots[idx].append(sendSlots)
                    self.idSeq[idx] = curNodeNum
                    sendSlots = []
                    candSlots = []
                    avgNeib.append(neibSize)
                else: # Add new node
                    self.totalCandSlots.append([])
                    self.totalSendSlots.append([])
                    self.idSeq.append(0)
                    sendSlots = []
                    candSlots = []
                    idx += 1
                    print(np.mean(avgNeib))
                    avgNeib = []
        print(np.mean(avgNeib))


    def drawAvg(self):

        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)

        allMeanRuns = []
        allMeanSend = []
        allStdRuns = []
        allStdSend = []
        allId = []

        for i in range(len(self.idSeq)):
            self.avgConvergeRun.append([])
            self.avgConvergeSendslot.append([])
            lastCand = 10
            doneRun = 0
            for run in range(len(self.totalCandSlots[i])):
                for cand in range(len(self.totalCandSlots[i][run])):
                    if lastCand ==0 and self.totalCandSlots[i][run][cand] == 0:
                        doneRun = cand - 1 
                        if doneRun == 0:
                            doneRun = 1
                        self.avgConvergeRun[i].append(doneRun)
                        self.avgConvergeSendslot[i].append(self.totalSendSlots[i][run][cand])
                        doneRun = 0
                        lastCand = 10

                        break
                    else:
                        lastCand = self.totalCandSlots[i][run][cand]

                    pass

            meanRun = np.mean(self.avgConvergeRun[i])
            stdRun = np.std(self.avgConvergeRun[i])
            meanSend = np.mean(self.avgConvergeSendslot[i])
            stdSend = np.std(self.avgConvergeSendslot[i])

            allMeanRuns.append(meanRun)
            allMeanSend.append(meanSend)
            allStdRuns.append(stdRun)
            allStdSend.append(stdSend)
            allId.append(self.idSeq[i])
            print(meanRun, stdRun, meanSend, stdSend)
            
            # ax.errorbar( self.idSeq[i], meanRun, yerr=stdRun, fmt='s',markersize=8, label = 'Runs-'+str(self.idSeq[i])+' nodes ' ,linestyle=ls)
            # ax.errorbar( self.idSeq[i], meanSend, yerr=stdSend, fmt='s',markersize=8, label = 'sendSlots-'+str(self.idSeq[i])+' nodes ' )
        ls = 'dotted'
        ax.errorbar( allId, allMeanRuns, yerr=allStdRuns, fmt='s',markersize=8, label = 'Frames' ,linestyle=ls)
        ax.errorbar( allId, allMeanSend, yerr=allStdSend, fmt='s',markersize=8, label = 'Send slots' ,linestyle=ls)
        plt.legend(loc='upper left')
        ax.set_xlabel("Number of nodes")
        ax.set_ylabel("Number of Frames/Slots")
        ax.semilogx()
        #ax.xaxis.set_ticks_position('none') 
        plt.savefig('result_multirun.pdf')


    def draw(self):
        fig = plt.figure()
        #fig = plt.figure(figsize=(5,7))
        ax = fig.add_subplot(1, 1, 1)
        for i in range(len(self.idSeq)):
            idx = self.idSeq[i]
            plt.plot(self.totalCandSlots[i][0], label = 'Avg candSlots-'+str(idx))
            plt.plot(self.totalSendSlots[i][0], label = 'Avg sendSlots-'+str(idx))
        ax.set_xlabel("Frame iterations")
        ax.set_ylabel("Slots number")
        plt.legend()    
        plt.savefig('result.svg')
        pass


    def drawExp(self):
        self.extractData()
        #self.draw()
        self.drawAvg()
        pass



if __name__ == '__main__':
    print(testingDir)
    filename = testingDir+'/multitimesRun.txt'
    work = rawdata(filename)
    work.drawExp()