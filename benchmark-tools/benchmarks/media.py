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
"""Media processing benchmarks."""

from benchmarks import benchmark
import benchmarks.helpers as helpers
from harness.machine import Machine
from workloads.ffmpeg import run_time


@benchmark(metrics=[run_time], machines=1)
def ffmpeg(machine: Machine, **kwargs) -> float:
    """Runs a video transcoding workload and times it.

    :param machine: a machine object.
    """
    # Load before timing.
    image = machine.pull("ffmpeg")

    # Drop caches.
    helpers.drop_caches(machine)

    # Time startup + transcoding.
    with helpers.Timer() as timer:
        machine.container(image, **kwargs).run()
        return timer.elapsed()
