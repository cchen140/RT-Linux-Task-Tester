__author__ = "Monowar Hasan"
__email__ = "mhasan11@illinois.edu"

import random
import math

from Config import *


class Task:
    def __init__(self, wcet, period, util, deadline, tid, jitter=0):
        self.wcet = wcet
        self.period = period
        self.util = util
        self.deadline = deadline
        self.jitter = jitter
        self.wcrt = -1  # will be updated later
        self.inv_budget = -1  # will be updated later
        self.tid = tid
        self.name = "Task" + str(tid)


class Job:
    def __init__(self, arrival_time, wcet, absolute_deadline, name, wcrt=-1, inv_budget=None):
        self.arrival_time = arrival_time
        self.wcet = wcet
        self.usage = 0
        self.absolute_deadline = absolute_deadline
        self.inv_budget=inv_budget
        self.remaining_budget=self.inv_budget
        self.wcrt = wcrt
        self.name = name


def get_task_dbf(task, time):
    """ Returns the DBF of a task """
    dbf = (math.floor((time - task.deadline)/task.period) + 1) * task.wcet
    dbf = max(0, dbf)
    return dbf


def get_taskset_dbf(taskset, time):
    """ Returns the DBF of a taskset """

    dbf = 0

    for task in taskset:
        dbf += get_task_dbf(task, time)

    return dbf


def get_edf_sched_test_upperbound(taskset, hyperperiod):

    Dmax = -1  # maximum deadline of a taskset
    total_util = 0

    t2 = 0  # get 2nd term in euqation
    for task in taskset:
        total_util += task.util
        t2 += task.util * max(0, task.period - task.deadline)
        if Dmax < task.deadline:
            Dmax = task.deadline

    t2 = (1/(1-total_util)) * t2

    upper_bound = min(hyperperiod, max(Dmax, t2))

    return upper_bound


def check_edf_schedulability(taskset, hyperperiod):

    upper_bound = get_edf_sched_test_upperbound(taskset, hyperperiod)
    upper_bound = int(math.ceil(upper_bound))

    for t in range(1, upper_bound+1):
        taskset_dbf = get_taskset_dbf(taskset, t)
        if taskset_dbf > t:
            print("### Taskset is not Schedulable by EDF! ###")
            return False

    return True


def get_W(t, taskset):
    "W(t) is the cumulative workload at time t, see the paper or EDF book"
    n = len(taskset) # number of tasks

    w = 0
    for task in taskset:
        w = w + math.ceil(t/task.period) * task.wcet

    return w


def calculate_maximum_workload(taskset):
    """
    This function calculate the maximum workload L
    defined in the following paper (Eq. 1)
    'Analysis of Deadline Scheduled Real-Time Systems'
    """

    L = 0
    for task in taskset:
        L = L + task.wcet

    cnt = 1
    while 1:
        Lnew = get_W(L, taskset)

        if Lnew == L:
            break

        L = Lnew
        cnt = cnt + 1

        if cnt > PARAMS.MAX_ITER:
            raise ValueError("Unable to calculate maximum workload!")

    return L


def get_interference(arrival, task, taskset):
    """
    Calculate the interference from higher priority workload for a
    given arrival
    """
    intf = 0

    for tsk in taskset:

        if (tsk.name != task.name) and (tsk.deadline <= arrival + task.deadline):
            term1 = math.ceil(task.deadline/tsk.period) + 1
            term2 = math.floor((arrival + task.deadline - tsk.deadline)/tsk.period) + 2
            temp = min(term1, term2) * tsk.wcet

            intf = intf + temp

    return intf


def calculate_wcrt_by_arrival(arrival, task, taskset):
    """
    Calculate the WCRT for a given arrival
    """

    wi = ( math.floor(arrival/task.period) + 1 ) * task.wcet + get_interference(arrival, task, taskset)

    wcrt = max(task.wcet, wi - arrival)

    return wcrt


def calculate_wcrt(task, taskset, max_workload):

    max_wcrt = 0
    for arrival in range(max_workload-task.wcet):
        wcrt = calculate_wcrt_by_arrival(arrival, task, taskset)
        # print("Task Name:", task.name, "Arrival:", arrival, "WCRT(a):", wcrt)
        if wcrt >= max_wcrt:
            max_wcrt = wcrt

    return max_wcrt


def check_edf_utilization_schedulability(taskset):
    """ Check whether the taskset is EDF-schedulable (Total Utilization <= 1, Di=Pi) """

    util = [task.wcet/task.period for task in taskset]

    if sum(util) <= 1:
        return True

    print("Taskset utilization: ", sum(util) )
    return False

