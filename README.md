# RT-Linux-Task-Tester

## File Description
- **x.c**: Source code of the true test program that creates RT processes.
- **x**: Executable of x.c.
- **run_single_x**: Test just a single instance.
- **run_x_begin_id**: Run mass test beginning with a given taskset ID.
- **console_black_hole**: It is to eat up output messages.
- **sample_tasksets (dic)**: This folder contains some sample tasksets. 

## Howto
### Run a single test
- Usage
```
sudo ./run_single_x [LOG_ID] [TEST_DURATION] "[TASKSET_PARAMETERS]"
```

- Example
```
sudo ./run_single_x 1 1 "10 1" 
```

### Run a mass test
- Usage
```
sudo ./run_x_begin_id [TEST_DURATION] [BEGIN_TASKSET_ID] [TASKSET_FILE_PATH]
```

- Example
```
sudo ./run_x_begin_id 5 1 TSK_Outputs/out0.txt 
```
