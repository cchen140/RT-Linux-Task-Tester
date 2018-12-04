import sys
import os
import time
import subprocess


def run_single_mix(tasksetId, logOutPath, duration, taskParams):

    if not os.path.exists('log'):
        os.makedirs('log')

    if not os.path.exists(logOutPath):
        os.makedirs(logOutPath)
    logFile = open("{}/{}.txt".format(logOutPath, tasksetId), "w")

    # extractLogOutPath = logOutPath + "/extracts"
    # if not os.path.exists(extractLogOutPath):
    #     os.makedirs(extractLogOutPath)
    # extractLogFile = open(extractLogOutPath + "/" + logId + ".txt", "w")

    # Clear dmesg
    subprocess.Popen("sudo dmesg -c > console_black_hole", shell=True)

    completeCommand = "sudo ./mix {} {} > console_black_hole".format(duration, taskParams)
    subprocess.Popen(completeCommand, shell=True)
    #subprocess.Popen("sudo ./mix 10 1 100 1 > console_black_hole", shell=True)

    time.sleep(duration)

    # Kill all test threads.
    psLines = subprocess.Popen('ps -e -T | grep mix', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in psLines.stdout.readlines():
        if 'grep' in line:
            continue

        lineSplits = line.strip().split(' ')
        pid = lineSplits[2]
        #print "Killing " + pid + "..."
        subprocess.Popen("sudo kill -9 " + pid, shell=True)
        #retval = p.wait()

    contextSwitchCount = int(subprocess.Popen('dmesg | grep -c context', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.readlines()[0])
    totalPickCount = int(subprocess.Popen('dmesg | grep -c picked', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.readlines()[0])
    budgetCount = int(subprocess.Popen('dmesg | grep -c budget', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.readlines()[0])
    randomPickCount = int(subprocess.Popen('dmesg | grep -c -e "(rad)" -e "(idle)"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.readlines()[0])

    if totalPickCount == 0:
        radRatio = 0
    else:
        radRatio = float(randomPickCount) / totalPickCount

    # Extract context switch cost values and compute their average
    costList = []
    costSum = 0
    #costCount = 0
    dmesgLines = subprocess.Popen('dmesg', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    dmesgLineCount = 0
    for line in dmesgLines.stdout.readlines():
        dmesgLineCount += 1
        if 'picked' in line:
            cost = int(line.strip().split('.')[-1])
            costSum += cost
            costList.append(cost)

    if len(costList) > 1:
        averageCost = costSum/len(costList)

        # Compute standard deviation of the context switch cost
        stdevSum = 0
        for thisCost in costList:
            stdevSum += (thisCost-averageCost)**2

        stdev = (stdevSum/(len(costList)-1))**0.5
        
        # Compute standard error
        stderror = stdev/(len(costList)**0.5)
    else:
        averageCost = 0
        stdev = 0
        stderror = 0

    summaryString = "pick:{}, rad:{}, radratio:{}, mean:{}, stdev:{}, sem:{}".format(totalPickCount, randomPickCount, radRatio, averageCost, stdev, stderror)
    logFile.write(completeCommand + '\n')
    logFile.write(summaryString + '\n')

    subprocess.Popen("dmesg >> {}/{}.txt".format(logOutPath, tasksetId), shell=True)

    if dmesgLineCount > 2:
        print summaryString
        return summaryString
    else:
        print "Test error occurs for {}".format(tasksetId)
        return "Test error occurs for {}".format(tasksetId)



if __name__ == '__main__':
    logId = sys.argv[1]
    duration = sys.argv[2]
    taskParams = sys.argv[3]
    if len(sys.argv) >= 5:
        logOutPath = sys.argv[4]
    else:
        logOutPath = "log/log"

    run_single_mix(logId, logOutPath, int(duration), taskParams)

