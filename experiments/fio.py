import csv
import os
import re
import shlex
import subprocess
import json

from enum import Enum

from experiments import WORKLOADS_DIR, BENCHMARK_TOOLS_DIR
from benchmark import Benchmark, Platform


class FioSubBench(Enum):
    RANDREAD = 1
    RANDWRITE = 2


class Fio(Benchmark):
    # Benchmark name as used in INI file sections
    BENCH_NAME = 'fio'

    # Performance metric for native output
    BW = 'bw'

    # Performance metric for Docker output
    DOCKER_METRIC = 'bandwidth'

    # Experiment parameters
    PARAM_RAMP_TIME = 'ramp_time'
    PARAM_IOENGINE = 'ioengine'
    PARAM_FILENAME = 'filename'
    PARAM_BS = 'bs'
    PARAM_RW = 'rw'
    PARAM_NRFILES = 'nrfiles'
    PARAM_FILESIZE = 'filesize'
    PARAM_THREAD = 'thread'
    PARAM_NUMJOBS = 'numjobs'
    PARAM_TIME_BASED = 'time_based'
    PARAM_RUNTIME = 'runtime'

    ORIGINAL_DOCKERFILE_DIR = os.path.join(WORKLOADS_DIR, 'fio')
    # Default Dockerfile provided by benchmark-tools (backed up to .Dockerfile)
    DEFAULT_DOCKERFILE_NAME = os.path.join(ORIGINAL_DOCKERFILE_DIR, '.Dockerfile')
    # Dockerfile we'll use with the parameters in INI file
    DOCKERFILE_NAME = os.path.join(ORIGINAL_DOCKERFILE_DIR, 'Dockerfile')

    def __init__(self,
                 ramp_time,
                 ioengine,
                 bs,
                 rw,
                 nrfiles,
                 filesize,
                 thread,
                 numjobs,
                 time_based,
                 runtime,
                 sub_bench: FioSubBench,
                 platform=Platform.NATIVE):
        super(Fio, self).__init__(platform)
        self.ramp_time = ramp_time
        self.ioengine = ioengine
        self.bs = bs
        self.rw = rw
        self.nrfiles = nrfiles
        self.filesize = filesize
        self.thread = (thread == 'True')
        self.numjobs = numjobs
        self.time_based = (time_based == 'True')
        self.runtime = runtime

        self.sub_bench = sub_bench

        self.csv_headers = ['ramp_time', 'ioengine', 'bs', 'rw', 'nrfiles', 'filesize', 'thread', 'numjobs', 'time_based', 'runtime', 'bw']
        if self.sub_bench == FioSubBench.RANDREAD:
            self.csv_filename = 'fio_randread.csv'
        elif self.sub_bench == FioSubBench.RANDWRITE:
            self.csv_filename = 'fio_randwrite.csv'

    def run_native(self):
        thread_option = '' if self.thread is False else '--thread'
        time_based_option = '' if self.time_based is False else '--time_based'
        cmd = (f'fio --output-format=json --name=test '
               f'--ramp_time={self.ramp_time} '
               f'--ioengine={self.ioengine} '
               f'--bs={self.bs} '
               f'--fsync={self.bs} '
               f'--rw={self.rw} '
               f'--nrfiles={self.nrfiles} '
               f'--filesize={self.filesize} '
               f'{thread_option} '
               f'--numjobs={self.numjobs} '
               f'--group_reporting '
               f'{time_based_option} '
               f'--runtime={self.runtime}')
        if self.sub_bench == FioSubBench.RANDREAD:
            print(f'[fio_randread] {cmd}')
        elif self.sub_bench == FioSubBench.RANDWRITE:
            print(f'[fio_randwrite] {cmd}')
        process = subprocess.run(shlex.split(cmd),
                             stdout=subprocess.PIPE,
                             universal_newlines=True)
        output_str = process.stdout
        return output_str

    def run_docker(self):
        # Copy the default Dockerfile into a list of strings
        with open(self.DEFAULT_DOCKERFILE_NAME, 'r') as f:
            lines = f.readlines()

        # Find the lines with ENV declarations
        env_linenos = []
        for lineno, line in enumerate(lines):
            if 'ENV' in line:
                env_linenos.append(lineno)

        # Remove ENV lines - assumes ENV lines are grouped together
        del lines[env_linenos[0] : env_linenos[-1] + 1]

        # Remove CMD lines - we'll hardcode in the param values
        for lineno, line in enumerate(lines):
            if 'CMD' in line:
                cmd_lineno = lineno
        del lines[cmd_lineno : cmd_lineno + 2]

        # Fio-specific: find the CMD lines
        thread_option = '' if self.thread is False else '--thread'
        time_based_option = '' if self.time_based is False else '--time_based'
        fio_cmd = (f'fio --output-format=json --name=test '
                   f'--ramp_time={self.ramp_time} '
                   f'--ioengine={self.ioengine} '
                   f'--bs={self.bs} '
                   f'--fsync={self.bs} '
                   f'--rw={self.rw} '
                   f'--nrfiles={self.nrfiles} '
                   f'--filesize={self.filesize} '
                   f'{thread_option} '
                   f'--numjobs={self.numjobs} '
                   f'--group_reporting '
                   f'{time_based_option} '
                   f'--runtime={self.runtime}'
        )
        cmd = f'CMD ["sh", "-c", "{fio_cmd}"]'
        lines[-1] = cmd

        # Write to Dockerfile
        new_dockerfile = self.DOCKERFILE_NAME
        with open(new_dockerfile, 'w') as f:
            for line in lines:
                f.write(line)

        # Run perf.py script
        if self.sub_bench == FioSubBench.RANDREAD:
            perf_cmd = f'python3 {BENCHMARK_TOOLS_DIR}/perf.py run --env {BENCHMARK_TOOLS_DIR}/examples/localhost.yaml fio.randread'
            print(f'[fio_randread] {perf_cmd}')
        elif self.sub_bench == FioSubBench.RANDWRITE:
            perf_cmd = f'python3 {BENCHMARK_TOOLS_DIR}/perf.py run --env {BENCHMARK_TOOLS_DIR}/examples/localhost.yaml fio.randwrite'
            print(f'[fio_randwrite] {perf_cmd}')
        process = subprocess.run(shlex.split(perf_cmd),
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)
        output_str = process.stdout
        return output_str.split('\n')

    def _parse_native_output(self, output):
        results_json = json.loads(output)
        if self.sub_bench == FioSubBench.RANDREAD:
            match = results_json['jobs'][0]['read'][self.BW]
            metric = int(match) * 1024
            print(f'[fio_randread] bandwidth: {metric}\n')
            return metric
        elif self.sub_bench == FioSubBench.RANDWRITE:
            match = results_json['jobs'][0]['write'][self.BW]
            metric = int(match) * 1024
            print(f'[fio_randwrite] bandwidth: {metric}\n')
            return metric

    def _parse_docker_output(self, output):
        for line in output:
            if self.DOCKER_METRIC in line:
                bw = int(line.split(',')[1])
                if self.sub_bench == FioSubBench.RANDREAD:
                    print(f'[fio randread] Bandwidth: {bw}\n')
                elif self.sub_bench == FioSubBench.RANDWRITE:
                    print(f'[fio randwrite] Bandwidth: {bw}\n')
                return bw

    def write_to_csv(self, data):
        csv_row = {'ramp_time': self.ramp_time,
                   'ioengine': self.ioengine,
                   'bs': self.bs,
                   'rw': self.rw,
                   'nrfiles': self.nrfiles,
                   'filesize': self.filesize,
                   'thread': self.thread,
                   'numjobs': self.numjobs,
                   'time_based': self.time_based,
                   'runtime': self.runtime,
                   'bw': data}

        # Check if results directory have been created
        if not os.path.isdir(self.RESULTS_CSV_DIR):
            os.mkdir(self.RESULTS_CSV_DIR)

        if self.platform == Platform.NATIVE:
            if not os.path.isdir(self.NATIVE_RESULTS_DIR):
                os.mkdir(self.NATIVE_RESULTS_DIR)
            filepath = os.path.join(self.NATIVE_RESULTS_DIR, self.csv_filename)
        elif self.platform == Platform.DOCKER:
            if not os.path.isdir(self.DOCKER_RESULTS_DIR):
                os.mkdir(self.DOCKER_RESULTS_DIR)
            filepath = os.path.join(self.DOCKER_RESULTS_DIR, self.csv_filename)

        # Write CSV headers when creating file for first time
        if not os.path.isfile(filepath):
            with open(filepath, 'w') as csv_file:
                csv_writer = csv.DictWriter(csv_file, fieldnames=self.csv_headers)
                csv_writer.writeheader()

        # Append row to CSV file
        with open(filepath, 'a') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=self.csv_headers)
            csv_writer.writerow(csv_row)
