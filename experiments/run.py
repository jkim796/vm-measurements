import argparse
import subprocess
import shlex
import configparser

from enum import Enum
from typing import List

from util import MultiDict


class Platform(Enum):
    NATIVE = 1
    DOCKER = 2


class Benchmark(object):
    pass


class SysbenchCPU(Benchmark):

    def __init__(self, num_threads, max_time, cpu_max_prime, platform=Platform.NATIVE):
        self.num_threads = num_threads
        self.max_time = max_time
        self.cpu_max_prime = cpu_max_prime
        self.platform = platform

    def run(self):
        if self.platform == Platform.NATIVE:
            self.run_native()
        elif self.platform == Platform.DOCKER:
            self.run_docker()
        else:
            pass

    def run_native(self):
        cmd = f"sysbench --threads={self.num_threads} --max-time={self.max_time} --cpu-max-prime={self.cpu_max_prime} cpu run"
        process = subprocess.run(shlex.split(cmd),
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)
        print(process.stdout)

    def run_docker(self):
        pass


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
        # Get the class
        benchmark_name = self._strip_multidict_token(bench_config[BenchmarkParser.BENCHMARK])

        # Get the parameters
        num_threads = bench_config['num_threads']
        max_time = bench_config['max_time']
        cpu_max_prime = bench_config['cpu_max_prime']
        sysbench_cpu = SysbenchCPU(num_threads, max_time, cpu_max_prime)
        sysbench_cpu.run()

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
