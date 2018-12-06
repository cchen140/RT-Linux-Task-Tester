import sys
import numpy


DEFAULT_LOG_FOLDER_PATH = "log"
SUB_LOG_FOLDER_NAME = "log{}"
SUMMARY_FILE_NAME = "summary.txt"
OUTPUT_FILE_NAME = "post_summary.txt"

if __name__ == '__main__':
    if len(sys.argv) > 1:
        logFolderPath = sys.argv[1]
    else:
        logFolderPath = DEFAULT_LOG_FOLDER_PATH

    rawMeanCostListByNumOfTasks = [[] for i in xrange(11)] # 0 is not used.
    for i in xrange(1,9):
        summaryFilePath = logFolderPath + "/" + SUB_LOG_FOLDER_NAME.format(i) + "/" + SUMMARY_FILE_NAME
        with open(summaryFilePath, "r") as lines:
            for line in lines:
                numOfTasks = int(line.split(":")[1])
                thisMeanCost = int(line.split("mean:")[1].split(",")[0])
                if thisMeanCost < 0:
                    continue
                rawMeanCostListByNumOfTasks[numOfTasks].append(thisMeanCost)

    outputFile = open(logFolderPath + "/" + OUTPUT_FILE_NAME, "w")
    meanMeanCostList = [0]*11 # 0 is unused.
    meanMeanCostStderrorList = [0]*11 # 0 is unused
    for i in xrange(1, 11):
        meanMeanCostList[i] = sum(rawMeanCostListByNumOfTasks[i])/len(rawMeanCostListByNumOfTasks[i])
        meanMeanCostStderrorList[i] = numpy.std(rawMeanCostListByNumOfTasks[i])/(len(rawMeanCostListByNumOfTasks[i])**0.5)
        outputString = "{}, {}\n".format(meanMeanCostList[i], meanMeanCostStderrorList[i])
        outputFile.write(outputString)
        print str(i) + ":" + outputString[:-1] # -1 is to remove "\n"
