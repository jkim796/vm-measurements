import configparser

from typing import List

from util import MultiDict


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
