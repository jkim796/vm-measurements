import argparse

from benchmark_parser import BenchmarkParser
from dispatcher import Dispatcher


def main(args):
    # Parse benchmark parameter config file (benchmarks.ini)
    bench_parser = BenchmarkParser()
    bench_configs = bench_parser.parse_ini_file(args.benchmark_file)

    # For each config, dispatch benchmark runner
    dispatcher = Dispatcher()
    dispatcher.dispatch_benchmarks(bench_configs)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Benchmark run script.')
    argparser.add_argument('-b', '--benchmark_file',
                           default='benchmarks.ini',
                           help='Benchmark config INI file. Default: benchmarks.ini')
    args = argparser.parse_args()

    main(args)
