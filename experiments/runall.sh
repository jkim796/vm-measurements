#!/bin/bash

if [ -z "$1" ]; then
    echo "usage: $0 native|docker"
    exit 1
fi

platform=$1

sudo python3 run.py -p $platform -b config/sysbench_cpu.ini
sudo python3 run.py -p $platform -b config/sysbench_memory.ini
sudo python3 run.py -p $platform -b config/fio_randread.ini
sudo python3 run.py -p $platform -b config/fio_randwrite.ini
sudo python3 run.py -p $platform -b config/syscall.ini
sudo python3 run.py -p $platform -b config/ml_tensorflow.ini
sudo python3 run.py -p $platform -b config/media_ffmpeg.ini
