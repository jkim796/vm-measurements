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
"""Machine Learning tests."""

from benchmarks import benchmark
from benchmarks.startup import startup
from harness.machine import Machine
from workloads.tensorflow import run_time


@benchmark(metrics=[run_time], machines=1)
def tensorflow(machine: Machine, **kwargs):
    """Run the tensorflow benchmark and return the runtime in seconds of workload.

    :param machine: a machine object.
    """
    return startup(machine, workload="tensorflow", count=1, **kwargs)
