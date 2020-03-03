import os


ROOT_DIR = os.path.dirname(os.path.abspath(__file__)).rsplit('/', 1)[0]
BENCHMARK_TOOLS_DIR = os.path.join(ROOT_DIR, 'benchmark-tools')
WORKLOADS_DIR = os.path.join(BENCHMARK_TOOLS_DIR, 'workloads')
EXPERIMENTS_DIR = os.path.join(ROOT_DIR, 'experiments')
