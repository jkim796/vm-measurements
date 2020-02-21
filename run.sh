#!/bin/sh

# TODO memory total size 5G fixed?
# TODO discuss why sysbench memory output latency min and avg are 0
# TODO FIO --filepath file.dat file: where can we get this from??

# Microbenchmarks

MEMSIZE=5G

# # sysbench.cpu native
# # run sysbench once as a warm-up and take the second result
# sysbench --threads=8 --memory-total-size=${MEMSIZE} memory run > /dev/null
# sysbench --threads=1 cpu run

# # sysbench.memory
# sysbench --threads=8 --memory-total-size=${MEMSIZE} memory run > /dev/null
# sysbench --threads=8 --memory-total-size=${MEMSIZE} memory run


# fio.randread

# # Parameterized test.
# workload=read
# ioengine=sync
# size=5000000
# iodepth=4
# blocksize="1m"
# time=""
# path="/disk/file.dat"
# ramp_time=0

# echo "fio --output-format=json --name=test --ramp_time=${ramp_time} --ioengine=${ioengine} --size=${size} \
# --filename=${path} --iodepth=${iodepth} --bs=${blocksize} --rw=${workload} ${time}"

# fio --name=test --ramp_time=${ramp_time} --ioengine=${ioengine} --size=${size} \
# --filename=${path} --iodepth=${iodepth} --bs=${blocksize} --rw=${workload} ${time}

# # fio.radnwrite
# workload=write
# echo "fio --output-format=json --name=test --ramp_time=${ramp_time} --ioengine=${ioengine} --size=${size} \
# --filename=${path} --iodepth=${iodepth} --bs=${blocksize} --rw=${read} ${time}"

# fio --output-format=json --name=test --ramp_time=${ramp_time} --ioengine=${ioengine} --size=${size} \
# --filename=${path} --iodepth=${iodepth} --bs=${blocksize} --rw=${read} ${time}


# # syscall.syscall
# cp ./benchmark-tools/workloads/syscall/syscall.c .
# gcc -O2 -o syscall syscall.c

# count=1000000
# ./syscall ${count}



# Applications

# ml.tensorflow
# #git clone https://github.com/aymericdamien/TensorFlow-Examples.git
# cd TensorFlow-Examples/examples
# export PYTHONPATH=$PYTHONPATH:./TensorFlow-Examples/examples

# workload=./3_NeuralNetworks/convolutional_network.py
# python ${workload} 2>/dev/null


# media.ffmpeg
#WORKDIR /media
wget https://samples.ffmpeg.org/MPEG-4/video.mp4 video.mp4
time ffmpeg -i video.mp4 -c:v libx264 -preset veryslow output.mp4
