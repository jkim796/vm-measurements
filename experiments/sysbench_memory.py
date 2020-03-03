import csv
import os
import re
import shlex
import subprocess

from experiments import WORKLOADS_DIR, BENCHMARK_TOOLS_DIR
from benchmark import Benchmark, Platform


class SysbenchMemory(Benchmark):
    # Benchmark name as used in INI file sections
    BENCH_NAME = 'sysbench_memory'

    # Performance metric for native output
    NATIVE_METRIC = 'Total operations'
    REGEX_FLOAT = '\d+\.\d+'

    # Performance metric for Docker output
    DOCKER_METRIC = 'memory_ops_per_second'

    # Experiment parameters
    PARAM_NUM_THREADS = 'num_threads'
    PARAM_MEMORY_BLOCK_SIZE = 'memory_block_size'
    PARAM_MEMORY_TOTAL_SIZE = 'memory_total_size'
    PARAM_MEMORY_SCOPE = 'memory_scope'
    PARAM_MEMORY_HUGETLB = 'memory_hugetlb'
    PARAM_MEMORY_OPER = 'memory_oper'
    PARAM_MEMORY_ACCESS_MODE = 'memory_access_mode'

    ORIGINAL_DOCKERFILE_DIR = os.path.join(WORKLOADS_DIR, 'sysbench')
    # Default Dockerfile provided by benchmark-tools (backed up to .Dockerfile)
    DEFAULT_DOCKERFILE_NAME = os.path.join(ORIGINAL_DOCKERFILE_DIR, '.Dockerfile')
    # Dockerfile we'll use with the parameters in INI file
    DOCKERFILE_NAME = os.path.join(ORIGINAL_DOCKERFILE_DIR, 'Dockerfile')

    def __init__(self,
                 num_threads,
                 memory_block_size,
                 memory_total_size,
                 memory_scope,
                 memory_hugetlb,
                 memory_oper,
                 memory_access_mode,
                 platform=Platform.NATIVE):
        super(SysbenchMemory, self).__init__(platform)
        # Parameters
        self.num_threads = num_threads
        self.memory_block_size = memory_block_size
        self.memory_total_size = memory_total_size
        self.memory_scope = memory_scope
        self.memory_hugetlb = memory_hugetlb
        self.memory_oper = memory_oper
        self.memory_access_mode = memory_access_mode

        self.csv_headers = ['num_threads', 'memory_block_size', 'memory_total_size', 'memory_scope', 'memory_hugetlb', 'memory_oper', 'memory_access_mode', 'memory_ops_per_second']
        self.csv_filename = 'sysbench_memory.csv'

    def run_native(self):
        cmd = (f'sysbench --threads={self.num_threads} '
               f'--memory_block_size={self.memory_block_size} '
               f'--memory_total_size={self.memory_total_size} '
               f'--memory_scope={self.memory_scope} '
               f'--memory_hugetlb={self.memory_hugetlb} '
               f'--memory_oper={self.memory_oper} '
               f'--memory_access_mode={self.memory_access_mode} '
               f'memory run')
        print(cmd)
        process = subprocess.run(shlex.split(cmd),
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)
        output_str = process.stdout
        return output_str.split('\n')

    def run_docker(self):
        # Copy the default Dockerfile into a list of strings
        with open(self.DEFAULT_DOCKERFILE_NAME, 'r') as f:
            lines = f.readlines()

        # We decided not to rely on Docker ENV variables

        # # Find the lines with ENV declarations
        # env_linenos = []
        # for lineno, line in enumerate(lines):
        #     if 'ENV' in line:
        #         env_linenos.append(lineno)

        # # Remove these lines - assumes ENV lines are grouped together
        # del lines[env_linenos[0] : env_linenos[-1] + 1]

        # # Create ENV declaration strings
        # env_decls = [f'ENV threads {self.num_threads}\n',
        #              f'ENV max_time {self.max_time}\n',
        #              f'ENV cpu_max_prime {self.cpu_max_prime}\n']

        # # Insert the new ENV decalrations to lines
        # lines[env_linenos[0] : env_linenos[0]] = env_decls

        # This will be the last line in the Dockerflie
        cmd = (f'sysbench --threads={self.num_threads} '
               f'--memory_block_size={self.memory_block_size} '
               f'--memory_total_size={self.memory_total_size} '
               f'--memory_scope={self.memory_scope} '
               f'--memory_hugetlb={self.memory_hugetlb} '
               f'--memory_oper={self.memory_oper} '
               f'--memory_access_mode={self.memory_access_mode} '
               f'memory run')
        lines[-1] = cmd + '"]'

        # Write to Dockerfile
        new_dockerfile = self.DOCKERFILE_NAME
        with open(new_dockerfile, 'w') as f:
            for line in lines:
                f.write(line)

        # Run perf.py script
        perf_cmd = f'python3 {BENCHMARK_TOOLS_DIR}/perf.py run --env {BENCHMARK_TOOLS_DIR}/examples/localhost.yaml sysbench.memory'
        print(perf_cmd)
        process = subprocess.run(shlex.split(perf_cmd),
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)
        output_str = process.stdout
        return output_str.split('\n')

    def parse_output(self, output):
        if self.platform == Platform.NATIVE:
            return self._parse_native_output(output)
        elif self.platform == Platform.DOCKER:
            return self._parse_docker_output(output)

    def _parse_native_output(self, output):
        for line in output:
            if self.NATIVE_METRIC in line:
                print(f"[sysbench memory] {line}")
                matches = re.findall(self.REGEX_FLOAT, line)
                # There should only be one floating point number
                memory_ops_per_second = float(matches[0])
                return memory_ops_per_second

    def _parse_docker_output(self, output):
        for line in output:
            if self.DOCKER_METRIC in line:
                print(f'[sysbench memory] {line}')
                memory_ops_per_second = float(line.split(',')[1])
                return memory_ops_per_second

    def write_to_csv(self, data):
        """Appends the given parameters and performance metric values to the csv file."""
        csv_row = {'num_threads': self.num_threads,
                   'memory_block_size': self.memory_block_size,
                   'memory_total_size': self.memory_total_size,
                   'memory_scope': self.memory_scope,
                   'memory_hugetlb': self.memory_hugetlb,
                   'memory_oper': self.memory_oper,
                   'memory_access_mode': self.memory_access_mode,
                   'memory_ops_per_second': data}

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
