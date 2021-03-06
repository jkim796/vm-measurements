import os

from enum import Enum


class Platform(Enum):
    NATIVE = 1
    DOCKER = 2


class Benchmark(object):
    EXPERIMENTS_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    RESULTS_CSV_DIR = os.path.join(EXPERIMENTS_ROOT_DIR, 'results')
    NATIVE_RESULTS_DIR = os.path.join(RESULTS_CSV_DIR, 'native')
    DOCKER_RESULTS_DIR = os.path.join(RESULTS_CSV_DIR, 'docker')

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
        if self.platform == Platform.NATIVE:
            return self._parse_native_output(output)
        elif self.platform == Platform.DOCKER:
            return self._parse_docker_output(output)

    def _parse_native_output(self, output):
        pass

    def _parse_docker_output(self, output):
        pass
