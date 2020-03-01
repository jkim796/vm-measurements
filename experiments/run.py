import argparse
import subprocess
import shlex
import configparser
import re
import csv
import os

from enum import Enum
from typing import List

from util import MultiDict


class Platform(Enum):
    NATIVE = 1
    DOCKER = 2


class Benchmark(object):
    RESULTS_CSV_DIR = './results'

    def __init__(self, platform=Platform.NATIVE):
        self.platform = platform

    def run(self):
        pass

    def run_native(self):
        pass

    def run_docker(self):
        pass

    def parse_output(self, output):
        pass


class SysbenchCPU(Benchmark):
    EVENTS_PER_SECOND = 'events per second'
    REGEX_FLOAT = '\d+\.\d+'

    def __init__(self, num_threads, max_time, cpu_max_prime, platform=Platform.NATIVE):
        super(SysbenchCPU, self).__init__(platform)
        self.num_threads = num_threads
        self.max_time = max_time
        self.cpu_max_prime = cpu_max_prime
        self.csv_headers = ['num_threads', 'max_time', 'cpu_max_prime', 'events_per_second']
        self.csv_filename = 'sysbench_cpu.csv'

    def run(self):
        if self.platform == Platform.NATIVE:
            return self.run_native()
        elif self.platform == Platform.DOCKER:
            return self.run_docker()
        else:
            pass

    def run_native(self):
        cmd = f"sysbench --threads={self.num_threads} --max-time={self.max_time} --cpu-max-prime={self.cpu_max_prime} cpu run"
        process = subprocess.run(shlex.split(cmd),
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)
        output_str = process.stdout
        return output_str.split('\n')

    def run_docker(self):
        pass

    def parse_output(self, output):
        for line in output:
            if self.EVENTS_PER_SECOND in line:
                matches = re.findall(self.REGEX_FLOAT, line)
                # There should only be one floating point number
                events_per_second = float(matches[0])
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
        filepath = os.path.join(self.RESULTS_CSV_DIR, self.csv_filename)

        # Write CSV headers when creating file for first time
        if not os.path.isfile(filepath):
            with open(filepath, 'w') as csv_file:
                csv_writer = csv.DictWriter(csv_file, fieldnames=self.csv_headers)
                csv_writer.writeheader()

        # Append row to csv file
        with open(filepath, 'a') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=self.csv_headers)
            csv_writer.writerow(csv_row)


class BenchmarkParser(object):
    BENCHMARK = 'BENCHMARK'

    def __init__(self):
        self.config = configparser.ConfigParser(defaults=None, dict_type=MultiDict, strict=False)

    def parse_ini_file(self, filepath) -> List:
        self.config.read(filepath)
        bench_configs = []
        for section in self.config.sections():
            bench_config = {BenchmarkParser.BENCHMARK: section}
            for key, val in self.config.items(section):
                bench_config[key] = val
            bench_configs.append(bench_config)
        return bench_configs


class Dispatcher(object):
    MSG_DISPATCH_LOOKUP_NOT_FOUND = 'Key not found.'

    def __init__(self):
        self.dispatch_lookup = {'sysbench_cpu': self.dispatch_sysbench_cpu,
                                'sysbench_memory': self.dispatch_sysbench_memory}

    def dispatch_benchmarks(self, bench_configs):
        for bench_config in bench_configs:
            benchmark_name = self._strip_multidict_token(bench_config[BenchmarkParser.BENCHMARK])
            # Get the function
            bench_runner = self.dispatch_lookup.get(benchmark_name, self.MSG_DISPATCH_LOOKUP_NOT_FOUND)
            # Run benchmark
            bench_runner(bench_config)

    def dispatch_sysbench_cpu(self, bench_config):
        benchmark_name = self._strip_multidict_token(bench_config[BenchmarkParser.BENCHMARK])
        # Get the parameters
        num_threads = bench_config['num_threads']
        max_time = bench_config['max_time']
        cpu_max_prime = bench_config['cpu_max_prime']

        sysbench_cpu = SysbenchCPU(num_threads, max_time, cpu_max_prime)
        output = sysbench_cpu.run()
        data = sysbench_cpu.parse_output(output)
        sysbench_cpu.write_to_csv(data)

    def dispatch_sysbench_memory(self, bench_config):
        pass

    def _strip_multidict_token(self, name):
        """Strips away trailing token for multidict unique id."""
        return name[:name.rindex(MultiDict.TOKEN)]


def main(args):
    bench_parser = BenchmarkParser()
    bench_configs = bench_parser.parse_ini_file(args.benchmark_file)

    dispatcher = Dispatcher()
    dispatcher.dispatch_benchmarks(bench_configs)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Benchmark run script.')
    argparser.add_argument('-b', '--benchmark_file',
                           default='benchmarks.ini',
                           help='Benchmark config INI file. Default: benchmarks.ini')
    args = argparser.parse_args()

    main(args)
