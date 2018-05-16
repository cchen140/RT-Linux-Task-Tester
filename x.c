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
}

void *run_deadline(void *data)
{
	struct sched_attr attr;
	int ret;
	unsigned int flags = 0;
	int busy_loop_us_time = 0;

	printf("deadline thread started [%ld] %lld, %lld \n", gettid(), ((task_params*)data)->runtime, ((task_params*)data)->period);

	attr.size = sizeof(attr);
	attr.sched_flags = 0;
	attr.sched_nice = 0;
	attr.sched_priority = 0;

	/* This creates a 10ms/30ms reservation */
	attr.sched_policy = SCHED_DEADLINE;
	attr.sched_runtime = ((task_params*)data)->runtime;
	attr.sched_period = attr.sched_deadline = ((task_params*)data)->period;

	ret = sched_setattr(0, &attr, flags);
	if (ret < 0) {
		done = 0;
		perror("sched_setattr");
		exit(-1);
	}

	busy_loop_us_time = (attr.sched_runtime/1000)*0.8;
	while (!done) {
		busy_loop_us(busy_loop_us_time);
		sched_yield();
	}

	printf("deadline thread dies [%ld]\n", gettid());
	pthread_exit(NULL);
	return NULL;
}



int main (int argc, char **argv)
{
	pthread_t threads[30];
	int num_of_tasks = (argc - 2)/2;
	int i;
	int exp_time_second = 1;

	if (argc < 3) {
		printf("Arguments are wrong.");
		return 0;
	}

	exp_time_second = atoi(argv[1]);
	printf("Running experiment for %d seconds.\n", exp_time_second);

	// periods
	for (i=0; i<num_of_tasks; i++) {
		task_params_instances[i].period = atoi(argv[i+2]);
		task_params_instances[i].period *= (1000*1000);
	}

	// runtime
	for (i=0; i<num_of_tasks; i++) {
		task_params_instances[i].runtime = atoi(argv[i+2+num_of_tasks]);
		task_params_instances[i].runtime *= (1000*1000);
	}

	printf("main thread [%ld]\n", gettid());

	for (i=0; i<num_of_tasks; i++) {
		pthread_create(&threads[i], NULL, run_deadline, &task_params_instances[i]);
	}
	
	sleep(exp_time_second);

	done = 1;

	for (i=0; i<num_of_tasks; i++) {
		pthread_join(threads[i], NULL);
	}

	sleep(1);

	printf("main dies [%ld]\n", gettid());
	return 0;
}
