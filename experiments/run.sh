#!/bin/bash

# TODO memory total size 5G fixed?
# TODO discuss why sysbench memory output latency min and avg are 0
# TODO FIO --filepath file.dat file: where can we get this from??

ROOT_DIR=~/vm-measurements
DOCKER_SCRIPT_DIR=${ROOT_DIR}/benchmark-tools

run_native() {
    echo "Running native"
    ### Microbenchmarks ###

    # 1. sysbench.cpu
    # Run sysbench once as a warm-up and take the second result
    MEMSIZE=5G

    sysbench --threads=8 --memory-total-size=${MEMSIZE} memory run > /dev/null
    echo "sysbench --threads=1 cpu run"
    sysbench --threads=1 cpu run

    # 2. sysbench.memory
    sysbench --threads=8 --memory-total-size=${MEMSIZE} memory run > /dev/null
    echo "sysbench --threads=8 --memory-total-size=${MEMSIZE} memory run"
    sysbench --threads=8 --memory-total-size=${MEMSIZE} memory run

    # 3. fio.randread
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

    # 4. fio.radnwrite
    workload=write
    echo "fio --output-format=json --name=test --ramp_time=${ramp_time} --ioengine=${ioengine} --size=${size} \
	--filename=${path} --iodepth=${iodepth} --bs=${blocksize} --rw=${read} ${time}"
    fio --output-format=json --name=test --ramp_time=${ramp_time} --ioengine=${ioengine} --size=${size} \
	--filename=${path} --iodepth=${iodepth} --bs=${blocksize} --rw=${workload} ${time}

    # 5. syscall.syscall
    if [[ ! -f syscall.c ]]; then
	cp ${DOCKER_SCRIPT_DIR}/workloads/syscall/syscall.c .
	gcc -O2 -o syscall syscall.c
    fi
    count=1000000
    echo "./syscall ${count}"
    ./syscall ${count}


    ### Applications ###

    # 1. ml.tensorflow
    if [[ ! -d TensorFlow-Examples ]]; then
	git clone https://github.com/aymericdamien/TensorFlow-Examples.git
    fi
    cd TensorFlow-Examples/examples
    export PYTHONPATH=$PYTHONPATH:./TensorFlow-Examples/examples
    workload=./3_NeuralNetworks/convolutional_network.py
    echo "python ${workload} 2>/dev/null"
    python ${workload} 2>/dev/null

    # 2. media.ffmpeg
    if [[ ! -f video.mp4 ]]; then
	wget https://samples.ffmpeg.org/MPEG-4/video.mp4 video.mp4
    fi
    echo "time ffmpeg -i video.mp4 -c:v libx264 -preset veryslow output.mp4"
    time ffmpeg -i video.mp4 -c:v libx264 -preset veryslow output.mp4
}

# TODO
run_kvm() {
    echo "Running KVM"
    ### Microbenchmarks ###

    # 1. sysbench.cpu

    # 2. sysbench.memory

    # 3. fio.randread

    # 4. fio.radnwrite

    # 5. syscall.syscall


    ### Applications ###

    # 1. ml.tensorflow

    # 2. media.ffmpeg
}

# TODO
run_firecracker() {
    echo "Running Firecracker"
    ### Microbenchmarks ###

    # 1. sysbench.cpu

    # 2. sysbench.memory

    # 3. fio.randread

    # 4. fio.radnwrite

    # 5. syscall.syscall


    ### Applications ###

    # 1. ml.tensorflow

    # 2. media.ffmpeg

}

run_docker() {
    echo "Running Docker"
    ### Microbenchmarks

    # 1. sysbench.cpu
    echo "python3 perf.py run --env examples/localhost.yaml sysbench.cpu"
    python3 ${DOCKER_SCRIPT_DIR}/perf.py run --env ${DOCKER_SCRIPT_DIR}/examples/localhost.yaml sysbench.cpu

    # 2. sysbench.memory
    echo "python3 perf.py run --env examples/localhost.yaml sysbench.memory"
    python3 ${DOCKER_SCRIPT_DIR}/perf.py run --env ${DOCKER_SCRIPT_DIR}/examples/localhost.yaml sysbench.memory

    # 3. fio.randread
    echo "python3 perf.py run --env examples/localhost.yaml fio.randread"
    python3 ${DOCKER_SCRIPT_DIR}/perf.py run --env ${DOCKER_SCRIPT_DIR}/examples/localhost.yaml fio.randread

    # 4. fio.radnwrite
    echo "python3 perf.py run --env examples/localhost.yaml fio.randwrite"
    python3 ${DOCKER_SCRIPT_DIR}/perf.py run --env ${DOCKER_SCRIPT_DIR}/examples/localhost.yaml fio.randwrite

    # 5. syscall.syscall
    echo "python3 perf.py run --env examples/localhost.yaml syscall.syscall"
    python3 ${DOCKER_SCRIPT_DIR}/perf.py run --env ${DOCKER_SCRIPT_DIR}/examples/localhost.yaml syscall.syscall


    ### Applications

    # 1. ml.tensorflow
    echo "python3 perf.py run --env examples/localhost.yaml ml.tensorflow"
    python3 ${DOCKER_SCRIPT_DIR}/perf.py run --env ${DOCKER_SCRIPT_DIR}/examples/localhost.yaml ml.tensorflow

    # 2. media.ffmpeg
    echo "python3 perf.py run --env examples/localhost.yaml media.ffmpeg"
    python3 ${DOCKER_SCRIPT_DIR}/perf.py run --env ${DOCKER_SCRIPT_DIR}/examples/localhost.yaml media.ffmpeg
}

clean() {
    files=( syscall syscall.c TensorFlow-Examples video.mp4 output.mp4 )
    for f in "${files[@]}"; do
	echo "rm -rf $f"
	rm -rf $f
    done
}

display_usage() {
    echo "Usage: ./run.sh [-p|--platform] [clean]"
    echo "[-p|--platform] can be one of: "
    echo " - native"
    echo " - kvm"
    echo " - docker"
    echo " - firecracker"
    echo "If a platform is not specified, all four platforms are run."
    echo "clean removes the following files: ( syscall syscall.c TensorFlow-Examples video.mp4 output.mp4 )"
}


# Parse optional arguments
while [[ $# -gt 0 ]]
do
    key="$1"
    case $key in
	-p|--platform)
	    PLATFORM="$2"
	    shift  # past argument
	    shift  # past value
	    ;;
	-h|--help)
	    display_usage
	    exit
	    ;;
	clean)
	    clean
	    exit
	    ;;
	*)
	    shift  # past argument
	    ;;
    esac
done

if [[ -n "${PLATFORM}" ]]; then
    case "${PLATFORM}" in
	"native")
	    run_native
	    ;;
	"kvm")
	    run_kvm
	    ;;
	"firecracker")
	    run_firecracker
	    ;;
	"docker")
	    run_docker
	    ;;
	*)
	    echo "${PLATFORM}: Not a recognized option."
	    ;;
    esac
else
    echo "Running all platforms!"
    run_native
    run_kvm
    run_firecracker
    run_docker
fi
