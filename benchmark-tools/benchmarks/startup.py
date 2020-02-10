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
"""Start-up benchmarks."""

from benchmarks import benchmark
import benchmarks.helpers as helpers
from harness.machine import Machine


#pylint: disable-msg=unused-argument
def startup_time_ms(value, **kwargs):
    """Returns average startup time per container in milliseconds."""
    return value * 1000


def startup(machine: Machine, workload: str, count: int = 5, port: int = 0, **kwargs):
    """Time the startup of some workload.

    :param count: Number of containers to start.
    :param port: The port to check for liveness, if provided.
    :param workload: The workload to run.
    :return: The mean start-up time in seconds.
    """
    # Load before timing.
    image = machine.pull(workload)
    netcat = machine.pull("netcat")
    count = int(count)
    port = int(port)

    with helpers.Timer() as timer:
        for _ in range(count):
            if not port:
                # Run the container synchronously.
                machine.container(image, **kwargs).run()
            else:
                # Run a detached container until httpd available.
                with machine.container(image, port=port, **kwargs).detach() as server:
                    (server_host, server_port) = server.address()
                    machine.container(netcat).run(host=server_host, port=server_port)
        return timer.elapsed() / float(count)


@benchmark(metrics=[startup_time_ms], machines=1)
def empty(machine: Machine, **kwargs) -> float:
    """Time the startup of a trivial container.

    :param machine: machine object
    :param kwargs:
        :param count: Number of containers to start.
    """
    return startup(machine, workload="true", **kwargs)


@benchmark(metrics=[startup_time_ms], machines=1)
def node(machine: Machine, **kwargs) -> float:
    """Time the startup of the node container.

    :param machine: machine object
    :param kwargs:
        :param count: Number of containers to start.
    """
    return startup(machine, workload="node", port=8080, **kwargs)


@benchmark(metrics=[startup_time_ms], machines=1)
def ruby(machine: Machine, **kwargs) -> float:
    """Time the startup of the ruby container.

    :param machine: machine object
    :param kwargs:
        :param count: The number of times to measure.
    """
    return startup(machine, workload="ruby", port=3000, **kwargs)
