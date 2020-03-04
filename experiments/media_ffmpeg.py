import csv
import os
import re
import shlex
import subprocess

from shutil import copyfile

from experiments import WORKLOADS_DIR, BENCHMARK_TOOLS_DIR, EXPERIMENTS_DIR
from benchmark import Benchmark, Platform


class MediaFFMPEG(Benchmark):
    # Benchmark name as used in INI file sections
    BENCH_NAME = 'media_ffmpeg'

    # Performance metric for native output
    NATIVE_METRIC = 'elapsed'
    REGEX_FLOAT = '\d+\.\d+'

    # Performance metric for Docker output
    DOCKER_METRIC = 'run_time'

    # Experiment parameters
    PARAM_INPUT_FILE = 'input_file'

    ORIGINAL_DOCKERFILE_DIR = os.path.join(WORKLOADS_DIR, 'ffmpeg')
    # Default Dockerfile provided by benchmark-tools (backed up to .Dockerfile)
    DEFAULT_DOCKERFILE_NAME = os.path.join(ORIGINAL_DOCKERFILE_DIR, '.Dockerfile')
    # Dockerfile we'll use with the parameters in INI file
    DOCKERFILE_NAME = os.path.join(ORIGINAL_DOCKERFILE_DIR, 'Dockerfile')

    def __init__(self, input_file, platform=Platform.NATIVE):
        super(MediaFFMPEG, self).__init__(platform)
        # Parameters
        self.input_file = input_file

        self.csv_headers = ['input_file', 'runtime']
        self.csv_filename = 'media_ffmpeg.csv'

    def run_native(self):
        if not os.path.isfile(self.input_file):
            wget_cmd = f'wget https://samples.ffmpeg.org/MPEG-4/video.mp4 {self.input_file}'
            print(wget_cmd)
            process = subprocess.run(shlex.split(wget_cmd),
                                     stdout=subprocess.PIPE,
                                     universal_newlines=True)
        cmd = f'sudo time ffmpeg -i {self.input_file} -c:v libx264 -preset veryslow output.mp4 -y'
        print(f'[media_ffmpeg] {cmd}')
        process = subprocess.run(shlex.split(cmd),
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True)
        output_str = process.stderr
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
                print(line)
                start = line.index('system') + len('system')
                end = line.index('elapsed')
                time_str = line[start : end]
                minutes = int(time_str.split(':')[0])
                seconds = float(time_str.split(':')[1])
                time = minutes * 60 + seconds
                print(f'[media_ffmpeg] {time} s (time_str)\n')
                return time

    def _parse_docker_output(self, output):
        for line in output:
            if self.DOCKER_METRIC in line:
                time = float(line.split(',')[1]) * 1000
                print(f'[media_ffmpeg] {time} ms\n')
                return time

    def write_to_csv(self, data):
        """Appends the given parameters and performance metric values to the csv file."""
        csv_row = {'input_file': self.input_file,
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
