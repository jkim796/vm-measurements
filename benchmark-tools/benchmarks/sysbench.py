# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Sysbench-based benchmarks."""

from benchmarks import benchmark
from harness.machine import Machine
from workloads.sysbench import cpu_events_per_second
from workloads.sysbench import memory_ops_per_second
from workloads.sysbench import mutex_time, mutex_deviation, mutex_latency


def sysbench(machine: Machine,
             test: str = "cpu",
             threads: int = 8,
             time: int = 5,
             options: str = "",
             **kwargs) -> str:
    """Run sysbench container with arguments.

    :param test: Relevant sysbench test to run (e.g. cpu, memory).
    :param threads: The number of threads to use for tests.
    :param time: The time to run tests.
    :param options: Additional sysbench options.
    :return: The output of the command as a string.
    """
    image = machine.pull("sysbench")
    return machine.container(image, **kwargs).run(
        test=test, threads=threads, time=time, options=options)


@benchmark(metrics=[cpu_events_per_second], machines=1)
def cpu(machine: Machine, max_prime: int = 5000, **kwargs) -> str:
    """Run sysbench CPU test. Additional arguments can be provided for sysbench.

    :param machine: A machine object.
    :param max_prime: The maximum prime number to search.
    :param kwargs:
        :param threads: The number of threads to use for tests.
        :param time: The time to run tests.
        :param options: Additional sysbench options. See sysbench tool:
        https://github.com/akopytov/sysbench
    """
    options = kwargs.pop("options", "")
    options += " --cpu-max-prime={}".format(max_prime)
    return sysbench(machine, test="cpu", options=options, **kwargs)


@benchmark(metrics=[memory_ops_per_second], machines=1)
def memory(machine: Machine, **kwargs) -> str:
    """Run sysbench memory test. Additional arguments can be provided per sysbench.

    :param machine: A machine object.
    :param kwargs:
        :param threads: The number of threads to use for tests.
        :param time: The time to run tests.
        :param options: Additional sysbench options. See sysbench tool:
        https://github.com/akopytov/sysbench
    """
    return sysbench(machine, test="memory", **kwargs)


@benchmark(metrics=[mutex_time, mutex_latency, mutex_deviation], machines=1)
def mutex(machine: Machine,
          locks: int = 4,
          count: int = 10000000,
          threads: int = 8,
          **kwargs) -> str:
    """Run sysbench mutex test. Additional arguments can be provided per sysbench.

    :param machine: A machine object.
    :param locks: The number of locks to use.
    :param count: The number of mutexes.
    :param kwargs:
        :param threads: The number of threads to use for tests.
        :param time: The time to run tests.
        :param options: Additional sysbench options. See sysbench tool:
        https://github.com/akopytov/sysbench
    """
    options = kwargs.pop("options", "")
    options += " --mutex-loops=1 --mutex-locks={} --mutex-num={}".format(count, locks)
    return sysbench(machine, test="mutex", options=options, threads=threads, **kwargs)
