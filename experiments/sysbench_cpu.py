import csv
import os
import re
import shlex
import subprocess

from experiments import WORKLOADS_DIR, BENCHMARK_TOOLS_DIR

from benchmark import Benchmark, Platform


class SysbenchCPU(Benchmark):
    # Benchmark name as used in INI file sections
    BENCH_NAME = 'sysbench_cpu'

    # Performance metric for native output
    EVENTS_PER_SECOND = 'events per second'
    REGEX_FLOAT = '\d+\.\d+'

    # Performance metric for Docker output
    EVENTS_PER_SECOND_DOCKER = 'cpu_events_per_second'

    # Experiment parameters
    PARAM_NUM_THREADS = 'num_threads'
    PARAM_MAX_TIME = 'max_time'
    PARAM_CPU_MAX_PRIME = 'cpu_max_prime'

    ORIGINAL_DOCKERFILE_DIR = os.path.join(WORKLOADS_DIR, 'sysbench')
    # Default Dockerfile provided by benchmark-tools (backed up to .Dockerfile)
    DEFAULT_DOCKERFILE_NAME = os.path.join(ORIGINAL_DOCKERFILE_DIR, '.Dockerfile')
    # Dockerfile we'll use with the parameters in INI file
    DOCKERFILE_NAME = os.path.join(ORIGINAL_DOCKERFILE_DIR, 'Dockerfile')

    def __init__(self, num_threads, max_time, cpu_max_prime, platform=Platform.NATIVE):
        super(SysbenchCPU, self).__init__(platform)
        # Parameters
        self.num_threads = num_threads
        self.max_time = max_time
        self.cpu_max_prime = cpu_max_prime

        self.csv_headers = ['num_threads', 'max_time', 'cpu_max_prime', 'events_per_second']
        self.csv_filename = 'sysbench_cpu.csv'

    def run_native(self):
        cmd = f"sysbench --threads={self.num_threads} --max-time={self.max_time} --cpu-max-prime={self.cpu_max_prime} cpu run"
        process = subprocess.run(shlex.split(cmd),
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)
        output_str = process.stdout
        return output_str.split('\n')

    def run_docker(self):
        # Copy the default Dockerfile into a list of strings
        with open(self.DEFAULT_DOCKERFILE_NAME, 'r') as f:
            lines = f.readlines()

        # Find the lines with ENV declarations
        env_linenos = []
        for lineno, line in enumerate(lines):
            if 'ENV' in line:
                env_linenos.append(lineno)

        # Sysbench-specific: find the last line
        last_line = len(lines) - 1

        # Remove these lines - assumes ENV lines are grouped together
        del lines[env_linenos[0] : env_linenos[-1] + 1]

        # Create ENV declaration strings
        env_decls = [f'ENV threads {self.num_threads}\n',
                     f'ENV max_time {self.max_time}\n',
                     f'ENV cpu_max_prime {self.cpu_max_prime}\n']

        # Insert the new ENV decalrations to lines
        lines[env_linenos[0] : env_linenos[0]] = env_decls

        # Handle sysbench-specific Dockerfile issues: replace ${options} with other parameters
        # This will be the last line in the Dockerflie
        cmd = 'sysbench --threads=${threads} --max-time=${max_time} --cpu-max-prime=${cpu_max_prime} cpu run"]"'
        lines[last_line] = cmd

        # Write to Dockerfile
        new_dockerfile = self.DOCKERFILE_NAME
        with open(new_dockerfile, 'w') as f:
            for line in lines:
                f.write(line)

        # Run perf.py script
        perf_cmd = f'python3 {BENCHMARK_TOOLS_DIR}/perf.py run --env {BENCHMARK_TOOLS_DIR}/examples/localhost.yaml sysbench.cpu'
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
            if self.EVENTS_PER_SECOND in line:
                print(f"[sysbench cpu] {line}")
                matches = re.findall(self.REGEX_FLOAT, line)
                # There should only be one floating point number
                events_per_second = float(matches[0])
                return events_per_second

    def _parse_docker_output(self, output):
        for line in output:
            if self.EVENTS_PER_SECOND_DOCKER in line:
                print(f'[sysbench cpu] {line}')
                events_per_second = float(line.split(',')[1])
                return events_per_second

    def write_to_csv(self, data):
        """Appends the given parameters and performance metric values to the csv file."""
        csv_row = {'num_threads': self.num_threads,
                   'max_time': self.max_time,
                   'cpu_max_prime': self.cpu_max_prime,
                   'events_per_second': data}

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
