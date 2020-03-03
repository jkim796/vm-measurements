# Ideally we want to set PYTHONPATH, but let's not mess with the machine env variables
import sys
sys.path.append('/home/ubuntu/vm-measurements')

import argparse

from benchmark_parser import BenchmarkParser
from dispatcher import Dispatcher


def main(args):
    # Parse benchmark parameter config file (benchmarks.ini)
    bench_parser = BenchmarkParser()
    bench_configs = bench_parser.parse_ini_file(args.benchmark_file)

    print(f'Running on {args.platform}...\n')

    # For each config, dispatch benchmark runner
    dispatcher = Dispatcher(args.platform)
    dispatcher.dispatch_benchmarks(bench_configs)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Benchmark run script.')
    argparser.add_argument('-b', '--benchmark_file',
                           default='benchmarks.ini',
                           help='Benchmark config INI file. Default: benchmarks.ini')
    argparser.add_argument('-p', '--platform',
                           default='native',
                           help='Platform to run benchmarks on (either native or docker). Default: native')
    args = argparser.parse_args()

    main(args)
