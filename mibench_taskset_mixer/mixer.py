import optparse
import math
import random

class Taskset:
    periods = []
    wcets = []
    utils = []
    totalUtil = 0

'''
max is included in the random number.
'''
def getRadNumList(max, count):
    radIntList = []
    for i in xrange(count):
        radIntList.append(random.randint(0, max))
    return radIntList

if __name__ == '__main__':
    parser = optparse.OptionParser()

    parser.add_option('-t', '--tasksets',
                      action="store", dest="tasksetFile", default="../sample_tasksets/out1.txt",
                      help="the path of a file containing tasksets")
    parser.add_option('-m', '--mibench',
                      action="store", dest="mibenchCmdFile", default="mibench_cmds.txt",
                      help="the path of a file containing mibench commands")
    parser.add_option('-o', '--out',
                      action="store", dest="outFile", default="out1.txt",
                      help="the path of a file containing tasksets")
    parser.add_option('-r', '--ratio',
                      action="store", dest="mibenchRatio", default="0.5",
                      help="what ratio of tasks in a taskset should be replaced with mibench tasks")

    options, args = parser.parse_args()
    print 'File Path:', options.tasksetFile

    mibenchCmdList = []
    mibenchCmdCtimeList = []
    with open(options.mibenchCmdFile, "r") as lines:
        firstLine = True
        for line in lines:
            if firstLine:
                mibenchCommonCmd = line.replace('\n', '')
                firstLine = False
                continue

            if line.strip() == "":
                continue

            if line.strip()[0] == '#':
                continue

            mibenchCmd = mibenchCommonCmd + ";" + line.split('@')[0].strip()
            cTime = int(line.split('@')[1])

            mibenchCmdList.append(mibenchCmd)
            mibenchCmdCtimeList.append(int(cTime*1.2))

        print str(len(mibenchCmdList)) + " mibench commands are added."


    tasksetList = []
    with open(options.tasksetFile, "r") as lines:
        for line in lines:
            lineSplits = line.split(':')
            lineTitle = lineSplits[0]
            if len(lineSplits) > 1:
                lineContent = lineSplits[1].replace('\n', '')
            else:
                continue

            if "Total Utilizations" in lineTitle:
                thisTaskSet = Taskset()
                thisTaskSet.totalUtil = float(lineContent)
                tasksetList.append(thisTaskSet)
                continue
            elif "Periods" in lineTitle:
                thisTaskSet.periods = lineContent.replace('[', '').replace(']', '').replace(' ', '').split(',')
                continue
            elif "WCETS" in lineTitle:
                thisTaskSet.wcets = lineContent.replace('[', '').replace(']', '').replace(' ', '').split(',')
                continue
            elif "Utilizations" in lineTitle:
                thisTaskSet.utils = lineContent.replace('[', '').replace(']', '').replace(' ', '').split(',')
                continue
            else:
                continue

    print str(len(tasksetList)) + " tasksets are added."
    tasksetOutStrList = []
    for taskset in tasksetList:
        numOfTasks = len(taskset.periods)
        numOfMibenchTasks = int(math.ceil(numOfTasks * float(options.mibenchRatio)))
        #radMibenchIndexList = getRadNumList(len(mibenchCmdList)-1, numOfMibenchTasks)
        radMibenchIndexList = [0]*numOfMibenchTasks

        tasksetOutStr = str(numOfTasks)
        '''Periods'''
        for i in xrange(numOfTasks-numOfMibenchTasks):
            tasksetOutStr += " " + taskset.periods[i].strip()
        shouldUseLastTaskset = False
        for i in xrange(numOfMibenchTasks):
            validMibenchTaskIsFound =False
            for j in xrange(10):
                radMibenchIndexList[i] = random.randint(0, len(mibenchCmdList)-1)
                thisMiBenchTaskPeriod = int( mibenchCmdCtimeList[radMibenchIndexList[i]] / float(taskset.utils[i+(numOfTasks-numOfMibenchTasks)]) )
                if thisMiBenchTaskPeriod < 5000:  # 5 second
                    validMibenchTaskIsFound = True
                    break
                else:
                    # Let's try again
                    continue
            if validMibenchTaskIsFound == True:
                tasksetOutStr += " " + str(thisMiBenchTaskPeriod)
            else:
                shouldUseLastTaskset = True
                break
        if shouldUseLastTaskset == True:
            tasksetOutStrList.append(tasksetOutStrList[-1])
            continue # Skip generating this taskset and move to generating the next one

        '''Wcets'''
        for i in xrange(numOfTasks-numOfMibenchTasks):
            tasksetOutStr += " " + taskset.wcets[i].strip()
        for i in xrange(numOfMibenchTasks):
            tasksetOutStr += " " + str(mibenchCmdCtimeList[radMibenchIndexList[i]])
        '''Mibench Commands'''
        for i in xrange(numOfMibenchTasks):
            tasksetOutStr += " \"" + mibenchCmdList[radMibenchIndexList[i]] + "\""

        tasksetOutStrList.append(tasksetOutStr)

    outFile = open(options.outFile, "w")
    for tasksetOutStr in tasksetOutStrList:
        outFile.write(tasksetOutStr + "\n")
