__author__ = "Monowar Hasan"
__email__ = "mhasan11@illinois.edu"

import math


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

""" Helper for creating constant variables
    Found in: https://stackoverflow.com/questions/2682745/how-to-create-a-constant-in-python
"""

class MetaConst(type):
    def __getattr__(cls, key):
        return cls[key]

    def __setattr__(cls, key, value):
        raise TypeError


class Const(object, metaclass=MetaConst):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        raise TypeError


class PARAMS(Const):

    """ This class stores all the configuration parameters """

    LARGENUMBER = 100000
    MAX_ITER = 10000
    MAXLOOPCOUNT = 100000

    PERIOD_MIN = 10
    PERIOD_MAX = 100
    COMMON_HP = PERIOD_MAX
    # NUMBER_OF_TASKS_LIST = [5, 10, 15]  # list of number of tasks -- varied over experiments
    # NUMBER_OF_TASKS_LIST = [3, 5, 7, 10, 12, 15]  # list of number of tasks -- varied over experiments

    N_TASK_MIN = 3
    N_TASK_MAX = 10

    NUMBER_OF_HP = 100  # number of HP we want to Simulate
    NUMBER_OF_HP_RATIO_EXP = 10  # number of HP for Ratio experiment

    N_BASE_UTIL_GRP = 10
    N_TASKSET_EACH_GRP = 500  # number of taskset in each base-utilization group

    N_TASKSET_EACH_GRP_TRUE_ENTROPY = 15  # number of taskset in each base-utilization group

    # name of the experiments
    NAME_EDF = "EDF"
    NAME_RAND_NOIDLE = "RAND_NOIDLE"
    NAME_RAND_IDLE = "RAND_IDLE"
    NAME_RAND_IDLE_FINE = "RAND_IDLE_FINE"

    GENERATE_NEW_TC = False  # indicate whether we will generate new taskset or load from file

    # TASKSET_FILENAME = 'all_taskset_n_5_10_15_hp_100.pickle.gzip'
    # TASKSET_FILENAME = 'all_taskset_n_3_5_7_10_12_15_hp_100.pickle.gzip'
    # TASKSET_FILENAME = 'all_taskset_n_3_to_15_tc_250_hp_100.pickle.gzip'
    TASKSET_FILENAME = 'all_taskset_n_3_to_15_tc_500_hp_100.pickle.gzip'


    DIST_UNIFORM = "Dist::Uniform"

    # for Entropy
    APEN_FACTOR = 0.35

    # Experiment outputs
    ENTROPY_OUT_FILENAME = 'entropy_all.pickle.gzip'
    RATIO_OUT_FILENAME = 'ratio_all.pickle.gzip'
    ENTROPY_TRUE_CORR_OUT_FILENAME = 'en_tru_cor.pickle.gzip'

