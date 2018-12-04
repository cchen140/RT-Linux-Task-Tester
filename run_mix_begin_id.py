import os
import sys
from run_single_mix import run_single_mix

def run_mix_begin_id(logId, duration, beginId, mixCmdFilePath):
    outLogFolderPath = "log/log{}".format(logId)
    if not os.path.exists(outLogFolderPath):
        os.makedirs(outLogFolderPath)

    summaryFile = open(outLogFolderPath + "/summary.txt", "a")

    tasksetIndex = 0
    with open(mixCmdFilePath, "r") as lines:
        for line in lines:
            tasksetIndex += 1
            if tasksetIndex < int(beginId):
                continue

            print "### Taskset {}".format(tasksetIndex)
            result = run_single_mix(tasksetIndex, outLogFolderPath, duration, line.replace('\n', ''))
            if "rror" in result:
                print result
                exit(0)
            else:
                summaryFile.write(str(tasksetIndex) + ": " + result + "\n")
                summaryFile.flush()
		print result

if __name__ == '__main__':
    duration = sys.argv[1]
    beginId = sys.argv[2]
    mixCmdFilePath = sys.argv[3]
    logId = sys.argv[4]
    run_mix_begin_id(logId, int(duration), int(beginId), mixCmdFilePath)
