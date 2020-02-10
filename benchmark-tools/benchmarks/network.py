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
"""Network microbenchmarks."""

from benchmarks import benchmark
from benchmarks.helpers import drop_caches
from harness.machine import Machine
from workloads.iperf import bandwidth


def iperf(client: Machine,
          server: Machine,
          client_kwargs: dict = None,
          server_kwargs: dict = None) -> str:
    """Measure iperf performance."""
    if not client_kwargs:
        client_kwargs = dict()
    if not server_kwargs:
        server_kwargs = dict()

    # Pull images.
    netcat = client.pull("netcat")
    iperf_client_image = client.pull("iperf")
    iperf_server_image = server.pull("iperf")

    # set this due to a bug in the kernel that resets connections for native and gvisor
    client.run("sudo /sbin/sysctl -w net.netfilter.nf_conntrack_tcp_be_liberal=1")
    server.run("sudo /sbin/sysctl -w net.netfilter.nf_conntrack_tcp_be_liberal=1")

    with server.container(iperf_server_image, port=5001, **server_kwargs).detach() as iperf_server:
        (host, port) = iperf_server.address()
        # Wait until the service is available.
        client.container(netcat).run(host=host, port=port)
        # Run a warm-up run.
        client.container(iperf_client_image, stderr=True, **client_kwargs).run(host=host, port=port)
        # Run the client with relevant arguments.
        res = client.container(iperf_client_image, stderr=True, **client_kwargs)\
            .run(host=host, port=port)
        drop_caches(client)
        return res


@benchmark(metrics=[bandwidth], machines=2)
def upload(client: Machine, server: Machine, **kwargs) -> str:
    """Measure upload performance.

    :param client: a machine object
    :param server: a machine object
    :param kwargs: passed to the client
    """
    if kwargs["runtime"] == "runc":
        kwargs["network_mode"] = "host"
    return iperf(client, server, client_kwargs=kwargs)


@benchmark(metrics=[bandwidth], machines=2)
def download(client: Machine, server: Machine, **kwargs) -> str:
    """Measure download performance.

    :param client: a machine object
    :param server: a machine object
    :param kwargs: passed to the server
    """

    client_kwargs = {"network_mode": "host"}
    return iperf(client, server, client_kwargs=client_kwargs, server_kwargs=kwargs)
