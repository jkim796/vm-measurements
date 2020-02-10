#!/usr/bin/env bash

if [ "$#" -lt "1" ]; then
  echo "usage: $0 <--mock |--env=<filename>> ..."
  echo "example: $0 --mock --runs=8"
  exit 1
fi

set -xe

readonly TIMESTAMP=`date "+%Y%m%d-%H%M%S"`
readonly OUTDIR="$(mktemp -d run-${TIMESTAMP}-XXX)"
readonly DEFAULT_RUNTIMES="--runtime=runc --runtime=runsc --runtime=runsc-kvm"
readonly ALL_RUNTIMES="--runtime=runc --runtime=runsc --runtime=runsc-kvm"

python3 perf.py run "$@" ${DEFAULT_RUNTIMES} 'fio.(read|write)' --metric=bandwidth --size=5g --ioengine=sync --blocksize=1m > "${OUTDIR}/fio.csv"
python3 perf.py run "$@" ${DEFAULT_RUNTIMES} fio.rand --metric=bandwidth --size=5g --ioengine=sync --blocksize=4k --time=30 > "${OUTDIR}/tmp_fio.csv"
cat "${OUTDIR}/tmp_fio.csv" | grep "\(runc\|runsc\)" >> "${OUTDIR}/fio.csv"
rm "${OUTDIR}/tmp_fio.csv"

python3 perf.py run "$@" ${DEFAULT_RUNTIMES} 'fio.(read|write)' --metric=bandwidth --tmpfs=True --size=5g --ioengine=sync --blocksize=1m > "${OUTDIR}/fio-tmpfs.csv"
python3 perf.py run "$@" ${DEFAULT_RUNTIMES} fio.rand --metric=bandwidth --tmpfs=True --size=5g --ioengine=sync --blocksize=4k --time=30 > "${OUTDIR}/tmp_fio.csv"
cat "${OUTDIR}/tmp_fio.csv" | grep "\(runc\|runsc\)" >> "${OUTDIR}/fio-tmpfs.csv"
rm "${OUTDIR}/tmp_fio.csv"


python3 perf.py run "$@" ${DEFAULT_RUNTIMES} startup --count=50  >  "${OUTDIR}/startup.csv"
python3 perf.py run "$@" ${DEFAULT_RUNTIMES} density > "${OUTDIR}/density.csv"

python3 perf.py run "$@" ${DEFAULT_RUNTIMES} sysbench.cpu --threads=1 --max_prime=50000 --options='--max-time=5' > "${OUTDIR}/sysbench-cpu.csv"
python3 perf.py run "$@" ${DEFAULT_RUNTIMES} sysbench.memory --threads=1 --options='--memory-block-size=1M --memory-total-size=500G'  > "${OUTDIR}/sysbench-memory.csv"
python3 perf.py run "$@" ${ALL_RUNTIMES} syscall > "${OUTDIR}/syscall.csv"
python3 perf.py run "$@" ${DEFAULT_RUNTIMES} 'network.(upload|download)' --runs=20 > "${OUTDIR}/iperf.csv"
python3 perf.py run "$@" ${DEFAULT_RUNTIMES} ml.tensorflow > "${OUTDIR}/tensorflow.csv"
python3 perf.py run "$@" ${DEFAULT_RUNTIMES} media.ffmpeg > "${OUTDIR}/ffmpeg.csv"
python3 perf.py run "$@" ${DEFAULT_RUNTIMES} http.httpd --path=latin100k.txt --connections=1 --connections=5 --connections=10 --connections=25 > "${OUTDIR}/httpd100k.csv"
python3 perf.py run "$@" ${DEFAULT_RUNTIMES} http.httpd --path=latin10240k.txt --connections=1 --connections=5 --connections=10 --connections=25 > "${OUTDIR}/httpd10240k.csv"
python3 perf.py run "$@" ${DEFAULT_RUNTIMES} redis > "${OUTDIR}/redis.csv"
python3 perf.py run "$@" ${DEFAULT_RUNTIMES} 'http.(ruby|node)' > "${OUTDIR}/applications.csv"
