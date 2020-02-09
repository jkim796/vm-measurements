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
"""Parser test."""

import workloads.sysbench as sysbench

SAMPLE_CPU_DATA = """
sysbench 1.0.11 (using system LuaJIT 2.1.0-beta3)

Running the test with following options:
Number of threads: 8
Initializing random number generator from current time


Prime numbers limit: 10000

Initializing worker threads...

Threads started!

CPU speed:
    events per second:  9093.38

General statistics:
    total time:                          10.0007s
    total number of events:              90949

Latency (ms):
         min:                                  0.64
         avg:                                  0.88
         max:                                 24.65
         95th percentile:                      1.55
         sum:                              79936.91

Threads fairness:
    events (avg/stddev):           11368.6250/831.38
    execution time (avg/stddev):   9.9921/0.01
"""

SAMPLE_MEMORY_DATA = """
sysbench 1.0.11 (using system LuaJIT 2.1.0-beta3)

Running the test with following options:
Number of threads: 8
Initializing random number generator from current time


Running memory speed test with the following options:
  block size: 1KiB
  total size: 102400MiB
  operation: write
  scope: global

Initializing worker threads...

Threads started!

Total operations: 47999046 (9597428.64 per second)

46874.07 MiB transferred (9372.49 MiB/sec)


General statistics:
    total time:                          5.0001s
    total number of events:              47999046

Latency (ms):
         min:                                  0.00
         avg:                                  0.00
         max:                                  0.21
         95th percentile:                      0.00
         sum:                              33165.91

Threads fairness:
    events (avg/stddev):           5999880.7500/111242.52
    execution time (avg/stddev):   4.1457/0.09
"""


SAMPLE_MUTEX_DATA = """
sysbench 1.0.11 (using system LuaJIT 2.1.0-beta3)

Running the test with following options:
Number of threads: 8
Initializing random number generator from current time


Initializing worker threads...

Threads started!


General statistics:
    total time:                          3.7869s
    total number of events:              8

Latency (ms):
         min:                               3688.56
         avg:                               3754.03
         max:                               3780.94
         95th percentile:                   3773.42
         sum:                              30032.28

Threads fairness:
    events (avg/stddev):           1.0000/0.00
    execution time (avg/stddev):   3.7540/0.03
"""


def sample(test, **kwargs):
    switch = {
        "cpu": SAMPLE_CPU_DATA,
        "memory": SAMPLE_MEMORY_DATA,
        "mutex": SAMPLE_MUTEX_DATA,
        "randwr": SAMPLE_CPU_DATA
    }
    return switch[test]


def test_sysbench_parser():
    """Test the basic parser."""
    assert sysbench.cpu_events_per_second(SAMPLE_CPU_DATA) == 9093.38
    assert sysbench.memory_ops_per_second(SAMPLE_MEMORY_DATA) == 9597428.64
    assert sysbench.mutex_time(SAMPLE_MUTEX_DATA, 1, 1, 100000000.0) == 3.754
    assert sysbench.mutex_deviation(SAMPLE_MUTEX_DATA) == 0.03
    assert sysbench.mutex_latency(SAMPLE_MUTEX_DATA) == 3754.03
