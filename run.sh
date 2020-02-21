#!/bin/sh

# TODO memory total size 5G fixed?
# TODO check if this is correct

# Microbenchmarks

# MEMSIZE=5G

# # sysbench.cpu native
# # run sysbench once as a warm-up and take the second result
# sysbench --threads=8 --memory-total-size=${MEMSIZE} memory run > /dev/null
# sysbench --threads=1 cpu run

# # sysbench.memory
# sysbench --threads=8 --memory-total-size=${MEMSIZE} memory run > /dev/null
# sysbench --threads=1 --memory-total-size=${MEMSIZE} memory run


# fio.randread

# Parameterized test.
workload=read
ioengine=sync
size=5000000
iodepth=4
blocksize="1m"
time=""
path="/disk/file.dat"
ramp_time=0

echo "fio --output-format=json --name=test --ramp_time=${ramp_time} --ioengine=${ioengine} --size=${size} \
--filename=${path} --iodepth=${iodepth} --bs=${blocksize} --rw=${workload} ${time}"

fio --output-format=json --name=test --ramp_time=${ramp_time} --ioengine=${ioengine} --size=${size} \
--filename=${path} --iodepth=${iodepth} --bs=${blocksize} --rw=${workload} ${time}

# # fio.radnwrite
# workload=write
# echo "fio --output-format=json --name=test --ramp_time=${ramp_time} --ioengine=${ioengine} --size=${size} \
# --filename=${path} --iodepth=${iodepth} --bs=${blocksize} --rw=${read} ${time}"

# fio --output-format=json --name=test --ramp_time=${ramp_time} --ioengine=${ioengine} --size=${size} \
# --filename=${path} --iodepth=${iodepth} --bs=${blocksize} --rw=${read} ${time}


# syscall.syscall



# Applications

# ml.tensorflow


# media.ffmpeg
