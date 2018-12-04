import subprocess

subprocess.Popen("sudo ./mix 10 1 100 1 > console_black_hole", shell=True)

psLines = subprocess.Popen('ps -e -T | grep mix', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
for line in psLines.stdout.readlines():
    if 'grep' in line:
        continue

    lineSplits = line.strip().split(' ')
    pid = lineSplits[2]
    print "Killing " + pid + "..."
    subprocess.Popen("sudo kill -9 " + pid, shell=True)
    #retval = p.wait()