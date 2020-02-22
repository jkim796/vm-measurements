#!/bin/bash

# TODO memory total size 5G fixed?
# TODO discuss why sysbench memory output latency min and avg are 0
# TODO FIO --filepath file.dat file: where can we get this from??

### BENCHMARKS ###
### Microbenchmarks ###
# 1. sysbench.cpu
# 2. sysbench.memory
# 3. fio.randread
# 4. fio.radnwrite
# 5. syscall.syscall

### Applications ###
# 1. ml.tensorflow
# 2. media.ffmpeg


ROOT_DIR=~/vm-measurements
DOCKER_SCRIPT_DIR=${ROOT_DIR}/benchmark-tools

sysbench_cpu_native() {
    # Run sysbench once as a warm-up and take the second result
    MEMSIZE=5G

    sysbench --threads=8 --memory-total-size=${MEMSIZE} memory run > /dev/null
    echo "sysbench --threads=1 cpu run"
    sysbench --threads=1 cpu run
}

sysbench_memory_native() {
    # Run sysbench once as a warm-up and take the second result
    MEMSIZE=5G

    sysbench --threads=8 --memory-total-size=${MEMSIZE} memory run > /dev/null
    echo "sysbench --threads=8 --memory-total-size=${MEMSIZE} memory run"
    sysbench --threads=8 --memory-total-size=${MEMSIZE} memory run
}

fio_randread_native() {
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
}

fio_randwrite_native() {
    workload=write
    ioengine=sync
    size=5000000
    iodepth=4
    blocksize="1m"
    time=""
    path="/disk/file.dat"
    ramp_time=0

    echo "fio --output-format=json --name=test --ramp_time=${ramp_time} --ioengine=${ioengine} --size=${size} \
	--filename=${path} --iodepth=${iodepth} --bs=${blocksize} --rw=${read} ${time}"
    fio --output-format=json --name=test --ramp_time=${ramp_time} --ioengine=${ioengine} --size=${size} \
	--filename=${path} --iodepth=${iodepth} --bs=${blocksize} --rw=${workload} ${time}
}

syscall_syscall_native() {
    if [[ ! -f syscall.c ]]; then
	cp ${DOCKER_SCRIPT_DIR}/workloads/syscall/syscall.c .
	gcc -O2 -o syscall syscall.c
    fi
    count=1000000
    echo "./syscall ${count}"
    ./syscall ${count}
}

ml_tensorflow_native() {
    if [[ ! -d TensorFlow-Examples ]]; then
	git clone https://github.com/aymericdamien/TensorFlow-Examples.git
    fi
    cd TensorFlow-Examples/examples
    export PYTHONPATH=$PYTHONPATH:./TensorFlow-Examples/examples
    workload=./3_NeuralNetworks/convolutional_network.py
    echo "python ${workload} 2>/dev/null"
    python ${workload} 2>/dev/null
}

media_ffmpeg_native() {
    if [[ ! -f video.mp4 ]]; then
	wget https://samples.ffmpeg.org/MPEG-4/video.mp4 video.mp4
    fi
    echo "time ffmpeg -i video.mp4 -c:v libx264 -preset veryslow output.mp4"
    time ffmpeg -i video.mp4 -c:v libx264 -preset veryslow output.mp4
}

run_native() {
    echo "Running native"

    if [[ -n "${BENCHMARK}" ]]; then
	case ${BENCHMARK} in
	    "sysbench.cpu")
		echo "Benchmark = ${BENCHMARK}"
		sysbench_cpu_native
		;;
	    "sysbench.memory")
		echo "Benchmark = ${BENCHMARK}"
		sysbench_memory_native
		;;
	    "fio.randread")
		echo "Benchmark = ${BENCHMARK}"
		fio_randread_native
		;;
	    "fio.randwrite")
		echo "Benchmark = ${BENCHMARK}"
		fio_randwrite_native
		;;
	    "syscall.syscall")
		echo "Benchmark = ${BENCHMARK}"
		syscall_syscall_native
		;;
	    "ml.tensorflow")
		echo "Benchmark = ${BENCHMARK}"
		ml_tensorflow_native
		;;
	    "media.ffmpeg")
		echo "Benchmark = ${BENCHMARK}"
		media_ffmpeg_native
		;;
	    *)
		echo "Unrecognized benchmark ${BENCHMARK}"
		;;
	esac
    else
	echo "Running all benchmarks in platform ${PLATFORM}"
	sysbench_cpu_native
	sysbench_memory_native
	fio_randread_native
	fio_randwrite_native
	syscall_syscall_native
	ml_tensorflow_native
	media_ffmpeg_native
    fi
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

sysbench_cpu_docker() {
    echo "python3 perf.py run --env examples/localhost.yaml sysbench.cpu"
    python3 ${DOCKER_SCRIPT_DIR}/perf.py run --env ${DOCKER_SCRIPT_DIR}/examples/localhost.yaml sysbench.cpu
}

sysbench_memory_docker() {
    echo "python3 perf.py run --env examples/localhost.yaml sysbench.memory"
    python3 ${DOCKER_SCRIPT_DIR}/perf.py run --env ${DOCKER_SCRIPT_DIR}/examples/localhost.yaml sysbench.memory
}

fio_randread_docker() {
    echo "python3 perf.py run --env examples/localhost.yaml fio.randread"
    python3 ${DOCKER_SCRIPT_DIR}/perf.py run --env ${DOCKER_SCRIPT_DIR}/examples/localhost.yaml fio.randread
}

fio_randwrite_docker() {
    echo "python3 perf.py run --env examples/localhost.yaml fio.randwrite"
    python3 ${DOCKER_SCRIPT_DIR}/perf.py run --env ${DOCKER_SCRIPT_DIR}/examples/localhost.yaml fio.randwrite
}

syscall_syscall_docker() {
    echo "python3 perf.py run --env examples/localhost.yaml syscall.syscall"
    python3 ${DOCKER_SCRIPT_DIR}/perf.py run --env ${DOCKER_SCRIPT_DIR}/examples/localhost.yaml syscall.syscall
}

ml_tensorflow_docker() {
    echo "python3 perf.py run --env examples/localhost.yaml ml.tensorflow"
    python3 ${DOCKER_SCRIPT_DIR}/perf.py run --env ${DOCKER_SCRIPT_DIR}/examples/localhost.yaml ml.tensorflow
}

media_ffmpeg_docker() {
    echo "python3 perf.py run --env examples/localhost.yaml media.ffmpeg"
    python3 ${DOCKER_SCRIPT_DIR}/perf.py run --env ${DOCKER_SCRIPT_DIR}/examples/localhost.yaml media.ffmpeg
}

run_docker() {
    echo "Running Docker"

    if [[ -n "${BENCHMARK}" ]]; then
	case ${BENCHMARK} in
	    "sysbench.cpu")
		echo "Benchmark = ${BENCHMARK}"
		sysbench_cpu_docker
		;;
	    "sysbench.memory")
		echo "Benchmark = ${BENCHMARK}"
		sysbench_memory_docker
		;;
	    "fio.randread")
		echo "Benchmark = ${BENCHMARK}"
		fio_randread_docker
		;;
	    "fio.randwrite")
		echo "Benchmark = ${BENCHMARK}"
		fio_randwrite_docker
		;;
	    "syscall.syscall")
		echo "Benchmark = ${BENCHMARK}"
		syscall_syscall_docker
		;;
	    "ml.tensorflow")
		echo "Benchmark = ${BENCHMARK}"
		ml_tensorflow_docker
		;;
	    "media.ffmpeg")
		echo "Benchmark = ${BENCHMARK}"
		media_ffmpeg_docker
		;;
	    *)
		echo "Unrecognized benchmark ${BENCHMARK}"
		;;
	esac
    else
	echo "Running all benchmarks in platform ${PLATFORM}"
	sysbench_cpu_docker
	sysbench_memory_docker
	fio_randread_docker
	fio_randwrite_docker
	syscall_syscall_docker
	ml_tensorflow_docker
	media_ffmpeg_docker
    fi
}

clean() {
    files=( syscall syscall.c TensorFlow-Examples video.mp4 output.mp4 )
    for f in "${files[@]}"; do
	echo "rm -rf $f"
	rm -rf $f
    done
}

display_usage() {
    echo "Usage: ./run.sh [-p|--platform] [-b|--benchmark] [clean]"
    echo "[-p|--platform] can be one of: "
    echo " - native"
    echo " - kvm"
    echo " - docker"
    echo " - firecracker"
    echo "[-b|--benchmark] can be one of: "
    echo " - sysbench.cpu"
    echo " - sysbench.memory"
    echo " - fio.randread"
    echo " - fio.randwrite"
    echo " - syscall.syscall"
    echo " - ml.tensorflow"
    echo " - media.ffmpeg"
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
	-b|--benchmark)
	    BENCHMARK="$2"
	    shift
	    shift
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
