import csv
import os
import re
import shlex
import subprocess

from shutil import copyfile

from experiments import WORKLOADS_DIR, BENCHMARK_TOOLS_DIR, EXPERIMENTS_DIR
from benchmark import Benchmark, Platform


class MLTensorflow(Benchmark):
    # Benchmark name as used in INI file sections
    BENCH_NAME = 'ml_tensorflow'

    # Performance metric for native output
    NATIVE_METRIC = 'Inference time'
    REGEX_FLOAT = '\d+\.\d+'

    # Performance metric for Docker output
    DOCKER_METRIC = 'run_time'

    # Experiment parameters
    PARAM_NETWORK = 'network'

    ORIGINAL_DOCKERFILE_DIR = os.path.join(WORKLOADS_DIR, 'tensorflow')
    # Default Dockerfile provided by benchmark-tools (backed up to .Dockerfile)
    DEFAULT_DOCKERFILE_NAME = os.path.join(ORIGINAL_DOCKERFILE_DIR, '.Dockerfile')
    # Dockerfile we'll use with the parameters in INI file
    DOCKERFILE_NAME = os.path.join(ORIGINAL_DOCKERFILE_DIR, 'Dockerfile')

    TENSORFLOW_EXAMPLES_ROOT_DIR = os.path.join(EXPERIMENTS_DIR, 'TensorFlow-Examples')
    EXAMPLES_DIR = os.path.join(TENSORFLOW_EXAMPLES_ROOT_DIR, 'examples')
    CNN_WORKLOAD = os.path.join(EXAMPLES_DIR, '3_NeuralNetworks/convolutional_network.py')

    WORKLOAD = {'cnn': CNN_WORKLOAD}

    def __init__(self, network, platform=Platform.NATIVE):
        super(MLTensorflow, self).__init__(platform)
        # Parameters
        self.network = network

        self.csv_headers = ['network', 'runtime']
        self.csv_filename = 'ml_tensorflow.csv'

    def run_native(self):
        # If TensorFlow-Examples directory doesn't exist, we need to git clone
        if not os.path.isdir(self.TENSORFLOW_EXAMPLES_ROOT_DIR):
            # Call git clone
            git_cmd = f'git clone https://github.com/aymericdamien/TensorFlow-Examples.git'
            print(git_cmd)
            process = subprocess.run(shlex.split(git_cmd),
                                     stdout=subprocess.PIPE,
                                     universal_newlines=True)
        cmd = f'python3 {self.WORKLOAD[self.network]}'
        #cmd = f'python3 {self.WORKLOAD[self.network]} 2>/dev/null'
        print(f'[ml_tensorflow] {cmd}')
        process = subprocess.run(shlex.split(cmd),
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.DEVNULL,
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
        workload_cmd = f'3_NeuralNetworks/convolutional_network.py'
        cmd = f'CMD python {workload_cmd}'
        lines[-1] = cmd

        # Write to Dockerfile
        new_dockerfile = self.DOCKERFILE_NAME
        with open(new_dockerfile, 'w') as f:
            for line in lines:
                f.write(line)

        # Run perf.py script
        perf_cmd = f'python3 {BENCHMARK_TOOLS_DIR}/perf.py run --env {BENCHMARK_TOOLS_DIR}/examples/localhost.yaml ml.tensorflow'
        print(f'[ml_tensorflow] {perf_cmd}')
        process = subprocess.run(shlex.split(perf_cmd),
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.DEVNULL,
                                 universal_newlines=True)
        output_str = process.stdout
        return output_str.split('\n')

    def _parse_native_output(self, output):
        for line in output:
            if self.NATIVE_METRIC in line:
                inference_time = float(line.split(':')[1]) * 1000
                print(f'[ml_tensorflow] {inference_time} ms\n')
                return inference_time

    def _parse_docker_output(self, output):
        for line in output:
            if self.DOCKER_METRIC in line:
                inference_time = float(line.split(',')[1]) * 1000
                print(f'[ml_tensorflow] {inference_time} ms\n')
                return inference_time

    def write_to_csv(self, data):
        """Appends the given parameters and performance metric values to the csv file."""
        csv_row = {'network': self.network,
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
