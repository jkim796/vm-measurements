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
"""Redis benchmarks."""

from benchmarks import benchmark
from harness.machine import Machine
from workloads.redisbenchmark import METRICS


@benchmark(metrics=list(METRICS.values()), machines=2)
def redis(server: Machine, client: Machine, flags: str = "", **kwargs) -> str:
    """Run redis-benchmark on client pointing at server machine.

    :param server: A machine object.
    :param client: A machine object.
    :param flags: Flags to pass redis-benchmark.
    """
    redis_server = server.pull("redis")
    redis_client = client.pull("redisbenchmark")
    netcat = client.pull("netcat")
    with server.container(redis_server, port=6379, **kwargs).detach() as container:
        (host, port) = container.address()
        # Wait for the container to be up.
        client.container(netcat).run(host=host, port=port)
        # Run all redis benchmarks.
        return client.container(redis_client).run(host=host, port=port, flags=flags)
