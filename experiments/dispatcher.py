from benchmark_parser import BenchmarkParser
from util import MultiDict
from sysbench_cpu import SysbenchCPU
from sysbench_memory import SysbenchMemory
from fio import Fio, FioSubBench
from syscall import Syscall
from ml_tensorflow import MLTensorflow

from benchmark import Platform


class Dispatcher(object):
    MSG_DISPATCH_LOOKUP_NOT_FOUND = 'Key not found.'

    def __init__(self, platform: str):
        # Platform Enum can convert given string (platform) to corresponding Enum
        self.platform = Platform[platform.upper()]
        self.dispatch_lookup = {SysbenchCPU.BENCH_NAME: self.dispatch_sysbench_cpu,
                                SysbenchMemory.BENCH_NAME: self.dispatch_sysbench_memory,
                                'fio_randread': self.dispatch_fio,
                                'fio_randwrite': self.dispatch_fio,
                                Syscall.BENCH_NAME: self.dispatch_syscall_syscall,
                                MLTensorflow.BENCH_NAME: self.dispatch_ml_tensorflow,
                                'media_ffmpeg': self.dispatch_media_ffmpeg}

    def dispatch_benchmarks(self, bench_configs):
        for bench_config in bench_configs:
            benchmark_name = self._strip_multidict_token(bench_config[BenchmarkParser.BENCHMARK])
            # Get the benchmark runner for given benchmark
            bench_runner = self.dispatch_lookup.get(benchmark_name, self.MSG_DISPATCH_LOOKUP_NOT_FOUND)
            # Run the benchmark
            if callable(bench_runner):
                bench_runner(bench_config)
            else:
                print(f'[Error] Unrecognized benchmark name: {benchmark_name}')
                print('Skipping this benchmark...')

    def dispatch_sysbench_cpu(self, bench_config):
        # Get the parameters
        num_threads = bench_config[SysbenchCPU.PARAM_NUM_THREADS]
        max_time = bench_config[SysbenchCPU.PARAM_MAX_TIME]
        cpu_max_prime = bench_config[SysbenchCPU.PARAM_CPU_MAX_PRIME]

        sysbench_cpu = SysbenchCPU(num_threads, max_time, cpu_max_prime, self.platform)
        output = sysbench_cpu.run()
        data = sysbench_cpu.parse_output(output)
        sysbench_cpu.write_to_csv(data)

    def dispatch_sysbench_memory(self, bench_config):
        # Get the parameters
        num_threads = bench_config[SysbenchMemory.PARAM_NUM_THREADS]
        memory_block_size = bench_config[SysbenchMemory.PARAM_MEMORY_BLOCK_SIZE]
        memory_total_size = bench_config[SysbenchMemory.PARAM_MEMORY_TOTAL_SIZE]
        memory_scope = bench_config[SysbenchMemory.PARAM_MEMORY_SCOPE]
        memory_hugetlb = bench_config[SysbenchMemory.PARAM_MEMORY_HUGETLB]
        memory_oper = bench_config[SysbenchMemory.PARAM_MEMORY_OPER]
        memory_access_mode = bench_config[SysbenchMemory.PARAM_MEMORY_ACCESS_MODE]

        sysbench_memory = SysbenchMemory(num_threads, memory_block_size, memory_total_size, memory_scope, memory_hugetlb, memory_oper, memory_access_mode, self.platform)
        output = sysbench_memory.run()
        data = sysbench_memory.parse_output(output)
        sysbench_memory.write_to_csv(data)

    def dispatch_fio(self, bench_config):
        # Get the parameters
        ramp_time = bench_config[Fio.PARAM_RUNTIME]
        ioengine = bench_config[Fio.PARAM_IOENGINE]
        #filename = bench_config[Fio.PARAM_FILENAME]
        bs = bench_config[Fio.PARAM_BS]
        rw = bench_config[Fio.PARAM_RW]
        nrfiles = bench_config[Fio.PARAM_NRFILES]
        filesize = bench_config[Fio.PARAM_FILESIZE]
        thread = bench_config[Fio.PARAM_THREAD]
        numjobs = bench_config[Fio.PARAM_NUMJOBS]
        time_based = bench_config[Fio.PARAM_TIME_BASED]
        runtime = bench_config[Fio.PARAM_RUNTIME]

        benchmark_name = self._strip_multidict_token(bench_config[BenchmarkParser.BENCHMARK])
        if benchmark_name == 'fio_randread':
            sub_bench = FioSubBench.RANDREAD
        elif benchmark_name == 'fio_randwrite':
            sub_bench = FioSubBench.RANDWRITE

        # Instantiate the corresponding benchmark runner
        fio = Fio(ramp_time, ioengine, bs, rw, nrfiles, filesize, thread, numjobs, time_based, runtime, sub_bench, self.platform)
        output = fio.run()
        data = fio.parse_output(output)
        fio.write_to_csv(data)

    def dispatch_syscall_syscall(self, bench_config):
        # Get the parameters
        count = bench_config[Syscall.PARAM_COUNT]

        syscall = Syscall(count, self.platform)
        output = syscall.run()
        data = syscall.parse_output(output)
        syscall.write_to_csv(data)

    def dispatch_ml_tensorflow(self, bench_config):
        # Get the parameters
        network = bench_config[MLTensorflow.PARAM_NETWORK]

        ml_tensorflow = MLTensorflow(network, self.platform)
        output = ml_tensorflow.run()
        data = ml_tensorflow.parse_output(output)
        ml_tensorflow.write_to_csv(data)

    def dispatch_media_ffmpeg(self, bench_config):
        # Get the parameters
        pass

    def _strip_multidict_token(self, name):
        """Strips away trailing token for multidict unique id."""
        return name[:name.rindex(MultiDict.TOKEN)]
