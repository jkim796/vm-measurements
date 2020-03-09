#!/bin/bash

if [ -z "$1" ]; then
    echo "usage: $0 native|docker"
    exit 1
fi

platform=$1

sudo python3 run.py -p $platform -b config/sysbench_memory_write_seq.ini
sudo python3 run.py -p $platform -b config/sysbench_memory_write_rnd.ini
sudo python3 run.py -p $platform -b config/sysbench_memory_read_seq.ini
sudo python3 run.py -p $platform -b config/sysbench_memory_read_rnd.ini
