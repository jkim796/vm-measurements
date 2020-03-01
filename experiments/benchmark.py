import os

from enum import Enum


class Platform(Enum):
    NATIVE = 1
    DOCKER = 2


class Benchmark(object):
    EXPERIMENTS_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    RESULTS_CSV_DIR = os.path.join(EXPERIMENTS_ROOT_DIR, 'results')

    def __init__(self, platform=Platform.NATIVE):
        self.platform = platform

    def run(self):
        if self.platform == Platform.NATIVE:
            return self.run_native()
        elif self.platform == Platform.DOCKER:
            return self.run_docker()
        else:
            pass

    def run_native(self):
        pass

    def run_docker(self):
        pass

    def parse_output(self, output):
        pass
