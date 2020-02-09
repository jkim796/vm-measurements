# Copyright 2019 The gVisor Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""absl build benchmark."""

from benchmarks import benchmark
from harness.machine import Machine
from workloads.absl import elapsed_time

@benchmark(metrics=[elapsed_time], machines=1)
def absl(machine: Machine, **kwargs) -> str:
    """Runs the absl workload and report the absl build time.

    Runs the 'bazel build //absl/...' in a clean bazel directory and
    monitors time elapsed.

    :param machine: A machine object.
    """
    image = machine.pull("absl")
    return machine.container(image, **kwargs).run()
