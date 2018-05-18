# __author__ = "Monowar Hasan"
# __email__ = "mhasan11@illinois.edu"
import random
import math
import HelperFunctions as HF
import Task as TF
import sys



def generate_taskset(n_tasks, util_grp):

    period_min = 10
    period_max = 100

    #util_grp = 7  # change from 0 to 8 to get different base-util (8 means = [0.8-0.9])
    base_util = random.uniform(0.02 + 0.1 * util_grp, 0.08 + 0.1 * util_grp)
    #print("- UTIL = " + str(base_util))

    period_list = [random.randint(period_min, period_max) for i in range(n_tasks)]
    util_list = HF.UUniFast(n_tasks, base_util)
    wcet_list = [math.ceil(ti * ui) for ti, ui in zip(period_list, util_list)]
    #util_list = [float('%.3f' % i) for i in util_list]

    '''
    new_wcet_list = []
    for wcet in wcet_list:
        if wcet == 0:
            new_wcet_list.append(1)
        else:
            new_wcet_list.append(wcet)
    wcet_list = new_wcet_list
    '''

    taskset = [TF.Task(wcet_list[i], period_list[i], util_list[i],
                       period_list[i], i + 1,
                       jitter=round(period_list[i] * 0)) for i in
               range(n_tasks)]

    return period_list, wcet_list, util_list, taskset


if __name__ == '__main__':

    n_tasks = 5
    n_task_each_tc = 11
    task_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    util_grp = int(sys.argv[1])

    if len(sys.argv) != 2:
        raise Exception("Use python TC_GEN_CY.py #util_grp_number (grp_number is from 0 to 8)")



    print("Generating Tasksets...")
    print("=========================")

    for n_tasks in task_list:

        cnt = 0
        loopcount = 0
        while cnt != n_task_each_tc:

            period_list, wcet_list, util_list, taskset = generate_taskset(n_tasks, util_grp)

            overall_util = 0
            for i in range(0,len(period_list)):
                overall_util += wcet_list[i]/period_list[i]

            if ((overall_util<util_grp*0.1) or (overall_util>=(util_grp+1)*0.1)):
                continue

            # if loopcount > 1000:
            #     break
            #
            # if not TF.check_edf_schedulability(taskset, HF.get_lcm(period_list)):
            #     print("Non EDF schedulable!, Try", loopcount)
            #     loopcount += 1
            #     continue
            # else:
            #     cnt += 1
            cnt += 1
            print("Number of Tasks", n_tasks)
            print("Total Utilizations:", overall_util)
            print("Periods:", period_list)
            print("WCETS:", wcet_list)
            print("Utilizations:", util_list)
            print("=========================")

    print("Script Finished!")