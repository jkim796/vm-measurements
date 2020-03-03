import csv
import os
import re
import shlex
import subprocess

from shutil import copyfile

from experiments import WORKLOADS_DIR, BENCHMARK_TOOLS_DIR
from benchmark import Benchmark, Platform


class Syscall(Benchmark):
    # Benchmark name as used in INI file sections
    BENCH_NAME = 'syscall_syscall'

    # Performance metric for native output
    REGEX_FLOAT = '\d+\.\d+'

    # Performance metric for Docker output
    DOCKER_METRIC = 'syscall_time_ns'

    # Experiment parameters
    PARAM_COUNT = 'count'

    ORIGINAL_DOCKERFILE_DIR = os.path.join(WORKLOADS_DIR, 'syscall')
    # Default Dockerfile provided by benchmark-tools (backed up to .Dockerfile)
    DEFAULT_DOCKERFILE_NAME = os.path.join(ORIGINAL_DOCKERFILE_DIR, '.Dockerfile')
    # Dockerfile we'll use with the parameters in INI file
    DOCKERFILE_NAME = os.path.join(ORIGINAL_DOCKERFILE_DIR, 'Dockerfile')

    # syscall binary file
    SYSCALL_BIN = 'syscall'
    SYSCALL_C_SOURCE = 'syscall.c'

    def __init__(self, count, platform=Platform.NATIVE):
        super(Syscall, self).__init__(platform)
        # Parameters
        self.count = count

        self.csv_headers = ['count', 'runtime']
        self.csv_filename = 'syscall_syscall.csv'

    def run_native(self):
        # If syscall binary doesn't exist, we need to compile source code
        if not os.path.isfile(self.SYSCALL_BIN):
            # Copy source C file
            c_source = os.path.join(self.ORIGINAL_DOCKERFILE_DIR, self.SYSCALL_C_SOURCE)
            copyfile(c_source, self.SYSCALL_BIN)
            # Compile
            gcc_cmd = 'gcc -O2 -o {self.SYSCALL_BIN} {self.SYSCALL_C_SOURCE}'
            print(gcc_cmd)
            process = subprocess.run(shlex.split(gcc_cmd),
                                     stdout=subprocess.PIPE,
                                     universal_newlines=True)
        cmd = f'./syscall {self.count}'
        print(f'[syscall_syscall] {cmd}')
        process = subprocess.run(shlex.split(cmd),
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)
        output_str = process.stdout
        return output_str.split('\n')

    def run_docker(self):
        # Copy the default Dockerfile into a list of strings
        with open(self.DEFAULT_DOCKERFILE_NAME, 'r') as f:
            lines = f.readlines()

        # Remove CMD lines - we'll hardcode in the param values
        for lineno, line in enumerate(lines):
            if 'CMD' in line:
                cmd_lineno = lineno
        del lines[cmd_lineno]

        # We decided not to rely on Docker ENV variables
        # This will be the last line in the Dockerflie
        syscall_cmd = f'./syscall {self.count}'
        cmd = f'CMD ["sh", "-c", "{syscall_cmd}"]'
        lines[-1] = cmd

        # Write to Dockerfile
        new_dockerfile = self.DOCKERFILE_NAME
        with open(new_dockerfile, 'w') as f:
            for line in lines:
                f.write(line)

        # Run perf.py script
        perf_cmd = f'python3 {BENCHMARK_TOOLS_DIR}/perf.py run --env {BENCHMARK_TOOLS_DIR}/examples/localhost.yaml syscall.syscall'
        print(f'[syscall_syscall] {perf_cmd}')
        process = subprocess.run(shlex.split(perf_cmd),
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)
        output_str = process.stdout
        return output_str.split('\n')

    def _parse_native_output(self, output):
        # There's only one line of output for syscall
        line = output[0]
        begin_index = line.index(',') + 1
        end_index = line.index('ns')
        single_runtime = int(line[begin_index : end_index])
        print(f"[syscall_syscall] {single_runtime} ns\n")
        return single_runtime

    def _parse_docker_output(self, output):
        for line in output:
            if self.DOCKER_METRIC in line:
                single_runtime = float(line.split(',')[1])
                print(f'[syscall_syscall] {single_runtime} ns\n')
                return single_runtime

    def write_to_csv(self, data):
        """Appends the given parameters and performance metric values to the csv file."""
        csv_row = {'count': self.count,
                   'runtime': data}

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
