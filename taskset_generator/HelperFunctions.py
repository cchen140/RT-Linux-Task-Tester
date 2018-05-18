import random
import math
from functools import reduce  # Reruired for Python 3 to calculate LCM
from collections import defaultdict
import itertools
import Task as TF
from Config import *
#import dill  # pickle will fail if we remove this line
#import pickle
import gzip
# import scipy.spatial.distance as scidist
#import distance
import copy


def UUniFast(n, U):
    """ Classic UUniFast algorithm """
    sumU = U  # sum of n uniform random variables
    vectU = []
    for i in range(1, n):  # iterate over i to n-1
        nextSumU = sumU * random.random() ** (1.0 / (n - i))  # the sum of n-i uniform random variables
        vectU.append(sumU - nextSumU)
        sumU = nextSumU
    vectU.append(sumU)

    return vectU


# http://stackoverflow.com/questions/171765/what-is-the-best-way-to-get-all-the-divisors-of-a-number
# returns all the divisor of the number n
def divisorGenerator(n):
    large_divisors = []
    for i in range(1, int(math.sqrt(n) + 1)):
        if n % i == 0:
            yield i
            if i * i != n:
                large_divisors.append(n / i)
    for divisor in reversed(large_divisors):
        yield divisor


# LCM calculator
def lcm(a, b):
    if a > b:
        greater = a
    else:
        greater = b

    while True:
        if greater % a == 0 and greater % b == 0:
            lcm = greater
            break
        greater += 1

    return lcm


# returns LCM of a list
def get_lcm(lcm_list):
    return reduce(lambda x, y: lcm(x, y), lcm_list)


# get periods for n tasks
def get_periods(n):
    all_possible_periods = list(divisorGenerator(PARAMS.COMMON_HP))
    # print(all_possible_periods)
    all_possible_periods = [i for i in all_possible_periods if i >= PARAMS.PERIOD_MIN]
    # print(all_possible_periods)
    low_range = [i for i in all_possible_periods if i <= PARAMS.PERIOD_SPLITTER]
    high_range = [i for i in all_possible_periods if i > PARAMS.PERIOD_SPLITTER]

    # print(low_range)

    period_list = []

    hp = 0
    count = 0
    max_count = 1000
    while hp != PARAMS.COMMON_HP:

        tmp = random.sample(range(1, len(low_range)), math.floor(n / 4))  # get from low_range of periods

        # print(tmp)
        period_list = [low_range[tmp[i]] for i in range(0, len(tmp))]
        # print(period_list)

        tmp = random.sample(range(1, len(high_range)), n - math.floor(n / 4))  # get from high range
        # print("high range is:", high_range)
        # print(tmp)
        period_list.extend([high_range[tmp[i]] for i in range(0, len(tmp))])
        # print(period_list)

        # test whether generated period matches with common HP
        # print("count is: ", count)
        hp = get_lcm(period_list)
        count += 1
        if count >= max_count:
            raise Exception('Periods LCM are not matched with Commom HP')

    # print("Hyperperiod of selected periods is: ", hp, ", Got in Try # ", count)

    # raise an excepion if the period's LCM is not the Common HP
    if hp != PARAMS.COMMON_HP:
        raise Exception('Periods LCM are not matched with Commom HP')

    period_list = list(map(int, period_list))  # make it to integer (optional)
    return period_list


# get periods for n tasks
def get_periods_v2(n):
    period_list = list(divisorGenerator(PARAMS.COMMON_HP))
    period_list = [i for i in period_list if i >= PARAMS.PERIOD_MIN]

    app_len = len(period_list)

    hp = get_lcm(period_list)
    if hp != PARAMS.COMMON_HP or n < app_len:
        print("Hyperperiod/number of Task is NOT compatible. Need to Fix this: get_periods_v2(), HelperFunctions.py!")
        exit(1)
        # raise Exception("Periods are not compatible with Hyperperiod Value. Need to Fixed this routine")

    if app_len == n and hp == PARAMS.COMMON_HP:
        return period_list
    else:
        diff = n - app_len
        for i in range(diff):
            indx = random.randint(0, app_len-1)
            val = copy.deepcopy(period_list[indx])
            period_list.append(val)

    return period_list


# get periods for n tasks
def get_periods_v3(n):

    period_list = list(divisorGenerator(PARAMS.COMMON_HP))
    period_list = [i for i in period_list if i >= PARAMS.PERIOD_MIN]

    app_len = len(period_list)

    hp = get_lcm(period_list)
    if hp != PARAMS.COMMON_HP:
        print("Hyperperiod/number of Task is NOT compatible. Need to Fix this: get_periods_v3(), HelperFunctions.py!")
        exit(1)
        # raise Exception("Periods are not compatible with Hyperperiod Value. Need to Fixed this routine")

    if app_len == n and hp == PARAMS.COMMON_HP:
        return period_list

    elif n < app_len:
        plist = list(itertools.combinations(period_list, n))
        plist = [list(elem) for elem in plist]  # change tuple to list

        random.shuffle(plist)  # just randomized the list to get different combination

        found = False
        for periods in plist:
            plcm = get_lcm(periods)
            if plcm == PARAMS.COMMON_HP:
                period_list = copy.deepcopy(periods)
                found = True
                break

        if found:
            return period_list
        else:
            print("Hyperperiod/number of Task is NOT compatible. Need to Fix this: get_periods_v2(), HelperFunctions.py!")
            exit(1)

    elif n > app_len:
        diff = n - app_len
        for i in range(diff):
            indx = random.randint(0, app_len-1)
            val = copy.deepcopy(period_list[indx])
            period_list.append(val)

        return period_list

    # some error checking
    if len(period_list) != n:
        print("Hyperperiod/number of Task is NOT compatible. Need to Fix this: get_periods_v2(), HelperFunctions.py!")
        exit(1)


# get periods for n tasks
def get_periods_entropy(n):

    # period_list = copy.deepcopy(PARAMS.PERIOD_LIST_ENTOPY)
    plist = list(itertools.combinations(PARAMS.PERIOD_LIST_ENTOPY, n))
    plist = [list(elem) for elem in plist]  # change tuple to list

    random.shuffle(plist)  # just randomized the list to get different combination

    found = False
    for periods in plist:
        plcm = get_lcm(periods)
        if plcm == PARAMS.COMMON_HP_ENTROPY:
            period_list = copy.deepcopy(periods)
            found = True
            break

    if found:
        return period_list
    else:
        print("Hyperperiod/number of Task is NOT compatible. Need to Fix this: get_periods_entropy(), HelperFunctions.py!")
        exit(1)

    # some error checking
    if len(period_list) != n:
        print("Hyperperiod/number of Task is NOT compatible. Need to Fix this: get_periods_entropy(), HelperFunctions.py!")
        exit(1)




def get_period_by_range(n, pmin, pmax):
    plist = []

    for i in range(n):
        plist.append(random.randint(pmin, pmax))

    return plist

#
# # returns WCET
# def get_wcet(utilizations, periods):
#
#     """ given periods and utilizations returns the WCET as
#         Ci = ceil(Ui * Ti)
#         (See Sanjay paper's experimental section)
#     """
#
#     wcet_list = [ math.ceil(a * b) for a, b in zip(utilizations, periods)]
#     # print("wcet", wcet_list)
#     return wcet_list


# returns WCET
def get_wcet(n, base_util, period_list):
    """ Returns the WCET of the tasks such that total utilization
    of the tasks are equal to base utilization """

    delta = 0.03  # tolerance
    max_count = 100000  # max count for a the while(1) loop

    count = 0

    while 1:

        wcet_candidate = []
        for i in range(0, len(period_list)):
            # print(period_list[i])
            wcet_candidate.append(random.randint(PARAMS.WCET_MIN, min(period_list[i], PARAMS.WCET_MAX)))

        # wcet_candidate = [random.randint(wcet_min, wcet_max) for _ in range(n)]

        # print("wcet candidate", wcet_candidate)

        util = [a / b for a, b in zip(wcet_candidate, period_list)]
        sum_util = sum(util)

        # print("util is: ", util, ", sum is: ", sum_util)

        count += 1
        # print("try for wcet combination #", count)

        if (base_util - delta) <= sum_util <= base_util:
            break

        if count >= max_count:
            raise Exception("Unable to find Task Parameters")

    # print("Got Task Params at iteration: ", count)
    return wcet_candidate

# retuns deadline


def get_deadlines(wcet_list, period_list):
    """ calculates deadline using Sanjay's paper """

    deadline_list = [random.randint(math.ceil(max(ci, pi/2)), PARAMS.PERIOD_MAX) for ci, pi in zip(wcet_list, period_list)]
    return deadline_list


def generate_taskset_for_base_util(n, base_util):

    """ Generate taskset for a given number of tasks and base util """

    period_list = get_periods(n)
    wcet_list = get_wcet(n, base_util, period_list)
    util_list = [a / b for a, b in zip(wcet_list, period_list)]
    deadline_list = get_deadlines(wcet_list, period_list)

    # id of the task in the taskset is starts from 1 (to n)
    taskset = [TF.Task(wcet_list[i], period_list[i], util_list[i],
                       deadline_list[i], i+1,
                       jitter=round(period_list[i] * PARAMS.MAX_JITTER_PERCENTAGE)) for i in
               range(n)]

    return taskset


def generate_taskset_for_base_util_sanjay_paper(n, base_util):

    """ Generate taskset for a given number of tasks and base util """

    # period_list = get_periods(n)
    # period_list = get_period_by_range(n, PARAMS.PERIOD_MIN, PARAMS.PERIOD_MAX)
    # period_list = get_periods_v2(n)
    period_list = get_periods_v3(n)

    # print(period_list)
    # hp = get_lcm(period_list)
    # print("HP is:", hp, "Number of Tasks:", n, "Length of Period List:", len(period_list))

    util_list = UUniFast(n, base_util)
    wcet_list = [math.ceil(ti * ui) for ti, ui in zip(period_list, util_list)]

    deadline_list = get_deadlines(wcet_list, period_list)

    # id of the task in the taskset is starts from 1 (to n)
    taskset = [TF.Task(wcet_list[i], period_list[i], util_list[i],
                       # deadline_list[i], i+1,
                       period_list[i], i + 1,
                       jitter=0) for i in
               range(n)]

    # print("Taskset creation done!")
    return taskset


def generate_taskset_for_true_entropy(n, base_util):

    """ Generate taskset for a given number of tasks and base util """

    period_list = get_periods_entropy(n)

    print(period_list)
    hp = get_lcm(period_list)
    print("HP is:", hp, "Number of Tasks:", n, "Length of Period List:", len(period_list))

    util_list = UUniFast(n, base_util)
    wcet_list = [math.ceil(ti * ui) for ti, ui in zip(period_list, util_list)]

    # deadline_list = get_deadlines(wcet_list, period_list)

    # id of the task in the taskset is starts from 1 (to n)
    taskset = [TF.Task(wcet_list[i], period_list[i], util_list[i],
                       # deadline_list[i], i+1,
                       period_list[i], i + 1,
                       jitter=round(period_list[i] * PARAMS.MAX_JITTER_PERCENTAGE)) for i in
               range(n)]

    return taskset


def generate_all_taskset():

    all_task_set_dict = defaultdict(lambda: defaultdict(dict))

    for n in PARAMS.NUMBER_OF_TASKS_LIST:
        for u in range(PARAMS.N_BASE_UTIL_GRP):
            cnt = 0
            ntc = 0
            print("== Generating taskset for", n, "tasks", " :: base utilization group", u, "==")
            while 1:
                base_util = random.uniform(0.02 + 0.1 * u, 0.08 + 0.1 * u)

                # print("base util:", base_util)
                cnt += 1
                # print("Try # ", cnt)
                try:
                    # taskset = generate_taskset_for_base_util(n, base_util)
                    taskset = generate_taskset_for_base_util_sanjay_paper(n, base_util)
                    # print("Saving Taskset", ntc, "... Found at iteration", cnt)
                    all_task_set_dict[n][u][ntc] = taskset
                    ntc += 1

                except Exception:
                    print("Got caught in Taskset creation!")
                    continue

                if ntc >= PARAMS.N_TASKSET_EACH_GRP:
                    break

                if cnt >= PARAMS.MAXLOOPCOUNT:
                    print("not found for", n, "and ", u)
                    #break
                    # TODO: need to fix that
                    raise Exception("Unable to find taskset!")

    print("Done with Taskset Creation!")
    return all_task_set_dict


def generate_all_taskset_random_task():

    all_task_set_dict = defaultdict(lambda: defaultdict(dict))

    for u in range(PARAMS.N_BASE_UTIL_GRP):
        for ntc in range(PARAMS.N_TASKSET_EACH_GRP):

            n = random.randint(PARAMS.N_TASK_MIN, PARAMS.N_TASK_MAX)
            print("== Generating taskset for", n, "tasks", " :: base utilization group", u, "Taskset#", ntc, "==")

            base_util = random.uniform(0.02 + 0.1 * u, 0.08 + 0.1 * u)
            taskset = generate_taskset_for_base_util_sanjay_paper(n, base_util)
            all_task_set_dict[u][ntc] = taskset

    print("Done with Taskset Creation!")
    return all_task_set_dict


def generate_all_taskset_for_true_entropy():
    all_task_set_dict = defaultdict(lambda: defaultdict(dict))

    for u in range(PARAMS.N_BASE_UTIL_GRP):
        for ntc in range(PARAMS.N_TASKSET_EACH_GRP_TRUE_ENTROPY):
            n = random.randint(PARAMS.N_TASK_ENTOPY_MIN, PARAMS.N_TASK_ENTOPY_MAX)
            print("== Generating taskset for", n, "tasks", " :: base utilization group", u, "Taskset#", ntc, "==")
            base_util = random.uniform(0.02 + 0.1 * u, 0.08 + 0.1 * u)
            taskset = generate_taskset_for_true_entropy(n, base_util)
            all_task_set_dict[u][ntc] = taskset

    print("Done with Taskset Creation!")
    return all_task_set_dict

# Source: https://stackoverflow.com/questions/25470799/circular-list-in-python
def circular_slice(a, start, length):
    """ Returns a circular slice of a list """
    it = itertools.cycle(a)
    next(itertools.islice(it, start, start), None)
    return list(itertools.islice(it, length))


# def get_hamming_distance(l1, l2):
#     assert len(l1) == len(l2)
#     return sum(u != v for u, v in zip(l1, l2))

def get_hamming_distance(l1, l2):
    return distance.hamming(l1, l2)


def write_object_to_file(input_obj, filename):
    """ Write the input object to a Pickle file """

    print("Writing as a Pickle object...")
    with gzip.open(filename, 'wb') as handle:
        dill.dump(input_obj, handle)


def load_object_from_file(filename):
    """ Load the given object from Pickle file """

    with gzip.open(filename, 'rb') as handle:
        output = dill.load(handle)

    return output
