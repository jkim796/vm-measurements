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
"""Sysbench."""

import re


STD_REGEX = r"events per second:\s*(\d*.?\d*)\n"
MEM_REGEX = r"Total\soperations:\s+\d*\s*\((\d*\.\d*)\sper\ssecond\)"
ALT_REGEX = r"execution time \(avg/stddev\):\s*(\d*.?\d*)/(\d*.?\d*)"
AVG_REGEX = r"avg:[^\n^\d]*(\d*\.?\d*)"


def cpu_events_per_second(data: str, **kwargs) -> float:
    """Returns events per second."""
    return float(re.compile(STD_REGEX).search(data).group(1))


def memory_ops_per_second(data: str, **kwargs) -> float:
    """Returns memory operations per second."""
    return float(re.compile(MEM_REGEX).search(data).group(1))


def mutex_time(data: str, count: int, locks: int, threads: int, **kwargs) -> float:
    """Returns normalized mutex time (lower is better)."""
    value = float(re.compile(ALT_REGEX).search(data).group(1))
    contention = float(threads)/float(locks)
    scale = contention*float(count)/100000000.0
    return value/scale


def mutex_deviation(data: str, **kwargs) -> float:
    """Returns deviation for threads."""
    return float(re.compile(ALT_REGEX).search(data).group(2))


def mutex_latency(data: str, **kwargs) -> float:
    """Returns average mutex latency."""
    return float(re.compile(AVG_REGEX).search(data).group(1))
