from benchmark_parser import BenchmarkParser
from util import MultiDict
from sysbench_cpu import SysbenchCPU


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
