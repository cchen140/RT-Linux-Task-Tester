#define _GNU_SOURCE
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <linux/unistd.h>
#include <linux/kernel.h>
#include <linux/types.h>
#include <sys/syscall.h>
#include <pthread.h>

/* test specific configurations */
#define PRINT_FIRST_START_TIME
#ifdef PRINT_FIRST_START_TIME
#include <time.h>	// For timespec and clock_gettime(). Remember to use -lrt when compiling for ARM CPU.
struct timespec timeInstance;
#endif


#define gettid() syscall(__NR_gettid)

#define SCHED_DEADLINE	6

/* XXX use the proper syscall numbers */
#ifdef __x86_64__
#define __NR_sched_setattr		314
#define __NR_sched_getattr		315
#endif

#ifdef __i386__
#define __NR_sched_setattr		351
#define __NR_sched_getattr		352
#endif

#ifdef __arm__
#define __NR_sched_setattr		380
#define __NR_sched_getattr		381
#endif

typedef struct task_params {
	char* mibench_cmd;
	__u64 runtime;	// ns
	__u64 period;	// ns
}task_params;

struct task_params task_params_instances[20];
/*= {
	{1 * 1000 * 1000, 36 * 1000 * 1000},
	{9 * 1000 * 1000, 73 * 1000 * 1000},
	{4 * 1000 * 1000, 71 * 1000 * 1000},
	{22 * 1000 * 1000, 95 * 1000 * 1000},
	{7 * 1000 * 1000, 83 * 1000 * 1000},
	{3 * 1000 * 1000, 48 * 1000 * 1000},
	{3 * 1000 * 1000, 59 * 1000 * 1000},
	{3 * 1000 * 1000, 62 * 1000 * 1000},
	{8 * 1000 * 1000, 88 * 1000 * 1000},
	{2 * 1000 * 1000, 49 * 1000 * 1000},
};
*/

static volatile int done;

struct sched_attr {
	__u32 size;

	__u32 sched_policy;
	__u64 sched_flags;

	/* SCHED_NORMAL, SCHED_BATCH */
	__s32 sched_nice;

	/* SCHED_FIFO, SCHED_RR */
	__u32 sched_priority;

	/* SCHED_DEADLINE (nsec) */
	__u64 sched_runtime;
	__u64 sched_deadline;
	__u64 sched_period;
};

int sched_setattr(pid_t pid,
		const struct sched_attr *attr,
		unsigned int flags)
{
	return syscall(__NR_sched_setattr, pid, attr, flags);
}

int sched_getattr(pid_t pid,
		struct sched_attr *attr,
		unsigned int size,
		unsigned int flags)
{
	return syscall(__NR_sched_getattr, pid, attr, size, flags);
}

void busy_loop_us(unsigned int us) {
        unsigned i, j, k;
        for (i=0;i<us;i++) {
                for (j=0;j<51;j++)
                        k=i+j;
        }
	i = k;	// this is to mute compiler's warnings.
}

void *run_deadline(void *data)
{
	struct sched_attr attr;
	int ret;
	unsigned int flags = 0;
	int busy_loop_us_time = 0;

	#ifdef PRINT_FIRST_START_TIME
	char start_time_printed = 0;
	#endif

	printf("deadline thread started [%ld] %lld, %lld \n", gettid(), ((task_params*)data)->runtime, ((task_params*)data)->period);

	if (((task_params*)data)->mibench_cmd != NULL) {
		printf("executing mibench command: \"%s\"\n", ((task_params*)data)->mibench_cmd);
	}

	attr.size = sizeof(attr);
	attr.sched_flags = 0;
	attr.sched_nice = 0;
	attr.sched_priority = 0;

	attr.sched_policy = SCHED_DEADLINE;
	attr.sched_runtime = ((task_params*)data)->runtime;
	attr.sched_period = attr.sched_deadline = ((task_params*)data)->period;

	ret = sched_setattr(0, &attr, flags);
	if (ret < 0) {
		done = 0;
		perror("sched_setattr");
		exit(-1);
	}

	// This configuration is not needed (is not affective in this case):
	//   Enable this thread's cancellation capability so that other threads can cancel this thread.
	// pthread_setcancelstate(PTHREAD_CANCEL_ENABLE, NULL);

	if (((task_params*)data)->mibench_cmd == NULL) {
		busy_loop_us_time = (attr.sched_runtime/1000)*0.8;
		while (!done) {
			busy_loop_us(busy_loop_us_time);
			sched_yield();
			#ifdef PRINT_FIRST_START_TIME
			if (start_time_printed == 0) {
				clock_gettime(CLOCK_MONOTONIC, &timeInstance);
				printf("[%ld] start time = %ld ns, task phase = %lld ns\r\n", gettid(), timeInstance.tv_nsec, timeInstance.tv_nsec%((task_params*)data)->period);
				start_time_printed = 1;
			}
			#endif
		}
	} else {
		while (!done) {
                        system(((task_params*)data)->mibench_cmd);
                        sched_yield();
                }
	}

	printf("deadline thread dies [%ld]\n", gettid());
	pthread_exit(NULL);
	return NULL;
}


#define	TASK_PARAMETER_OFFSET	3
int main (int argc, char **argv)
{
	pthread_t threads[30];
	int num_of_tasks, num_of_mibench_tasks;
	int i, j;
	int exp_time_second = 1;

	if (argc < 3) {
		printf("Arguments are wrong.\r\n");
		printf("Usage (w/o mibench): ./mix [duration_sec] [task_num] [T_0] [T_1] [T_i] [C_0] [C_1] [C_i]\r\n");
		printf("Usage (w/ mibench): ./mix [duration_sec] [task_num] [T_0] [T_1] [T_i] [C_0] [C_1] [C_i] \"task_i_cmd\"\r\n");
		printf("\t- when N commands are given, the last N tasks are assigned to them.\r\n");
		printf("\t- all times are in ms (and then converted into ns internally.)\r\n");
		return 0;
	}

	num_of_tasks = atoi(argv[2]);
	printf("%d tasks to be loaded.\n", num_of_tasks);

	exp_time_second = atoi(argv[1]);
	printf("Running experiment for %d seconds.\n", exp_time_second);

	// periods
	for (i=0; i<num_of_tasks; i++) {
		task_params_instances[i].period = strtoull(argv[i+TASK_PARAMETER_OFFSET], NULL, 10);
		task_params_instances[i].period *= (1000*1000);
	}

	// runtime
	for (i=0; i<num_of_tasks; i++) {
		task_params_instances[i].runtime = strtoull(argv[i+TASK_PARAMETER_OFFSET+num_of_tasks], NULL, 10);
		task_params_instances[i].runtime *= (1000*1000);
	}

	// mibench commands
	num_of_mibench_tasks = argc - TASK_PARAMETER_OFFSET - (2*num_of_tasks);
	for (i=0; i<num_of_tasks-num_of_mibench_tasks; i++) {
                task_params_instances[i].mibench_cmd = NULL;
        }
	for (i=num_of_tasks-num_of_mibench_tasks, j=0; i<num_of_tasks; i++, j++) {
		// This task should run a mibench program. Send the cmd directly.
		task_params_instances[i].mibench_cmd = argv[j+TASK_PARAMETER_OFFSET+(2*num_of_tasks)];
	}
	

	printf("main thread [%ld]\n", gettid());

	//sleep(1);

	for (i=0; i<num_of_tasks; i++) {
		pthread_create(&threads[i], NULL, run_deadline, &task_params_instances[i]);
	}
	
	sleep(exp_time_second);

	done = 1;

	for (i=0; i<num_of_tasks; i++) {
		//pthread_cancel(threads[i]);
		pthread_join(threads[i], NULL);
	}

	sleep(1);

	printf("main dies [%ld]\n", gettid());
	return 0;
}
