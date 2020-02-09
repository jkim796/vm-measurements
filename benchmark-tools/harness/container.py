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
"""Container definitions."""

import contextlib
import types
import logging
import pydoc
import docker
import docker.errors


class Container:
    """Abstract container. Must be a context manager. Usage:

    with Container(client, image, ...):
        ...
    """
    def run(self, **env):
        """Run the container synchronously."""
        raise NotImplementedError

    def detach(self, **env):
        """Run the container asynchronously."""
        raise NotImplementedError

    def address(self) -> (str, int):
        """Return the bound address for the container."""
        raise NotImplementedError

    def get_names(self) -> types.GeneratorType:
        """Return names of all containers."""
        raise NotImplementedError


#pylint: disable-msg=too-many-instance-attributes
class DockerContainer(Container):
    """Class that handles creating a docker container."""

    #pylint: disable-msg=too-many-arguments
    def __init__(self,
                 client: docker.DockerClient,
                 host: str,
                 image: str,
                 count: int = 1,
                 runtime: str = "runc",
                 port: int = 0,
                 **kwargs):
        """Trys to setup "count" containers.

        :param client: A docker client from docker py lib (machine.docker_client).
        :param host: the host address the image is running on.
        :param image: name of the image to run.
        :param count: number of containers to setup.
        :param runtime: the container runtime to use.
        :param port: the port to reserve.
        :param env: all environment variables.
        """
        assert count >= 1
        assert port == 0 or count == 1
        self._client = client
        self._host = host
        self._containers = []
        self._count = count
        self._image = image
        self._runtime = runtime
        self._port = port
        self._kwargs = kwargs
        if port != 0:
            self._ports = {'%d/tcp' % port: None}
        else:
            self._ports = {}

    @contextlib.contextmanager
    def detach(self, **env):
        env = ["%s=%s" % (key, value) for (key, value) in env.items()]
        # Start all containers.
        for _ in range(self._count):
            try:
                # Start the container in a detached mode.
                container = self._client.containers.run(self._image,
                                                        detach=True,
                                                        remove=True,
                                                        runtime=self._runtime,
                                                        ports=self._ports,
                                                        environment=env,
                                                        **self._kwargs)
                logging.info("Started detached container %s -> %s",
                             self._image, container.attrs["Id"])
                self._containers.append(container)
            except Exception as exc:
                self._clean_containers()
                raise exc
        try:
            # Wait for all containers to be up.
            for container in self._containers:
                while not container.attrs["State"]["Running"]:
                    container = self._client.containers.get(container.attrs["Id"])
            yield self
        finally:
            self._clean_containers()

    def address(self) -> (str, int):
        assert self._count == 1
        assert self._port != 0
        container = self._client.containers.get(self._containers[0].attrs["Id"])
        port = container.attrs["NetworkSettings"]["Ports"]["%d/tcp" % self._port][0]["HostPort"]
        return (self._host, port)

    def get_names(self) -> types.GeneratorType:
        for container in self._containers:
            yield container.name

    def run(self, **env):
        env = ["%s=%s" % (key, value) for (key, value) in env.items()]
        return self._client.containers.run(self._image,
                                           runtime=self._runtime,
                                           ports=self._ports,
                                           remove=True,
                                           environment=env,
                                           **self._kwargs).decode("utf-8")

    def _clean_containers(self):
        """Kills all containers."""
        for container in self._containers:
            try:
                container.kill()
            except docker.errors.NotFound:
                pass


class MockContainer(Container):
    """Mock of Container."""

    def __init__(self, workload: str):
        self._workload = workload

    def __enter__(self):
        return self

    def run(self, **env):
        # Lookup sample data if any exists for the workload module. We use
        # a well-defined test locate and a well-defined sample function.
        mod = pydoc.locate("workloads.%s.%s_test" % (self._workload, self._workload))
        if hasattr(mod, 'sample'):
            return mod.sample(**env)
        return "" # No output.

    def address(self) -> (str, int):
        return ("example.com", 80)

    def get_names(self) -> types.GeneratorType:
        yield "mock"

    @contextlib.contextmanager
    def detach(self, **env):
        yield self
